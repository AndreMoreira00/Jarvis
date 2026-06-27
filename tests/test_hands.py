"""Testes da logica de geometria pura de ``hands.Hands`` (hands.py).

Foco: o NOSSO codigo de reconhecimento de gesto (geometria dos 21 landmarks do
MediaPipe), sem nenhum I/O. O MediaPipe e stubado pelo conftest, entao
``Hands()`` instancia sem libs reais.

Convencao de tela (igual ao conftest): coordenadas dos landmarks sao
normalizadas em [0,1]; o codigo converte para pixel via ``int(norm * w|h)``.
Usamos h = w = 1000 quando precisamos raciocinar em pixels (norm * 1000 = px),
de modo que um threshold de ``0.05 * w`` vale 50 px.

Detalhe de contrato importante: cada ``Map_*`` retorna ``True`` quando a pose
casa e cai num ``return`` implicito (``None``) caso contrario. Por isso os
testes de "nao dispara" checam valor *falsy* (``None``), nao ``False``.
"""

import math

import conftest
import pytest
from conftest import (
    INDEX_MCP,
    INDEX_PIP,
    INDEX_TIP,
    PINKY_PIP,
    PINKY_TIP,
    THUMB_CMC,
    THUMB_TIP,
    make_hand_landmarks,
)

# Lista dos metodos de reconhecimento, usada nas matrizes de exclusividade.
MAP_NAMES = list(conftest.ALL_GESTURES.keys())


# ---------------------------------------------------------------------------
# Helpers locais
# ---------------------------------------------------------------------------


def _call(hands_instance, map_name, coords, h=1000, w=1000):
    """Atalho: monta landmarks a partir de ``coords`` e chama ``map_name``."""
    lm = make_hand_landmarks(coords)
    return getattr(hands_instance, map_name)(h, w, lm, None)


# ---------------------------------------------------------------------------
# 1. Cada gesto canonico dispara o seu Map_*
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("map_name,coords", list(conftest.ALL_GESTURES.items()))
def test_gesto_canonico_dispara_seu_map(hands_instance, map_name, coords):
    """Cada fixture canonica de gesto deve fazer o seu proprio Map_* retornar True.

    Garante que as condicoes geometricas que definem cada pose estao satisfeitas
    pelas coordenadas de referencia do conftest.
    """
    assert _call(hands_instance, map_name, coords) is True


# ---------------------------------------------------------------------------
# 2. Nao-gesto: pose neutra e default nao disparam nenhum Map_*
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("map_name", MAP_NAMES)
def test_mao_aberta_nao_dispara_nenhum_map(hands_instance, map_name):
    """A pose neutra (mao aberta, GESTURE_NONE) nao pode casar com nenhum gesto.

    E o cenario mais comum em runtime (mao parada na frente da camera); um falso
    positivo aqui dispararia acoes indevidas.
    """
    assert _call(hands_instance, map_name, conftest.GESTURE_NONE) is None


@pytest.mark.parametrize("map_name", MAP_NAMES)
def test_landmarks_default_nao_dispara_nenhum_map(hands_instance, map_name):
    """Landmarks degenerados (todos em (0.5,0.5)) nao podem casar com gesto algum.

    Com todos os pontos colapsados num so lugar, nenhuma desigualdade estrita
    (>, <) de fronteira se sustenta, logo nada deve disparar.
    """
    lm = make_hand_landmarks()
    assert getattr(hands_instance, map_name)(1000, 1000, lm, None) is None


# ---------------------------------------------------------------------------
# 3. Exclusividade: matriz completa gesto x Map_*
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("gesture_name,coords", list(conftest.ALL_GESTURES.items()))
@pytest.mark.parametrize("map_name", MAP_NAMES)
def test_exclusividade_gesto_dispara_apenas_seu_map(hands_instance, gesture_name, coords, map_name):
    """Cada gesto canonico dispara SO o seu Map_* e nenhum outro.

    Produto cartesiano (5 gestos x 5 maps): na diagonal espera-se True; fora
    dela, None. Protege contra sobreposicao de poses (ambiguidade de gesto).
    """
    resultado = _call(hands_instance, map_name, coords)
    if map_name == gesture_name:
        assert resultado is True
    else:
        assert resultado is None


