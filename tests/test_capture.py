"""Testes de ``Capture`` (jarvis.core.capture): captura de foto/video/audio.

Foco no NOSSO codigo de I/O (nomes por timestamp, encadeamento de upload, loop de
gravacao via ``RuntimeState``, sons de confirmacao e tratamento de erro do
reconhecimento de voz), nao as libs stubadas. ``Capture`` recebe seus
colaboradores por construtor (config, uploader, state, mixer).
"""

from concurrent.futures import Future
from unittest.mock import MagicMock, patch

import pytest

from jarvis.config import Config
from jarvis.core import capture as capture_mod
from jarvis.core.state import RuntimeState


def _make_future(value):
    """``concurrent.futures.Future`` ja resolvido com ``value``."""
    fut = Future()
    fut.set_result(value)
    return fut


class _ImmediateExecutor:
    """Executor falso: roda ``fn`` na hora e devolve um Future ja resolvido."""

    def __init__(self):
        self.calls = []

    def submit(self, fn, *args, **kwargs):
        self.calls.append((fn, args, kwargs))
        try:
            result = fn(*args, **kwargs)
        except Exception as exc:  # propaga via Future, como o real faria
            fut = Future()
            fut.set_exception(exc)
            return fut
        return _make_future(result)


@pytest.fixture
def state():
    return RuntimeState()


@pytest.fixture
def capture_instance(state):
    """``Capture`` com config default, uploader/mixer mockados e state real."""
    mixer = MagicMock(name="mixer")
    mixer.Sound.return_value.get_length.return_value = 0.0
    uploader = MagicMock(name="uploader")
    return capture_mod.Capture(Config(), uploader, state, mixer)


# ---------------------------------------------------------------------------
# play_confirmation_sound (sincrono)
# ---------------------------------------------------------------------------


class TestPlayConfirmationSound:
    def test_toca_e_para_o_som(self, capture_instance):
        """play() e stop() sao chamados; get_length alimenta o sleep."""
        sound_obj = MagicMock(name="sound")
        sound_obj.get_length.return_value = 0.0
        with patch.object(capture_instance.mixer, "Sound", return_value=sound_obj) as mk_sound:
            capture_instance.play_confirmation_sound("audios_check/x.wav")

        mk_sound.assert_called_once_with("audios_check/x.wav")
        sound_obj.play.assert_called_once()
        sound_obj.get_length.assert_called_once()
        sound_obj.stop.assert_called_once()


# ---------------------------------------------------------------------------
# capture_photo
# ---------------------------------------------------------------------------


class TestCapturePhoto:
    def test_grava_jpg_com_timestamp_e_agenda_upload(self, capture_instance, fake_frame):
        """imwrite recebe midia/<timestamp>.jpg; upload e agendado; retorna o caminho."""
        executor = MagicMock(name="executor")
        with (
            patch.object(capture_mod, "cv2") as mk_cv2,
            patch.object(capture_mod.time, "strftime", return_value="20260627_120000"),
        ):
            caminho = capture_instance.capture_photo(fake_frame, executor)

        esperado = "midia/20260627_120000.jpg"
        assert caminho == esperado
        mk_cv2.imwrite.assert_called_once_with(esperado, fake_frame)
        executor.submit.assert_called_once_with(capture_instance.uploader.upload_media, esperado)

    def test_toca_som_de_foto(self, capture_instance, fake_frame):
        """O som de confirmacao usado e o config.photo_sound (chamada sincrona)."""
        executor = MagicMock(name="executor")
        with (
            patch.object(capture_mod, "cv2"),
            patch.object(capture_instance, "play_confirmation_sound") as mk_play,
        ):
            capture_instance.capture_photo(fake_frame, executor)
        mk_play.assert_called_once_with(capture_instance.config.photo_sound)


# ---------------------------------------------------------------------------
# capture_video (controlado por RuntimeState)
# ---------------------------------------------------------------------------


