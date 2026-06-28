"""Testes do composition root (jarvis.app.build).

Valida que o wiring monta os componentes dos tipos certos, inicializa o mixer e
compartilha um unico ``RuntimeState`` entre captura e fluxos.
"""

from jarvis import app as app_mod
from jarvis.core.capture import Capture
from jarvis.core.flows import Flows
from jarvis.core.state import RuntimeState
from jarvis.vision.hands import Hands


def test_build_monta_componentes_dos_tipos_certos():
    application = app_mod.build()
    assert isinstance(application.hands, Hands)
    assert isinstance(application.capture, Capture)
    assert isinstance(application.flows, Flows)
    assert isinstance(application.state, RuntimeState)


def test_build_inicializa_mixer():
    """O servico de audio do pygame e inicializado no composition root."""
    app_mod.mixer.init.reset_mock()
    app_mod.build()
    app_mod.mixer.init.assert_called_once()


def test_build_estado_inicial_livre():
    application = app_mod.build()
    assert application.state.busy is False
    assert application.state.is_recording() is False


def test_state_compartilhado_entre_capture_e_flows():
    """O mesmo RuntimeState e injetado em capture e flows (estado unico)."""
    application = app_mod.build()
    assert application.flows.state is application.capture.state
    assert application.flows.state is application.state


def test_flows_recebe_o_capture_construido():
    """O capture montado e o mesmo injetado no flows."""
    application = app_mod.build()
    assert application.flows.capture is application.capture