# ---------------------------------------------------------------------------
# 4. Thresholds de fronteira (logo acima vs logo abaixo do limite)
# ---------------------------------------------------------------------------
# Estrategia: partimos de uma copia do GESTURE_* relevante (que ja satisfaz
# todas as outras condicoes) e mexemos APENAS nos pontos do limite testado,
# fixando-os em coordenadas que rendem pixels exatos (norm * 1000).


class TestThresholdMapOk:
    """Fronteira da distancia polegar(4)-indicador(8) < 0.05*w (=50px @ w=1000)."""

    @staticmethod
    def _ok_com_distancia(dist_px):
        # Ancoramos indicador_8 em (450,450) e afastamos polegar_4 no eixo x.
        coords = dict(conftest.GESTURE_OK)
        coords[INDEX_TIP] = (0.45, 0.45)  # 450, 450
        coords[THUMB_TIP] = ((450 + dist_px) / 1000.0, 0.45)
        return make_hand_landmarks(coords)

    def test_distancia_logo_abaixo_do_limite_dispara(self, hands_instance):
        """dist=49px (< 50) com as demais condicoes ok deve disparar Map_Ok."""
        lm = self._ok_com_distancia(49)
        assert hands_instance.Map_Ok(1000, 1000, lm, None) is True

    def test_distancia_no_limite_exato_nao_dispara(self, hands_instance):
        """dist=50px nao satisfaz '< 50' (comparacao estrita) -> nao dispara."""
        lm = self._ok_com_distancia(50)
        assert hands_instance.Map_Ok(1000, 1000, lm, None) is None

    def test_distancia_logo_acima_do_limite_nao_dispara(self, hands_instance):
        """dist=51px (>= 50) nao dispara Map_Ok."""
        lm = self._ok_com_distancia(51)
        assert hands_instance.Map_Ok(1000, 1000, lm, None) is None


class TestThresholdMapPositive:
    """Fronteira: polegar_4_y < polegar_1_y - 0.05*h (polegar erguido o bastante)."""

    @staticmethod
    def _positive_com_polegar4_y(thumb4_y_px):
        # polegar_1 (idx1) em y=400 -> limite = 400 - 50 = 350.
        coords = dict(conftest.GESTURE_POSITIVE)
        coords[THUMB_CMC] = (0.50, 0.40)  # y = 400
        coords[THUMB_TIP] = (0.50, thumb4_y_px / 1000.0)
        return make_hand_landmarks(coords)

    def test_polegar_logo_acima_do_limite_dispara(self, hands_instance):
        """polegar_4_y=349 (< 350) deve disparar Map_Positive."""
        lm = self._positive_com_polegar4_y(349)
        assert hands_instance.Map_Positive(1000, 1000, lm, None) is True

    def test_polegar_no_limite_exato_nao_dispara(self, hands_instance):
        """polegar_4_y=350 nao satisfaz '< 350' (estrito) -> nao dispara."""
        lm = self._positive_com_polegar4_y(350)
        assert hands_instance.Map_Positive(1000, 1000, lm, None) is None

    def test_polegar_logo_abaixo_do_limite_nao_dispara(self, hands_instance):
        """polegar_4_y=351 (>= 350) nao dispara Map_Positive."""
        lm = self._positive_com_polegar4_y(351)
        assert hands_instance.Map_Positive(1000, 1000, lm, None) is None


class TestThresholdMapSpeak:
    """Fronteira: indicador_8_y < indicador_5_y - 0.05*h (indicador erguido)."""

    @staticmethod
    def _speak_com_indicador8_y(idx8_y_px):
        # indicador_5 (idx5) em y=400 -> limite = 350.
        coords = dict(conftest.GESTURE_SPEAK)
        coords[INDEX_MCP] = (0.50, 0.40)  # y = 400
        coords[INDEX_TIP] = (0.50, idx8_y_px / 1000.0)
        return make_hand_landmarks(coords)

    def test_indicador_logo_acima_do_limite_dispara(self, hands_instance):
        """indicador_8_y=349 (< 350) deve disparar Map_Speak."""
        lm = self._speak_com_indicador8_y(349)
        assert hands_instance.Map_Speak(1000, 1000, lm, None) is True

    def test_indicador_no_limite_exato_nao_dispara(self, hands_instance):
        """indicador_8_y=350 nao satisfaz '< 350' -> nao dispara."""
        lm = self._speak_com_indicador8_y(350)
        assert hands_instance.Map_Speak(1000, 1000, lm, None) is None

    def test_indicador_logo_abaixo_do_limite_nao_dispara(self, hands_instance):
        """indicador_8_y=351 (>= 350) nao dispara Map_Speak."""
        lm = self._speak_com_indicador8_y(351)
        assert hands_instance.Map_Speak(1000, 1000, lm, None) is None


