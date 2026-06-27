"""Testes da classe ``Control`` (control.py): orquestracao das acoes do Jarvis.

Foco: testar O NOSSO codigo (fluxo de captura, encadeamento de futures, trava
``ACTION``, estado de gravacao via ``threading.Event``, nomes por timestamp e
tratamento de erros do reconhecimento de voz), nao as libs stubadas.

Isolamento da rede/IA:
- Apos criar ``Control()``, substituimos ``jarvis_system`` e ``menager_system``
  por mocks. Os metodos do jarvis sao corrotinas (rodadas via ``self._run`` =
  run_until_complete num loop por thread), entao usamos ``AsyncMock``.
- ``mixer`` vem do stub MagicMock do pygame; ``play_confirmation_sound`` agora e
  SINCRONO e usa ``time.sleep(get_length())``, entao fixamos get_length em 0.0.
"""

from concurrent.futures import Future
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jarvis.core import control as control_mod

# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------


def _make_future(value):
    """Cria um ``concurrent.futures.Future`` ja resolvido com ``value``."""
    fut = Future()
    fut.set_result(value)
    return fut


@pytest.fixture
def control_instance():
    """Instancia de ``Control`` com jarvis e manager mockados."""
    ctrl = control_mod.Control()
    ctrl.jarvis_system = MagicMock(name="jarvis_system")
    ctrl.jarvis_system.Text_To_Text = AsyncMock(name="Text_To_Text")
    ctrl.jarvis_system.Image_To_Text = AsyncMock(name="Image_To_Text")
    ctrl.jarvis_system.Video_To_Text = AsyncMock(name="Video_To_Text")
    ctrl.menager_system = MagicMock(name="menager_system")
    return ctrl


@pytest.fixture(autouse=True)
def sound_length_zero():
    """``mixer.Sound(...).get_length()`` -> 0.0 (alimenta time.sleep do som)."""
    control_mod.mixer.Sound.return_value.get_length.return_value = 0.0
    yield


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


# ---------------------------------------------------------------------------
# 1. __init__
# ---------------------------------------------------------------------------


class TestInit:
    """Estado inicial e efeitos colaterais do construtor."""

    def test_estado_inicial_desligado(self, control_instance):
        """ACTION desligado e nenhuma gravacao em curso no inicio."""
        assert control_instance.ACTION is False
        assert control_instance.is_recording() is False

    def test_mixer_init_chamado_na_construcao(self):
        """O servico de audio do pygame deve ser inicializado no __init__."""
        control_mod.mixer.init.reset_mock()
        control_mod.Control()
        control_mod.mixer.init.assert_called_once()

    def test_caminhos_de_som_apontam_para_wav_de_check(self, control_instance):
        """Todos os sons de confirmacao sao .wav dentro de audios_check/."""
        sons = [
            control_instance.photo_take_sound,
            control_instance.audio_start_sound,
            control_instance.video_start_sound,
            control_instance.video_end_sound,
        ]
        for caminho in sons:
            assert caminho.startswith("audios_check/")
            assert caminho.endswith(".wav")
        assert len(set(sons)) == 4

    def test_subsistemas_jarvis_e_manager_instanciados(self):
        """jarvis_system e menager_system existem apos a construcao."""
        ctrl = control_mod.Control()
        assert ctrl.jarvis_system is not None
        assert ctrl.menager_system is not None


# ---------------------------------------------------------------------------
# 2. toggle_recording / is_recording (Event substitui a antiga flag Control_Video)
# ---------------------------------------------------------------------------


class TestToggleRecording:
    """Estado de gravacao via threading.Event."""

    def test_toggle_liga_e_desliga(self, control_instance):
        """toggle alterna o Event e o retorno reflete o novo estado."""
        assert control_instance.is_recording() is False
        assert control_instance.toggle_recording() is True  # passou a gravar
        assert control_instance.is_recording() is True
        assert control_instance.toggle_recording() is False  # parou
        assert control_instance.is_recording() is False


# ---------------------------------------------------------------------------
# 3. play_confirmation_sound (agora sincrono)
# ---------------------------------------------------------------------------


