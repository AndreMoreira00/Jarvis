"""Testes do loop principal (jarvis.core.loop): ``check_gesture``.

Foco no que e testavel de forma honesta:

- ``check_gesture``: a logica central de decisao (gesto + mao -> seta cooldown
  e, conforme ``controls_recording``, alterna a gravacao e/ou dispara
  ``func_exe``). Funcao sincrona, sem I/O, entao da pra exercitar todos os ramos.

O loop ``main()`` em si abre camera, monta o app (composition root) e faz I/O de
janela num ``while cap.isOpened()``; nao e testado aqui (a montagem e coberta por
test_app.py). A regra de decremento do cooldown vive dentro desse loop; cobrimos
apenas o lado que *seta* o cooldown.
"""

from unittest.mock import MagicMock

import pytest

from jarvis.core import loop


@pytest.fixture(autouse=True)
def reset_cooldown():
    """Zera o global ``loop.gesture_cooldown`` antes e depois de cada teste."""
    loop.gesture_cooldown = 0
    yield
    loop.gesture_cooldown = 0


@pytest.fixture
def state_stub():
    """Stub do ``state`` (RuntimeState) com so o que ``check_gesture`` toca.

    ``toggle_recording`` por padrao devolve ``True`` (passou a gravar).
    """
    stub = MagicMock(name="state")
    stub.toggle_recording.return_value = True
    return stub


def _make_act(result):
    """Cria um ``func_act`` (callable sem args) que devolve ``result`` fixo."""
    return lambda: result


# ---------------------------------------------------------------------------
# check_gesture: gesto comum (foto/voz/imagem), sem controle de gravacao
# ---------------------------------------------------------------------------


def test_dispara_func_exe_quando_gesto_e_mao_batem(state_stub):
    """func_act True + hand_label == side, gesto comum -> func_exe chamada."""
    func_exe = MagicMock(name="func_exe")
    loop.check_gesture(func_exe, _make_act(True), "Right", "Right", 20, False, state_stub)
    func_exe.assert_called_once_with()


def test_seta_cooldown_global(state_stub):
    """No caminho feliz o global ``gesture_cooldown`` recebe o valor de cooldown."""
    loop.check_gesture(MagicMock(), _make_act(True), "Left", "Left", 30, False, state_stub)
    assert loop.gesture_cooldown == 30


def test_gesto_comum_nao_alterna_gravacao(state_stub):
    """Gesto com controls_recording=False nao chama toggle_recording."""
    loop.check_gesture(MagicMock(), _make_act(True), "Right", "Right", 20, False, state_stub)
    state_stub.toggle_recording.assert_not_called()


# ---------------------------------------------------------------------------
# check_gesture: gesto de gravacao -> toggle + submete worker so ao INICIAR
# ---------------------------------------------------------------------------


def test_inicio_de_gravacao_dispara_worker(state_stub):
    """controls_recording=True e toggle_recording()->True (iniciou): func_exe roda."""
    state_stub.toggle_recording.return_value = True
    func_exe = MagicMock(name="func_exe")
    loop.check_gesture(func_exe, _make_act(True), "Left", "Left", 30, True, state_stub)
    state_stub.toggle_recording.assert_called_once_with()
    func_exe.assert_called_once_with()


def test_parada_de_gravacao_nao_dispara_worker(state_stub):
    """controls_recording=True e toggle_recording()->False (parou): NAO submete worker."""
    state_stub.toggle_recording.return_value = False
    func_exe = MagicMock(name="func_exe")
    loop.check_gesture(func_exe, _make_act(True), "Left", "Left", 30, True, state_stub)
    state_stub.toggle_recording.assert_called_once_with()
    func_exe.assert_not_called()


# ---------------------------------------------------------------------------
# check_gesture: mao errada -> nada acontece
# ---------------------------------------------------------------------------


def test_nao_dispara_quando_mao_diverge(state_stub):
    """Gesto detectado mas em mao diferente de ``side``: nada e disparado."""
    func_exe = MagicMock(name="func_exe")
    loop.check_gesture(func_exe, _make_act(True), "Right", "Left", 20, False, state_stub)
    func_exe.assert_not_called()
    state_stub.toggle_recording.assert_not_called()


def test_mao_diverge_nao_altera_cooldown(state_stub):
    """Mao divergente nao deve mexer no cooldown global (continua 0)."""
    loop.gesture_cooldown = 0
    loop.check_gesture(MagicMock(), _make_act(True), "Right", "Left", 20, False, state_stub)
    assert loop.gesture_cooldown == 0


# ---------------------------------------------------------------------------
# check_gesture: gesto ausente -> nada acontece
# ---------------------------------------------------------------------------


def test_nao_dispara_quando_gesto_ausente(state_stub):
    """func_act False: independentemente da mao, nada e disparado."""
    func_exe = MagicMock(name="func_exe")
    loop.check_gesture(func_exe, _make_act(False), "Right", "Right", 20, False, state_stub)
    func_exe.assert_not_called()
    assert loop.gesture_cooldown == 0
    state_stub.toggle_recording.assert_not_called()


# ---------------------------------------------------------------------------
# check_gesture: ordem (cooldown setado ANTES de func_exe)
# ---------------------------------------------------------------------------


def test_seta_cooldown_antes_de_chamar_func_exe(state_stub):
    """Garante que o cooldown ja esta setado no momento em que ``func_exe`` roda."""
    visto = {}

    def spy():
        visto["cooldown_no_disparo"] = loop.gesture_cooldown

    loop.check_gesture(spy, _make_act(True), "Right", "Right", 42, False, state_stub)
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
def test_match_de_mao(side, hand_label, deve_disparar, state_stub):
    """Tabela-verdade do match ``hand_label == side`` com gesto sempre presente."""
    func_exe = MagicMock(name="func_exe")
    loop.check_gesture(func_exe, _make_act(True), side, hand_label, 20, False, state_stub)
    assert func_exe.called is deve_disparar