class TestThresholdMapSquid:
    """Fronteira: indicador_8_y < indicador_6_y - 0.05*h."""

    @staticmethod
    def _squid_com_indicador8_y(idx8_y_px):
        # indicador_6 (idx6 = INDEX_PIP) em y=400 -> limite = 350.
        coords = dict(conftest.GESTURE_SQUID)
        coords[INDEX_PIP] = (0.40, 0.40)  # y = 400
        coords[INDEX_TIP] = (0.40, idx8_y_px / 1000.0)
        return make_hand_landmarks(coords)

    def test_indicador_logo_acima_do_limite_dispara(self, hands_instance):
        """indicador_8_y=349 (< 350) deve disparar Map_Squid."""
        lm = self._squid_com_indicador8_y(349)
        assert hands_instance.Map_Squid(1000, 1000, lm, None) is True

    def test_indicador_no_limite_exato_nao_dispara(self, hands_instance):
        """indicador_8_y=350 nao satisfaz '< 350' -> nao dispara."""
        lm = self._squid_com_indicador8_y(350)
        assert hands_instance.Map_Squid(1000, 1000, lm, None) is None

    def test_indicador_logo_abaixo_do_limite_nao_dispara(self, hands_instance):
        """indicador_8_y=351 (>= 350) nao dispara Map_Squid."""
        lm = self._squid_com_indicador8_y(351)
        assert hands_instance.Map_Squid(1000, 1000, lm, None) is None


class TestThresholdMapRock:
    """Fronteira dupla do rock: indicador (8<6-50px) E mindinho (20<18-50px)."""

    @staticmethod
    def _rock_indicador8_y(idx8_y_px):
        # indicador_6 (idx6 = INDEX_PIP) em y=400 -> limite = 350; mindinho ok.
        coords = dict(conftest.GESTURE_ROCK)
        coords[INDEX_PIP] = (0.30, 0.40)  # y = 400
        coords[INDEX_TIP] = (0.30, idx8_y_px / 1000.0)
        return make_hand_landmarks(coords)

    @staticmethod
    def _rock_mindinho20_y(pinky20_y_px):
        # mindinho_18 (idx18 = PINKY_PIP) em y=400 -> limite = 350; indicador ok.
        coords = dict(conftest.GESTURE_ROCK)
        coords[PINKY_PIP] = (0.70, 0.40)  # y = 400
        coords[PINKY_TIP] = (0.70, pinky20_y_px / 1000.0)
        return make_hand_landmarks(coords)

    def test_indicador_logo_acima_do_limite_dispara(self, hands_instance):
        """Com mindinho ok, indicador_8_y=349 (< 350) deve disparar Map_Rock."""
        lm = self._rock_indicador8_y(349)
        assert hands_instance.Map_Rock(1000, 1000, lm, None) is True

    def test_indicador_no_limite_nao_dispara(self, hands_instance):
        """indicador_8_y=350 (nao < 350) quebra a 1a condicao -> nao dispara."""
        lm = self._rock_indicador8_y(350)
        assert hands_instance.Map_Rock(1000, 1000, lm, None) is None

    def test_indicador_logo_abaixo_do_limite_nao_dispara(self, hands_instance):
        """indicador_8_y=351 (>= 350) nao dispara Map_Rock."""
        lm = self._rock_indicador8_y(351)
        assert hands_instance.Map_Rock(1000, 1000, lm, None) is None

    def test_mindinho_logo_acima_do_limite_dispara(self, hands_instance):
        """Com indicador ok, mindinho_20_y=349 (< 350) deve disparar Map_Rock."""
        lm = self._rock_mindinho20_y(349)
        assert hands_instance.Map_Rock(1000, 1000, lm, None) is True

    def test_mindinho_no_limite_nao_dispara(self, hands_instance):
        """mindinho_20_y=350 (nao < 350) quebra a 2a condicao -> nao dispara."""
        lm = self._rock_mindinho20_y(350)
        assert hands_instance.Map_Rock(1000, 1000, lm, None) is None

    def test_mindinho_logo_abaixo_do_limite_nao_dispara(self, hands_instance):
        """mindinho_20_y=351 (>= 350) nao dispara Map_Rock."""
        lm = self._rock_mindinho20_y(351)
        assert hands_instance.Map_Rock(1000, 1000, lm, None) is None