class TestPlayConfirmationSound:
    """Reproducao sincrona de som de confirmacao."""

    def test_toca_e_para_o_som(self, control_instance):
        """play() e stop() sao chamados; get_length alimenta o sleep."""
        sound_obj = MagicMock(name="sound")
        sound_obj.get_length.return_value = 0.0
        with patch.object(control_mod.mixer, "Sound", return_value=sound_obj) as mk_sound:
            control_instance.play_confirmation_sound("audios_check/x.wav")

        mk_sound.assert_called_once_with("audios_check/x.wav")
        sound_obj.play.assert_called_once()
        sound_obj.get_length.assert_called_once()
        sound_obj.stop.assert_called_once()


# ---------------------------------------------------------------------------
# 4. Capture_Photo
# ---------------------------------------------------------------------------


class TestCapturePhoto:
    """Captura de foto: grava o arquivo, dispara upload e retorna o caminho."""

    def test_grava_jpg_com_timestamp_e_agenda_upload(self, control_instance, fake_frame):
        """imwrite recebe midia/<timestamp>.jpg; upload e agendado; retorna o caminho."""
        executor = MagicMock(name="executor")
        with (
            patch.object(control_mod, "cv2") as mk_cv2,
            patch.object(control_mod.time, "strftime", return_value="20260627_120000"),
        ):
            caminho = control_instance.Capture_Photo(fake_frame, executor)

        esperado = "midia/20260627_120000.jpg"
        assert caminho == esperado
        mk_cv2.imwrite.assert_called_once_with(esperado, fake_frame)
        executor.submit.assert_called_once_with(
            control_instance.menager_system.uploadMidia, esperado
        )

    def test_toca_som_de_foto(self, control_instance, fake_frame):
        """O som de confirmacao usado e o photo_take_sound (chamada sincrona)."""
        executor = MagicMock(name="executor")
        with (
            patch.object(control_mod, "cv2"),
            patch.object(control_instance, "play_confirmation_sound") as mk_play,
        ):
            control_instance.Capture_Photo(fake_frame, executor)
        mk_play.assert_called_once_with(control_instance.photo_take_sound)


# ---------------------------------------------------------------------------
# 5. Capture_Video (controlado pelo Event _recording)
# ---------------------------------------------------------------------------


class TestCaptureVideo:
    """Gravacao de video controlada por ``_recording`` (threading.Event)."""

    def test_sem_gravar_nao_entra_no_loop_mas_finaliza(self, control_instance):
        """_recording desligado: o while nao roda; VideoWriter criado e released."""
        cap = MagicMock(name="cap")
        executor = MagicMock(name="executor")
        out = MagicMock(name="out")
        with (
            patch.object(control_mod, "cv2") as mk_cv2,
            patch.object(control_mod.time, "strftime", return_value="20260627_120000"),
        ):
            mk_cv2.VideoWriter.return_value = out
            caminho = control_instance.Capture_Video(cap, executor)

        esperado = "midia/20260627_120000.avi"
        assert caminho == esperado
        mk_cv2.VideoWriter.assert_called_once()
        out.release.assert_called_once()
        out.write.assert_not_called()
        cap.read.assert_not_called()
        executor.submit.assert_called_once_with(
            control_instance.menager_system.uploadMidia, esperado
        )

    def test_uma_iteracao_grava_um_frame(self, control_instance):
        """Com _recording ligado e desligado no 1o read, grava exatamente 1 frame."""
        cap = MagicMock(name="cap")
        executor = MagicMock(name="executor")
        out = MagicMock(name="out")
        frame_obj = MagicMock(name="frame")

        control_instance._recording.set()

        def read_then_stop():
            # desliga apos a 1a leitura -> o while encerra na proxima checagem
            control_instance._recording.clear()
            return True, frame_obj

        cap.read.side_effect = read_then_stop

        with (
            patch.object(control_mod, "cv2") as mk_cv2,
            patch.object(control_mod.time, "strftime", return_value="20260627_120000"),
            patch.object(control_mod.time, "sleep"),
        ):
            mk_cv2.VideoWriter.return_value = out
            caminho = control_instance.Capture_Video(cap, executor)

        assert caminho == "midia/20260627_120000.avi"
        cap.read.assert_called_once()
        out.write.assert_called_once_with(frame_obj)
        out.release.assert_called_once()

    def test_read_sem_sucesso_encerra_gravacao(self, control_instance):
        """Se cap.read() falha (status False), a gravacao para sem escrever frame."""
        cap = MagicMock(name="cap")
        executor = MagicMock(name="executor")
        out = MagicMock(name="out")

        control_instance._recording.set()
        cap.read.return_value = (False, None)  # camera falhou

        with (
            patch.object(control_mod, "cv2") as mk_cv2,
            patch.object(control_mod.time, "strftime", return_value="20260627_120000"),
            patch.object(control_mod.time, "sleep"),
        ):
            mk_cv2.VideoWriter.return_value = out
            control_instance.Capture_Video(cap, executor)

        cap.read.assert_called_once()
        out.write.assert_not_called()
        out.release.assert_called_once()