class TestCaptureVideo:
    def test_sem_gravar_nao_entra_no_loop_mas_finaliza(self, capture_instance):
        """state nao gravando: o while nao roda; VideoWriter criado e released."""
        cap = MagicMock(name="cap")
        executor = MagicMock(name="executor")
        out = MagicMock(name="out")
        with (
            patch.object(capture_mod, "cv2") as mk_cv2,
            patch.object(capture_mod.time, "strftime", return_value="20260627_120000"),
        ):
            mk_cv2.VideoWriter.return_value = out
            caminho = capture_instance.capture_video(cap, executor)

        esperado = "midia/20260627_120000.avi"
        assert caminho == esperado
        mk_cv2.VideoWriter.assert_called_once()
        out.release.assert_called_once()
        out.write.assert_not_called()
        cap.read.assert_not_called()
        executor.submit.assert_called_once_with(capture_instance.uploader.upload_media, esperado)

    def test_uma_iteracao_grava_um_frame(self, capture_instance):
        """Com gravacao ligada e desligada no 1o read, grava exatamente 1 frame."""
        cap = MagicMock(name="cap")
        executor = MagicMock(name="executor")
        out = MagicMock(name="out")
        frame_obj = MagicMock(name="frame")

        capture_instance.state.start_recording()

        def read_then_stop():
            # desliga apos a 1a leitura -> o while encerra na proxima checagem
            capture_instance.state.stop_recording()
            return True, frame_obj

        cap.read.side_effect = read_then_stop

        with (
            patch.object(capture_mod, "cv2") as mk_cv2,
            patch.object(capture_mod.time, "strftime", return_value="20260627_120000"),
            patch.object(capture_mod.time, "sleep"),
        ):
            mk_cv2.VideoWriter.return_value = out
            caminho = capture_instance.capture_video(cap, executor)

        assert caminho == "midia/20260627_120000.avi"
        cap.read.assert_called_once()
        out.write.assert_called_once_with(frame_obj)
        out.release.assert_called_once()

    def test_read_sem_sucesso_encerra_gravacao(self, capture_instance):
        """Se cap.read() falha (status False), a gravacao para sem escrever frame."""
        cap = MagicMock(name="cap")
        executor = MagicMock(name="executor")
        out = MagicMock(name="out")

        capture_instance.state.start_recording()
        cap.read.return_value = (False, None)  # camera falhou

        with (
            patch.object(capture_mod, "cv2") as mk_cv2,
            patch.object(capture_mod.time, "strftime", return_value="20260627_120000"),
            patch.object(capture_mod.time, "sleep"),
        ):
            mk_cv2.VideoWriter.return_value = out
            capture_instance.capture_video(cap, executor)

        cap.read.assert_called_once()
        out.write.assert_not_called()
        out.release.assert_called_once()


# ---------------------------------------------------------------------------
# capture_audio (retorna None em qualquer falha; marca busy)
# ---------------------------------------------------------------------------


class TestCaptureAudio:
    @pytest.fixture
    def recognizer(self):
        """Recognizer falso configuravel; substitui sr.Recognizer no modulo capture."""
        rec = MagicMock(name="recognizer")
        with (
            patch.object(capture_mod.sr, "Recognizer", return_value=rec),
            patch.object(capture_mod.sr, "Microphone") as mk_mic,
        ):
            mk_mic.return_value.__enter__.return_value = MagicMock(name="source")
            yield rec

    def test_retorno_inclui_texto_reconhecido(self, capture_instance, recognizer):
        """Happy path: o texto do recognize_google e retornado e o state fica busy."""
        recognizer.recognize_google.return_value = "ola jarvis"
        resultado = capture_instance.capture_audio(_ImmediateExecutor())

        assert resultado == "ola jarvis"
        assert capture_instance.state.busy is True
        recognizer.recognize_google.assert_called_once()
        assert recognizer.recognize_google.call_args.kwargs.get("language") == "pt-BR"

    def test_unknown_value_error_retorna_none(self, capture_instance, recognizer):
        recognizer.recognize_google.side_effect = capture_mod.sr.UnknownValueError()
        assert capture_instance.capture_audio(_ImmediateExecutor()) is None

    def test_request_error_retorna_none(self, capture_instance, recognizer):
        recognizer.recognize_google.side_effect = capture_mod.sr.RequestError()
        assert capture_instance.capture_audio(_ImmediateExecutor()) is None

    def test_excecao_generica_retorna_none(self, capture_instance, recognizer):
        recognizer.recognize_google.side_effect = ValueError("boom")
        assert capture_instance.capture_audio(_ImmediateExecutor()) is None

    def test_texto_vazio_retorna_none(self, capture_instance, recognizer):
        recognizer.recognize_google.return_value = ""
        assert capture_instance.capture_audio(_ImmediateExecutor()) is None

    def test_configura_parametros_do_microfone(self, capture_instance, recognizer):
        recognizer.recognize_google.return_value = "ok"
        capture_instance.capture_audio(_ImmediateExecutor())

        assert recognizer.pause_threshold == 0.8
        assert recognizer.dynamic_energy_threshold is False
        assert recognizer.energy_threshold == 300