# ---------------------------------------------------------------------------
# 5. Calculate_Distance: euclidiana pura
# ---------------------------------------------------------------------------


class TestCalculateDistance:
    """Distancia euclidiana entre dois pontos (x,y)."""

    @pytest.mark.parametrize(
        "p1,p2,esperado",
        [
            ((0, 0), (3, 4), 5.0),  # triangulo 3-4-5 classico
            ((0, 0), (0, 0), 0.0),  # ponto consigo mesmo
            ((7, 7), (7, 7), 0.0),  # mesmo ponto fora da origem
            ((1, 2), (4, 6), 5.0),  # deslocado: dx=3, dy=4
            ((-3, 0), (0, 4), 5.0),  # coordenadas negativas
        ],
    )
    def test_distancia_valores_conhecidos(self, hands_instance, p1, p2, esperado):
        """A distancia deve bater com o calculo euclidiano para casos conhecidos."""
        assert hands_instance.Calculate_Distance(p1, p2) == pytest.approx(esperado)

    def test_distancia_e_simetrica(self, hands_instance):
        """d(p1,p2) == d(p2,p1): a metrica nao depende da ordem dos argumentos."""
        p1, p2 = (2, 9), (11, 3)
        assert hands_instance.Calculate_Distance(p1, p2) == pytest.approx(
            hands_instance.Calculate_Distance(p2, p1)
        )

    def test_distancia_bate_com_math_hypot(self, hands_instance):
        """Resultado deve coincidir com math.hypot (referencia da stdlib)."""
        p1, p2 = (5, 12), (0, 0)
        assert hands_instance.Calculate_Distance(p1, p2) == pytest.approx(
            math.hypot(p1[0] - p2[0], p1[1] - p2[1])
        )


# ---------------------------------------------------------------------------
# 6. Robustez: rescala de h,w e landmarks nas bordas
# ---------------------------------------------------------------------------


class TestRobustez:
    """Geometria deve ser invariante a escala (coords normalizadas) e segura nas bordas."""

    @pytest.mark.parametrize("h,w", [(480, 640), (720, 1280), (1080, 1920)])
    @pytest.mark.parametrize("map_name,coords", list(conftest.ALL_GESTURES.items()))
    def test_gesto_canonico_dispara_em_resolucoes_variadas(
        self, hands_instance, h, w, map_name, coords
    ):
        """Como os limites escalam com h/w, o gesto canonico ainda dispara fora de 1000x1000.

        Confirma que o reconhecimento nao esta acoplado a uma resolucao fixa
        (a camera do RPi pode entregar varios tamanhos de frame).
        """
        lm = make_hand_landmarks(coords)
        assert getattr(hands_instance, map_name)(h, w, lm, None) is True

    @pytest.mark.parametrize("borda", [0.0, 1.0])
    @pytest.mark.parametrize("map_name", MAP_NAMES)
    def test_landmarks_nas_bordas_nao_levantam_excecao(self, hands_instance, borda, map_name):
        """Todos os 21 pontos em x=y=0.0 ou 1.0 nao podem causar excecao.

        Pixels nas bordas (0 ou w/h) sao validos; o codigo nao deve estourar
        index/overflow. Resultado e indiferente (sera falsy por degeneracao),
        o que importa e nao explodir.
        """
        lm = make_hand_landmarks(default=(borda, borda))
        # Nao deve levantar; com pose degenerada, nenhum gesto casa.
        assert getattr(hands_instance, map_name)(1000, 1000, lm, None) is None

    @pytest.mark.parametrize("map_name,coords", list(conftest.ALL_GESTURES.items()))
    def test_gesto_canonico_estavel_entre_chamadas(self, hands_instance, map_name, coords):
        """Map_* e funcao pura dos landmarks: chamar duas vezes da o mesmo True.

        Garante ausencia de estado interno mutavel escondido entre frames.
        """
        lm = make_hand_landmarks(coords)
        fn = getattr(hands_instance, map_name)
        primeiro = fn(1000, 1000, lm, None)
        segundo = fn(1000, 1000, lm, None)
        assert primeiro is True and segundo is True
