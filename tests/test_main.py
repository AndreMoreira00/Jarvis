"""Testes do orquestrador ``main.py``.

Foco no que e testavel de forma honesta:

- ``Check_Gesture``: a logica central de decisao (gesto + mao -> seta cooldown
  e, conforme ``controls_recording``, alterna a gravacao e/ou dispara
  ``func_exe``). Funcao sincrona, sem I/O, entao da pra exercitar todos os ramos.
- ``init_hands`` / ``init_control``: helpers async que rodam o construtor em
  executor e devolvem a instancia (tipo verificado).

O loop ``main()`` em si abre camera e faz I/O de janela num
``while cap.isOpened()``; nao e testado aqui. A regra de decremento do cooldown
vive dentro desse loop; cobrimos apenas o lado que *seta* o cooldown.
"""

from unittest.mock import MagicMock

import pytest

import main


@pytest.fixture(autouse=True)
def reset_cooldown():
    """Zera o global ``main.gesture_cooldown`` antes e depois de cada teste."""
    main.gesture_cooldown = 0
    yield
    main.gesture_cooldown = 0


@pytest.fixture
def control_stub():
    """Stub de ``control_functions`` com so o que ``Check_Gesture`` toca.

    ``toggle_recording`` por padrao devolve ``True`` (passou a gravar).
    """
    stub = MagicMock(name="control_functions")
    stub.toggle_recording.return_value = True
    return stub


def _make_act(result):
    """Cria um ``func_act`` (callable sem args) que devolve ``result`` fixo."""
    return lambda: result


# ---------------------------------------------------------------------------
# Check_Gesture: gesto comum (foto/voz/imagem), sem controle de gravacao
# ---------------------------------------------------------------------------


def test_dispara_func_exe_quando_gesto_e_mao_batem(control_stub):
    """func_act True + hand_label == side, gesto comum -> func_exe chamada."""
    func_exe = MagicMock(name="func_exe")
    main.Check_Gesture(func_exe, _make_act(True), "Right", "Right", 20, False, control_stub)
    func_exe.assert_called_once_with()


def test_seta_cooldown_global(control_stub):
    """No caminho feliz o global ``gesture_cooldown`` recebe o valor de cooldown."""
    main.Check_Gesture(MagicMock(), _make_act(True), "Left", "Left", 30, False, control_stub)
    assert main.gesture_cooldown == 30


def test_gesto_comum_nao_alterna_gravacao(control_stub):
    """Gesto com controls_recording=False nao chama toggle_recording."""
    main.Check_Gesture(MagicMock(), _make_act(True), "Right", "Right", 20, False, control_stub)
    control_stub.toggle_recording.assert_not_called()


# ---------------------------------------------------------------------------
# Check_Gesture: gesto de gravacao -> toggle + submete worker so ao INICIAR
# ---------------------------------------------------------------------------


def test_inicio_de_gravacao_dispara_worker(control_stub):
    """controls_recording=True e toggle_recording()->True (iniciou): func_exe roda."""
    control_stub.toggle_recording.return_value = True
    func_exe = MagicMock(name="func_exe")
    main.Check_Gesture(func_exe, _make_act(True), "Left", "Left", 30, True, control_stub)
    control_stub.toggle_recording.assert_called_once_with()
    func_exe.assert_called_once_with()


def test_parada_de_gravacao_nao_dispara_worker(control_stub):
    """controls_recording=True e toggle_recording()->False (parou): NAO submete worker."""
    control_stub.toggle_recording.return_value = False
    func_exe = MagicMock(name="func_exe")
    main.Check_Gesture(func_exe, _make_act(True), "Left", "Left", 30, True, control_stub)
    control_stub.toggle_recording.assert_called_once_with()
    func_exe.assert_not_called()


# ---------------------------------------------------------------------------
# Check_Gesture: mao errada -> nada acontece
# ---------------------------------------------------------------------------


def test_nao_dispara_quando_mao_diverge(control_stub):
    """Gesto detectado mas em mao diferente de ``side``: nada e disparado."""
    func_exe = MagicMock(name="func_exe")
    main.Check_Gesture(func_exe, _make_act(True), "Right", "Left", 20, False, control_stub)
    func_exe.assert_not_called()
    control_stub.toggle_recording.assert_not_called()


def test_mao_diverge_nao_altera_cooldown(control_stub):
    """Mao divergente nao deve mexer no cooldown global (continua 0)."""
    main.gesture_cooldown = 0
    main.Check_Gesture(MagicMock(), _make_act(True), "Right", "Left", 20, False, control_stub)
    assert main.gesture_cooldown == 0


# ---------------------------------------------------------------------------
# Check_Gesture: gesto ausente -> nada acontece
# ---------------------------------------------------------------------------


def test_nao_dispara_quando_gesto_ausente(control_stub):
    """func_act False: independentemente da mao, nada e disparado."""
    func_exe = MagicMock(name="func_exe")
    main.Check_Gesture(func_exe, _make_act(False), "Right", "Right", 20, False, control_stub)
    func_exe.assert_not_called()
    assert main.gesture_cooldown == 0
    control_stub.toggle_recording.assert_not_called()


# ---------------------------------------------------------------------------
# Check_Gesture: ordem (cooldown setado ANTES de func_exe)
# ---------------------------------------------------------------------------


def test_seta_cooldown_antes_de_chamar_func_exe(control_stub):
    """Garante que o cooldown ja esta setado no momento em que ``func_exe`` roda."""
    visto = {}

    def spy():
        visto["cooldown_no_disparo"] = main.gesture_cooldown

    main.Check_Gesture(spy, _make_act(True), "Right", "Right", 42, False, control_stub)
    assert visto["cooldown_no_disparo"] == 42


@pytest.mark.parametrize(
    "side,hand_label,deve_disparar",
    [
        ("Right", "Right", True),
        ("Left", "Left", True),
        ("Right", "Left", False),
        ("Left", "Right", False),
    ],
)
def test_match_de_mao(side, hand_label, deve_disparar, control_stub):
    """Tabela-verdade do match ``hand_label == side`` com gesto sempre presente."""
    func_exe = MagicMock(name="func_exe")
    main.Check_Gesture(func_exe, _make_act(True), side, hand_label, 20, False, control_stub)
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
    """A instancia de Control vem com ACTION desligado e sem gravacao em curso."""
    resultado = await main.init_control()

    assert resultado.ACTION is False
    assert resultado.is_recording() is False
