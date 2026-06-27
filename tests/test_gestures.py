"""Testes das funcoes puras de classificacao de gesto (gestures.py).

Diferente de test_hands.py (que valida o wrapper ``Hands.Map_*`` e seu contrato
legado True/None), aqui exercitamos as funcoes puras diretamente: recebem
``(h, w, hand_landmarks)`` e retornam ``bool`` limpo (True/False).

Reaproveita os fixtures canonicos de gesto do conftest (``GESTURE_*``), ja
verificados contra a geometria do reconhecedor.
"""

import conftest
import pytest
from conftest import make_hand_landmarks

from jarvis.vision import gestures

# Nome -> (funcao pura, coordenadas canonicas que devem dispara-la).
FUNC_BY_GESTURE = {
    "is_ok": (gestures.is_ok, conftest.GESTURE_OK),
    "is_positive": (gestures.is_positive, conftest.GESTURE_POSITIVE),
    "is_speak": (gestures.is_speak, conftest.GESTURE_SPEAK),
    "is_squid": (gestures.is_squid, conftest.GESTURE_SQUID),
    "is_rock": (gestures.is_rock, conftest.GESTURE_ROCK),
}
ALL_FUNCS = [fn for fn, _ in FUNC_BY_GESTURE.values()]


def _call(fn, coords, h=1000, w=1000):
    """Monta landmarks a partir de ``coords`` e chama a funcao pura."""
    return fn(h, w, make_hand_landmarks(coords))


# ---------------------------------------------------------------------------
# 1. Cada gesto canonico dispara a sua propria funcao
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", list(FUNC_BY_GESTURE))
def test_gesto_canonico_dispara_sua_funcao(name):
    """As coordenadas de referencia de cada gesto fazem a sua funcao retornar True."""
    fn, coords = FUNC_BY_GESTURE[name]
    assert _call(fn, coords) is True


# ---------------------------------------------------------------------------
# 2. Exclusividade: cada gesto canonico dispara SO a sua funcao
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("gesture_name", list(FUNC_BY_GESTURE))
@pytest.mark.parametrize("func_name", list(FUNC_BY_GESTURE))
def test_exclusividade_gesto_dispara_apenas_sua_funcao(func_name, gesture_name):
    """Produto cartesiano 5x5: True so na diagonal, False fora dela."""
    fn = FUNC_BY_GESTURE[func_name][0]
    coords = FUNC_BY_GESTURE[gesture_name][1]
    assert _call(fn, coords) is (func_name == gesture_name)


# ---------------------------------------------------------------------------
# 3. Nao-gesto: pose neutra e landmarks degenerados -> todas False
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fn", ALL_FUNCS)
def test_pose_neutra_nao_dispara(fn):
    """A pose neutra (mao aberta) nao pode casar com nenhum gesto."""
    assert _call(fn, conftest.GESTURE_NONE) is False


@pytest.mark.parametrize("fn", ALL_FUNCS)
def test_landmarks_default_nao_dispara(fn):
    """Todos os pontos colapsados em (0.5, 0.5): nenhuma desigualdade se sustenta."""
    assert fn(1000, 1000, make_hand_landmarks()) is False


# ---------------------------------------------------------------------------
# 4. Contrato: o retorno e sempre bool (nunca None, ao contrario do wrapper)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", list(FUNC_BY_GESTURE))
def test_retorno_e_sempre_bool(name):
    """Tanto no caso positivo quanto no negativo, o tipo de retorno e bool."""
    fn, coords = FUNC_BY_GESTURE[name]
    assert isinstance(_call(fn, coords), bool)
    assert isinstance(_call(fn, conftest.GESTURE_NONE), bool)


# ---------------------------------------------------------------------------
# 5. distance: euclidiana pura
# ---------------------------------------------------------------------------


class TestDistance:
    """Distancia euclidiana entre dois pontos (x, y)."""

    @pytest.mark.parametrize(
        "p1,p2,esperado",
        [
            ((0, 0), (3, 4), 5.0),  # triangulo 3-4-5 classico
            ((0, 0), (0, 0), 0.0),  # ponto consigo mesmo
            ((1, 2), (4, 6), 5.0),  # dx=3, dy=4
            ((-3, 0), (0, 4), 5.0),  # coordenadas negativas
        ],
    )
    def test_valores_conhecidos(self, p1, p2, esperado):
        assert gestures.distance(p1, p2) == pytest.approx(esperado)

    def test_e_simetrica(self):
        """d(p1, p2) == d(p2, p1)."""
        assert gestures.distance((2, 9), (11, 3)) == pytest.approx(
            gestures.distance((11, 3), (2, 9))
        )