# ---------------------------------------------------------------------------
# 6. Capture_Audio (retorna None em qualquer falha)
# ---------------------------------------------------------------------------


class TestCaptureAudio:
    """Transcricao de voz e tratamento de erros do reconhecimento."""

    @pytest.fixture
    def recognizer(self):
        """Recognizer falso configuravel; substitui sr.Recognizer no modulo control."""
        rec = MagicMock(name="recognizer")
        with (
            patch.object(control_mod.sr, "Recognizer", return_value=rec),
            patch.object(control_mod.sr, "Microphone") as mk_mic,
        ):
            mk_mic.return_value.__enter__.return_value = MagicMock(name="source")
            yield rec

    def test_retorno_inclui_texto_reconhecido(self, control_instance, recognizer):
        """Happy path: o texto do recognize_google e retornado e ACTION fica True."""
        recognizer.recognize_google.return_value = "ola jarvis"
        executor = _ImmediateExecutor()

        resultado = control_instance.Capture_Audio(executor)

        assert resultado == "ola jarvis"
        assert control_instance.ACTION is True
        recognizer.recognize_google.assert_called_once()
        assert recognizer.recognize_google.call_args.kwargs.get("language") == "pt-BR"

    def test_unknown_value_error_retorna_none(self, control_instance, recognizer):
        """UnknownValueError (audio nao compreendido) -> None (sem pergunta)."""
        recognizer.recognize_google.side_effect = control_mod.sr.UnknownValueError()
        executor = _ImmediateExecutor()

        assert control_instance.Capture_Audio(executor) is None

    def test_request_error_retorna_none(self, control_instance, recognizer):
        """RequestError (falha de rede) -> None."""
        recognizer.recognize_google.side_effect = control_mod.sr.RequestError()
        executor = _ImmediateExecutor()

        assert control_instance.Capture_Audio(executor) is None

    def test_excecao_generica_retorna_none(self, control_instance, recognizer):
        """Qualquer outra excecao tambem vira None (nao quebra o fluxo)."""
        recognizer.recognize_google.side_effect = ValueError("boom")
        executor = _ImmediateExecutor()

        assert control_instance.Capture_Audio(executor) is None

    def test_texto_vazio_retorna_none(self, control_instance, recognizer):
        """String vazia do reconhecedor vira None (sem pergunta valida)."""
        recognizer.recognize_google.return_value = ""
        executor = _ImmediateExecutor()

        assert control_instance.Capture_Audio(executor) is None

    def test_configura_parametros_do_microfone(self, control_instance, recognizer):
        """Os parametros de calibracao do recognizer sao ajustados antes de ouvir."""
        recognizer.recognize_google.return_value = "ok"
        executor = _ImmediateExecutor()

        control_instance.Capture_Audio(executor)

        assert recognizer.pause_threshold == 0.8
        assert recognizer.dynamic_energy_threshold is False
        assert recognizer.energy_threshold == 300


# ---------------------------------------------------------------------------
# 7. Fluxos que orquestram o Jarvis
# ---------------------------------------------------------------------------


class TestAudioToAudio:
    """Audio_to_Audio: voz -> Gemini (texto)."""

    def test_chama_text_to_text_e_zera_action(self, control_instance):
        """O prompt transcrito vai para Text_To_Text e ACTION volta a False."""
        executor = MagicMock(name="executor")
        with patch.object(control_instance, "Capture_Audio", return_value="qual a previsao?"):
            control_instance.Audio_to_Audio(executor)

        control_instance.jarvis_system.Text_To_Text.assert_awaited_once_with("qual a previsao?")
        assert control_instance.ACTION is False

    def test_chama_capture_audio_com_executor(self, control_instance):
        """A captura de audio e feita passando o executor."""
        executor = MagicMock(name="executor")
        with patch.object(control_instance, "Capture_Audio", return_value="oi") as mk_audio:
            control_instance.Audio_to_Audio(executor)

        mk_audio.assert_called_once_with(executor)

    def test_prompt_vazio_nao_consulta_jarvis(self, control_instance):
        """Sem pergunta valida (None), Text_To_Text NAO e chamado."""
        executor = MagicMock(name="executor")
        with patch.object(control_instance, "Capture_Audio", return_value=None):
            control_instance.Audio_to_Audio(executor)

        control_instance.jarvis_system.Text_To_Text.assert_not_awaited()
        assert control_instance.ACTION is False


