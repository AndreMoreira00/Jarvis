"""Testes de ``RuntimeState`` (jarvis.core.state).

Estado efemero compartilhado das acoes: trava ``busy`` + gravacao de video
(``threading.Event``). Substitui a antiga flag ``ACTION`` e o ``_recording`` que
viviam dentro de ``Control``.
"""

from jarvis.core.state import RuntimeState


def test_estado_inicial_livre_e_sem_gravacao():
    state = RuntimeState()
    assert state.busy is False
    assert state.is_recording() is False


def test_begin_e_end_alternam_busy():
    state = RuntimeState()
    state.begin()
    assert state.busy is True
    state.end()
    assert state.busy is False


def test_toggle_recording_liga_e_desliga():
    """toggle alterna o Event e o retorno reflete o novo estado."""
    state = RuntimeState()
    assert state.toggle_recording() is True  # passou a gravar
    assert state.is_recording() is True
    assert state.toggle_recording() is False  # parou
    assert state.is_recording() is False


def test_start_e_stop_recording():
    state = RuntimeState()
    state.start_recording()
    assert state.is_recording() is True
    state.stop_recording()
    assert state.is_recording() is False
