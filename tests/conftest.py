"""Infra compartilhada dos testes do Jarvis.

Estrategia: **mock total**. As libs pesadas (mediapipe, cv2, pygame,
speech_recognition, google-generativeai, edge-tts, google-auth*) NAO precisam
estar instaladas para rodar os testes. Este conftest injeta stubs em
``sys.modules`` ANTES de qualquer ``import`` do pacote ``jarvis.*`` (vision/core/
services), de modo que o codigo de producao importa os stubs em vez das libs reais.

Por que aqui: o pytest importa o ``conftest.py`` da pasta de testes antes dos
modulos ``test_*.py``. Como os modulos de producao so sao importados dentro dos
testes, os stubs ja estarao em ``sys.modules`` no momento do import.

So mockamos o que NAO esta instalado ou faz I/O real. ``requests`` e
``python-dotenv`` estao instalados e sao reais; os testes que precisam mockam
pontualmente (monkeypatch) o comportamento de rede.
"""

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# 1. Stubs de modulos de terceiros (injetados no import deste conftest)
# ---------------------------------------------------------------------------


def _ensure_pkg(dotted: str) -> ModuleType:
    """Garante que ``dotted`` e todos os seus pais existam em ``sys.modules``.

    Usa MagicMock como corpo do modulo: qualquer atributo acessado vira um mock
    filho automaticamente. Retorna o modulo folha.
    """
    parts = dotted.split(".")
    for i in range(1, len(parts) + 1):
        name = ".".join(parts[:i])
        if name not in sys.modules:
            sys.modules[name] = MagicMock(name=name)
    return sys.modules[dotted]


def _install_stubs() -> None:
    # mediapipe: hands.py faz `import mediapipe as mp` e
    # `from mediapipe.tasks import python`. As poses (Map_*) so usam geometria
    # dos landmarks, entao um MagicMock basta para o __init__ nao quebrar.
    _ensure_pkg("mediapipe")
    _ensure_pkg("mediapipe.tasks")
    _ensure_pkg("mediapipe.tasks.python")

    # cv2: control.py/main.py usam imwrite, VideoWriter, cvtColor, etc.
    _ensure_pkg("cv2")

    # pygame + pygame.mixer: control.py faz `from pygame import mixer`.
    _ensure_pkg("pygame")

    # edge_tts: jarvis.py usa edge_tts.Communicate(...).save(...)
    _ensure_pkg("edge_tts")

    # google-generativeai (genai) + pacote google
    _ensure_pkg("google")
    _ensure_pkg("google.generativeai")

    # google-auth* usados por manager.py
    _ensure_pkg("google.oauth2")
    _ensure_pkg("google.oauth2.credentials")
    _ensure_pkg("google.auth")
    _ensure_pkg("google.auth.transport")
    _ensure_pkg("google.auth.transport.requests")
    _ensure_pkg("google_auth_oauthlib")
    _ensure_pkg("google_auth_oauthlib.flow")

    # speech_recognition precisa de tratamento especial: control.py captura
    # `except sr.UnknownValueError`/`sr.RequestError`, que TEM que ser classes
    # de excecao reais (um MagicMock quebraria o `except`).
    if "speech_recognition" not in sys.modules:
        sr_mod = ModuleType("speech_recognition")

        class UnknownValueError(Exception):
            pass

        class RequestError(Exception):
            pass

        sr_mod.Recognizer = MagicMock(name="speech_recognition.Recognizer")
        sr_mod.Microphone = MagicMock(name="speech_recognition.Microphone")
        sr_mod.UnknownValueError = UnknownValueError
        sr_mod.RequestError = RequestError
        sys.modules["speech_recognition"] = sr_mod


_install_stubs()


# ---------------------------------------------------------------------------
# 2. Construtor de landmarks falsos (MediaPipe Hands tem 21 pontos)
# ---------------------------------------------------------------------------