class TestImageAudio:
    """Image_Audio: foto + voz -> Gemini (imagem+texto)."""

    def test_passa_caminho_da_foto_e_prompt(self, control_instance):
        """Image_To_Text recebe (image_path, prompt) e ACTION volta a False."""
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/foto.jpg")  # Capture_Photo
        with patch.object(control_instance, "Capture_Audio", return_value="o que e isso?"):
            control_instance.Image_Audio(MagicMock(name="frame"), executor)

        control_instance.jarvis_system.Image_To_Text.assert_awaited_once_with(
            "midia/foto.jpg", "o que e isso?"
        )
        assert control_instance.ACTION is False

    def test_prompt_vazio_nao_consulta_jarvis(self, control_instance):
        """Sem pergunta valida, Image_To_Text NAO e chamado."""
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/foto.jpg")
        with patch.object(control_instance, "Capture_Audio", return_value=None):
            control_instance.Image_Audio(MagicMock(name="frame"), executor)

        control_instance.jarvis_system.Image_To_Text.assert_not_awaited()
        assert control_instance.ACTION is False


class TestVideoAudio:
    """Video_Audio: grava video + voz -> Gemini (video+texto).

    A gravacao e iniciada (Event set), a fala capturada (~5s) e a gravacao
    encerrada (Event clear) antes de consultar o Gemini. O bug historico (chamar
    ``Capture_Audio`` sem o argumento ``executor``) foi corrigido na Onda 1.
    """

    def test_passa_caminho_do_video_e_prompt(self, control_instance):
        """Video_To_Text recebe (video_path, prompt) e ACTION volta a False."""
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/video.avi")  # Capture_Video
        with patch.object(control_instance, "Capture_Audio", return_value="descreva a cena"):
            control_instance.Video_Audio(MagicMock(name="cap"), executor)

        control_instance.jarvis_system.Video_To_Text.assert_awaited_once_with(
            "midia/video.avi", "descreva a cena"
        )
        assert control_instance.ACTION is False

    def test_capture_audio_recebe_executor(self, control_instance):
        """Regressao do bug corrigido: Capture_Audio e chamado COM o executor."""
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/v.avi")
        with patch.object(control_instance, "Capture_Audio", return_value="x") as mk_audio:
            control_instance.Video_Audio(MagicMock(name="cap"), executor)

        mk_audio.assert_called_once_with(executor)

    def test_encerra_gravacao_ao_final(self, control_instance):
        """Ao fim de Video_Audio a gravacao esta encerrada (Event clear)."""
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("midia/v.avi")
        with patch.object(control_instance, "Capture_Audio", return_value="x"):
            control_instance.Video_Audio(MagicMock(name="cap"), executor)

        assert control_instance.is_recording() is False


# ---------------------------------------------------------------------------
# 8. Recycle_midia: bug NAO corrigido na Onda 1 (codigo morto, deferido)
# ---------------------------------------------------------------------------


class TestRecycleMidia:
    """Recycle_midia foi declarado sem ``self`` (control.py). Deferido."""

    @pytest.mark.xfail(
        reason="Recycle_midia(midia_path) declarado sem self -> chamar via instancia "
        "passa o self como midia_path (deferido para onda futura)",
        strict=False,
    )
    def test_bug_recycle_midia_sem_self(self, control_instance):
        """Chamar pela instancia injeta self como 1o arg, deslocando midia_path."""
        with patch.object(control_mod, "os") as mk_os:
            control_instance.Recycle_midia("midia/foto.jpg")
            mk_os.remove.assert_called_once_with("midia/foto.jpg")

    def test_recycle_midia_chamada_diretamente_remove_arquivo(self):
        """Chamada como funcao da classe (sem instancia) funciona: remove o path."""
        with patch.object(control_mod, "os") as mk_os:
            control_mod.Control.Recycle_midia("midia/foto.jpg")
            mk_os.remove.assert_called_once_with("midia/foto.jpg")
