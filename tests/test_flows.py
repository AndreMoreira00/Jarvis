"""Testes de ``Flows`` (jarvis.core.flows): a 'state machine' das acoes.

Cada fluxo orquestra captura -> assistente -> fala sob a trava ``busy``. Aqui os
colaboradores (capture, assistant, bridge) sao mockados e o ``RuntimeState`` e
real, entao validamos a LOGICA de orquestracao (ordem, trava, gravacao, consulta
condicional ao assistente), nao o I/O nem a corrotina em si.
"""

from concurrent.futures import Future
from unittest.mock import MagicMock

import pytest

from jarvis.core import flows as flows_mod
from jarvis.core.state import RuntimeState


def _make_future(value):
    fut = Future()
    fut.set_result(value)
    return fut


@pytest.fixture
def state():
    return RuntimeState()


@pytest.fixture
def flows_instance(state):
    """``Flows`` com capture/assistant/bridge mockados e state real."""
    capture = MagicMock(name="capture")
    assistant = MagicMock(name="assistant")
    bridge = MagicMock(name="bridge")
    return flows_mod.Flows(capture, assistant, bridge, state)


# ---------------------------------------------------------------------------
# audio_to_audio
# ---------------------------------------------------------------------------


class TestAudioToAudio:
    def test_roda_text_to_text_e_libera_busy(self, flows_instance):
        """O prompt transcrito vira text_to_text (via bridge) e busy volta a False."""
        flows_instance.capture.capture_audio.return_value = "qual a previsao?"
        flows_instance.audio_to_audio(MagicMock(name="executor"))

        flows_instance.assistant.text_to_text.assert_called_once_with("qual a previsao?")
        flows_instance.bridge.run.assert_called_once_with(
            flows_instance.assistant.text_to_text.return_value
        )
        assert flows_instance.state.busy is False

    def test_capture_audio_recebe_executor(self, flows_instance):
        executor = MagicMock(name="executor")
        flows_instance.capture.capture_audio.return_value = "oi"
        flows_instance.audio_to_audio(executor)
        flows_instance.capture.capture_audio.assert_called_once_with(executor)

    def test_prompt_vazio_nao_consulta_assistente(self, flows_instance):
        """Sem pergunta valida (None), bridge.run NAO e chamado."""
        flows_instance.capture.capture_audio.return_value = None
        flows_instance.audio_to_audio(MagicMock(name="executor"))

        flows_instance.bridge.run.assert_not_called()
        assert flows_instance.state.busy is False


# ---------------------------------------------------------------------------
# image_audio
# ---------------------------------------------------------------------------


class TestImageAudio:
    def test_passa_caminho_da_foto_e_prompt(self, flows_instance):
        """image_to_text recebe (image_path, prompt) e busy volta a False."""
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/foto.jpg")  # capture_photo
        flows_instance.capture.capture_audio.return_value = "o que e isso?"
        flows_instance.image_audio(MagicMock(name="frame"), executor)

        flows_instance.assistant.image_to_text.assert_called_once_with(
            "midia/foto.jpg", "o que e isso?"
        )
        flows_instance.bridge.run.assert_called_once_with(
            flows_instance.assistant.image_to_text.return_value
        )
        assert flows_instance.state.busy is False

    def test_prompt_vazio_nao_consulta_assistente(self, flows_instance):
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/foto.jpg")
        flows_instance.capture.capture_audio.return_value = None
        flows_instance.image_audio(MagicMock(name="frame"), executor)

        flows_instance.bridge.run.assert_not_called()
        assert flows_instance.state.busy is False


# ---------------------------------------------------------------------------
# video_audio
# ---------------------------------------------------------------------------


class TestVideoAudio:
    def test_passa_caminho_do_video_e_prompt(self, flows_instance):
        """video_to_text recebe (video_path, prompt) e busy volta a False."""
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/video.avi")  # capture_video
        flows_instance.capture.capture_audio.return_value = "descreva a cena"
        flows_instance.video_audio(MagicMock(name="cap"), executor)

        flows_instance.assistant.video_to_text.assert_called_once_with(
            "midia/video.avi", "descreva a cena"
        )
        assert flows_instance.state.busy is False

    def test_capture_audio_recebe_executor(self, flows_instance):
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/v.avi")
        flows_instance.capture.capture_audio.return_value = "x"
        flows_instance.video_audio(MagicMock(name="cap"), executor)
        flows_instance.capture.capture_audio.assert_called_once_with(executor)

    def test_encerra_gravacao_ao_final(self, flows_instance):
        """Ao fim do fluxo a gravacao esta encerrada (state nao gravando)."""
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/v.avi")
        flows_instance.capture.capture_audio.return_value = "x"
        flows_instance.video_audio(MagicMock(name="cap"), executor)

        assert flows_instance.state.is_recording() is False
