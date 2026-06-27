"""Testes do orquestrador ``main.py``.

Foco no que e testavel de forma honesta:

- ``Check_Gesture``: a logica central de decisao (gesto + mao + estado ->
  seta cooldown, alterna ``Control_Video``, dispara ``func_exe``). E uma corrotina
  pura, sem I/O, entao da pra exercitar todos os ramos.
- ``init_hands`` / ``init_control``: helpers async que rodam o construtor em
  executor e devolvem a instancia (tipo verificado).

O loop ``main()`` em si abre camera (``cv2.VideoCapture``) e faz I/O de janela
(``cv2.imshow``/``waitKey``) num ``while cap.isOpened()``; nao e testado aqui
(ver ``notes`` no retorno). A regra de decremento do cooldown
(``if gesture_cooldown > 0: gesture_cooldown -= 1``) vive dentro desse loop e nao
e extraivel sem reexecutar o loop; cobrimos apenas o lado que *seta* o cooldown
(``Check_Gesture``), sem reimplementar a logica de decremento.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import main


@pytest.fixture(autouse=True)
def reset_cooldown():
    """Zera o global ``main.gesture_cooldown`` antes e depois de cada teste.

    Como e estado de modulo, sem isso um teste contaminaria o seguinte.
    """
    main.gesture_cooldown = 0
    yield
    main.gesture_cooldown = 0


@pytest.fixture
def control_stub():
    """Stub minimo de ``control_functions`` com so o que ``Check_Gesture`` toca.

    ``Control_Video`` comeca em ``False`` (mesmo default da classe real).
    """
    return SimpleNamespace(Control_Video=False)


def _make_act(result):
    """Cria um ``func_act`` (callable sem args) que devolve ``result`` fixo."""
    return lambda: result


# ---------------------------------------------------------------------------
# Check_Gesture: caminho feliz (gesto detectado, mao certa, estado Async)
# ---------------------------------------------------------------------------

async def test_check_gesture_disparada_quando_gesto_e_mao_batem(control_stub):
    """func_act True + hand_label == side + state Async dispara func_exe."""
    func_exe = MagicMock(name="func_exe")

    await main.Check_Gesture(
        func_exe=func_exe,
        func_act=_make_act(True),
        side="Right",
        hand_label="Right",
        state="Async",
        cooldown=20,
        control_functions=control_stub,
    )

    func_exe.assert_called_once_with()


async def test_check_gesture_seta_cooldown_global(control_stub):
    """No caminho feliz o global ``gesture_cooldown`` recebe o valor de cooldown."""
    await main.Check_Gesture(
        func_exe=MagicMock(),
        func_act=_make_act(True),
        side="Left",
        hand_label="Left",
        state="Async",
        cooldown=30,
        control_functions=control_stub,
    )

    assert main.gesture_cooldown == 30


async def test_check_gesture_alterna_control_video(control_stub):
    """No caminho feliz ``Control_Video`` e invertido (False -> True)."""
    control_stub.Control_Video = False

    await main.Check_Gesture(
        func_exe=MagicMock(),
        func_act=_make_act(True),
        side="Right",
        hand_label="Right",
        state="Async",
        cooldown=20,
        control_functions=control_stub,
    )

    assert control_stub.Control_Video is True


async def test_check_gesture_alterna_control_video_de_true_para_false(control_stub):
    """A inversao e simetrica: se ja estava True, volta para False."""
    control_stub.Control_Video = True

    await main.Check_Gesture(
        func_exe=MagicMock(),
        func_act=_make_act(True),
        side="Right",
        hand_label="Right",
        state="Async",
        cooldown=20,
        control_functions=control_stub,
    )

    assert control_stub.Control_Video is False


# ---------------------------------------------------------------------------
# Check_Gesture: mao errada -> nao dispara
# ---------------------------------------------------------------------------

async def test_check_gesture_nao_dispara_quando_mao_diverge(control_stub):
    """Gesto detectado mas em mao diferente de ``side``: func_exe NAO e chamada."""
    func_exe = MagicMock(name="func_exe")

    await main.Check_Gesture(
        func_exe=func_exe,
        func_act=_make_act(True),
        side="Right",
        hand_label="Left",
        state="Async",
        cooldown=20,
        control_functions=control_stub,
    )

    func_exe.assert_not_called()


async def test_check_gesture_mao_diverge_nao_altera_cooldown(control_stub):
    """Mao divergente nao deve mexer no cooldown global (continua 0)."""
    main.gesture_cooldown = 0

    await main.Check_Gesture(
        func_exe=MagicMock(),
        func_act=_make_act(True),
        side="Right",
        hand_label="Left",
        state="Async",
        cooldown=20,
        control_functions=control_stub,
    )

    assert main.gesture_cooldown == 0


async def test_check_gesture_mao_diverge_nao_altera_control_video(control_stub):
    """Mao divergente nao deve inverter ``Control_Video``."""
    control_stub.Control_Video = False

    await main.Check_Gesture(
        func_exe=MagicMock(),
        func_act=_make_act(True),
        side="Right",
        hand_label="Left",
        state="Async",
        cooldown=20,
        control_functions=control_stub,
    )

    assert control_stub.Control_Video is False


# ---------------------------------------------------------------------------
# Check_Gesture: gesto ausente -> nada acontece
# ---------------------------------------------------------------------------

async def test_check_gesture_nao_dispara_quando_gesto_ausente(control_stub):
    """func_act False: independentemente da mao, nada e disparado."""
    func_exe = MagicMock(name="func_exe")

    await main.Check_Gesture(
        func_exe=func_exe,
        func_act=_make_act(False),
        side="Right",
        hand_label="Right",
        state="Async",
        cooldown=20,
        control_functions=control_stub,
    )

    func_exe.assert_not_called()
    assert main.gesture_cooldown == 0
    assert control_stub.Control_Video is False


# ---------------------------------------------------------------------------
# Check_Gesture: estado != "Async" -> seta cooldown mas NAO dispara nem alterna
# ---------------------------------------------------------------------------

async def test_check_gesture_estado_nao_async_seta_cooldown_mas_nao_dispara(control_stub):
    """Documenta o comportamento ATUAL: com state != 'Async', o codigo entra no
    ``if func_act() and hand_label == side`` (setando o cooldown) mas pula o bloco
    interno (sem alternar ``Control_Video`` nem chamar ``func_exe``).
    """
    func_exe = MagicMock(name="func_exe")
    control_stub.Control_Video = False

    await main.Check_Gesture(
        func_exe=func_exe,
        func_act=_make_act(True),
        side="Right",
        hand_label="Right",
        state="Sync",  # qualquer valor diferente de "Async"
        cooldown=15,
        control_functions=control_stub,
    )

    assert main.gesture_cooldown == 15  # cooldown e setado antes do check de state
    func_exe.assert_not_called()         # mas o bloco Async nao roda
    assert control_stub.Control_Video is False


# ---------------------------------------------------------------------------
# Check_Gesture: ordem de efeitos (cooldown setado ANTES de func_exe)
# ---------------------------------------------------------------------------

async def test_check_gesture_seta_cooldown_antes_de_chamar_func_exe(control_stub):
    """Garante que o cooldown ja esta setado no momento em que ``func_exe`` roda.

    Importante para a semantica de debounce: a acao so e disparada com o cooldown
    ja armado, evitando reentrancia no mesmo gesto.
    """
    visto = {}

    def spy():
        visto["cooldown_no_disparo"] = main.gesture_cooldown

    await main.Check_Gesture(
        func_exe=spy,
        func_act=_make_act(True),
        side="Right",
        hand_label="Right",
        state="Async",
        cooldown=42,
        control_functions=control_stub,
    )

    assert visto["cooldown_no_disparo"] == 42


@pytest.mark.parametrize("side,hand_label,deve_disparar", [
    ("Right", "Right", True),
    ("Left", "Left", True),
    ("Right", "Left", False),
    ("Left", "Right", False),
])
async def test_check_gesture_match_de_mao(side, hand_label, deve_disparar, control_stub):
    """Tabela-verdade do match ``hand_label == side`` com gesto sempre presente."""
    func_exe = MagicMock(name="func_exe")

    await main.Check_Gesture(
        func_exe=func_exe,
        func_act=_make_act(True),
        side=side,
        hand_label=hand_label,
        state="Async",
        cooldown=20,
        control_functions=control_stub,
    )

    assert func_exe.called is deve_disparar


# ---------------------------------------------------------------------------
# init_hands / init_control: helpers async retornam instancias corretas
# ---------------------------------------------------------------------------

async def test_init_hands_retorna_instancia_de_hands():
    """``init_hands`` roda ``hands.Hands`` em executor e devolve a instancia."""
    import hands

    resultado = await main.init_hands()

    assert isinstance(resultado, hands.Hands)


async def test_init_control_retorna_instancia_de_control():
    """``init_control`` roda ``control.Control`` em executor e devolve a instancia."""
    import control

    resultado = await main.init_control()

    assert isinstance(resultado, control.Control)


async def test_init_control_instancia_tem_estado_inicial_esperado():
    """A instancia de Control vem com as flags de concorrencia no default.

    Confirma que o helper devolve um objeto utilizavel pelo loop (ACTION e
    Control_Video em False), nao um mock vazio.
    """
    resultado = await main.init_control()

    assert resultado.ACTION is False
    assert resultado.Control_Video is False