class _FakeLandmark:
    """Imita ``mp.solutions.hands`` landmark: tem .x, .y, .z normalizados [0,1]."""

    __slots__ = ("x", "y", "z")

    def __init__(self, x: float, y: float, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z


class _FakeHandLandmarks:
    """Imita o objeto ``hand_landmarks`` (atributo ``.landmark`` indexavel 0..20)."""

    __slots__ = ("landmark",)

    def __init__(self, landmark):
        self.landmark = landmark


# Indice -> nome legivel (referencia MediaPipe Hands), so para documentar fixtures.
WRIST = 0
THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20


def make_hand_landmarks(coords=None, default=(0.5, 0.5)):
    """Cria um objeto de landmarks com 21 pontos.

    Args:
        coords: dict {indice: (x_norm, y_norm)} sobrescrevendo pontos especificos.
            Coordenadas sao normalizadas [0,1] (como o MediaPipe devolve).
        default: (x,y) usado para todo indice nao informado.

    Returns:
        Objeto com ``.landmark`` = lista de 21 _FakeLandmark.
    """
    coords = coords or {}
    dx, dy = default
    pts = []
    for i in range(21):
        if i in coords:
            x, y = coords[i]
        else:
            x, y = dx, dy
        pts.append(_FakeLandmark(float(x), float(y)))
    return _FakeHandLandmarks(pts)


# ---------------------------------------------------------------------------
# 3. Coordenadas canonicas de cada gesto (VERIFICADAS contra hands.py)
# ---------------------------------------------------------------------------
# Convencao de tela nos testes: w = h = 1000 (use a fixture `frame_size`).
# Sistema de imagem: x cresce para a direita, y cresce para BAIXO
# (portanto "dedo levantado" => y do tip MENOR que o da base).
#
# Cada dict abaixo dispara EXATAMENTE o seu Map_* (exclusividade verificada no
# script tests/_verify_gestures.py e no test_hands.py).

GESTURE_OK = {
    # Polegar e indicador se tocam (circulo do "OK"), demais dedos pra baixo.
    THUMB_CMC: (0.55, 0.65),
    THUMB_IP: (0.55, 0.50),
    THUMB_TIP: (0.45, 0.46),
    INDEX_MCP: (0.50, 0.60),
    INDEX_PIP: (0.50, 0.50),
    INDEX_TIP: (0.45, 0.45),
}

GESTURE_POSITIVE = {
    # Joinha: polegar levantado, demais dedos dobrados.
    THUMB_CMC: (0.50, 0.40),
    THUMB_TIP: (0.50, 0.20),
    INDEX_MCP: (0.50, 0.50),
    INDEX_TIP: (0.50, 0.60),
    MIDDLE_MCP: (0.50, 0.50),
    MIDDLE_TIP: (0.50, 0.62),
    RING_MCP: (0.50, 0.50),
    RING_TIP: (0.50, 0.62),
    PINKY_MCP: (0.50, 0.50),
    PINKY_TIP: (0.50, 0.62),
}

GESTURE_SPEAK = {
    # Indicador levantado, polegar pro lado (x maior que a base), demais dobrados.
    THUMB_CMC: (0.50, 0.50),
    THUMB_TIP: (0.60, 0.50),
    INDEX_MCP: (0.50, 0.40),
    INDEX_TIP: (0.50, 0.20),
    MIDDLE_MCP: (0.50, 0.50),
    MIDDLE_TIP: (0.50, 0.62),
    RING_MCP: (0.50, 0.50),
    RING_TIP: (0.50, 0.62),
    PINKY_MCP: (0.50, 0.50),
    PINKY_TIP: (0.50, 0.62),
}

GESTURE_SQUID = {
    # "L": indicador levantado + polegar aberto para a esquerda, demais dobrados.
    THUMB_MCP: (0.40, 0.50),
    THUMB_TIP: (0.20, 0.50),
    INDEX_PIP: (0.40, 0.40),
    INDEX_TIP: (0.40, 0.20),
    MIDDLE_MCP: (0.50, 0.50),
    MIDDLE_TIP: (0.50, 0.62),
    RING_MCP: (0.50, 0.50),
    RING_TIP: (0.50, 0.62),
    PINKY_MCP: (0.50, 0.50),
    PINKY_TIP: (0.50, 0.62),
}

GESTURE_ROCK = {
    # Rock: indicador + mindinho levantados, medio e anelar dobrados.
    INDEX_PIP: (0.30, 0.40),
    INDEX_TIP: (0.30, 0.20),
    MIDDLE_MCP: (0.50, 0.50),
    MIDDLE_TIP: (0.50, 0.62),
    RING_MCP: (0.50, 0.50),
    RING_TIP: (0.50, 0.62),
    PINKY_PIP: (0.70, 0.40),
    PINKY_TIP: (0.70, 0.20),
}

# Pose neutra (mao aberta, todos os dedos esticados pra cima) -> nao dispara nada.
GESTURE_NONE = {
    WRIST: (0.50, 0.90),
    THUMB_CMC: (0.35, 0.80),
    THUMB_MCP: (0.30, 0.72),
    THUMB_IP: (0.27, 0.66),
    THUMB_TIP: (0.24, 0.60),
    INDEX_MCP: (0.45, 0.60),
    INDEX_PIP: (0.45, 0.45),
    INDEX_TIP: (0.45, 0.30),
    MIDDLE_MCP: (0.52, 0.60),
    MIDDLE_PIP: (0.52, 0.44),
    MIDDLE_TIP: (0.52, 0.28),
    RING_MCP: (0.59, 0.60),
    RING_PIP: (0.59, 0.46),
    RING_TIP: (0.59, 0.32),
    PINKY_MCP: (0.66, 0.62),
    PINKY_PIP: (0.66, 0.50),
    PINKY_TIP: (0.66, 0.38),
}

ALL_GESTURES = {
    "map_ok": GESTURE_OK,
    "map_positive": GESTURE_POSITIVE,
    "map_speak": GESTURE_SPEAK,
    "map_squid": GESTURE_SQUID,
    "map_rock": GESTURE_ROCK,
}


# ---------------------------------------------------------------------------
# 4. Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def frame_size():
    """(h, w) padrao usado nos testes de geometria."""
    return 1000, 1000


@pytest.fixture
def fake_frame():
    """Placeholder de frame de camera (so precisa ser um objeto qualquer)."""
    return MagicMock(name="frame")


@pytest.fixture
def landmarks_factory():
    """Expoe o construtor ``make_hand_landmarks`` como fixture."""
    return make_hand_landmarks


@pytest.fixture
def hands_instance():
    """Instancia real de ``hands.Hands`` (com mediapipe stubado)."""
    from jarvis.vision import hands

    return hands.Hands()
