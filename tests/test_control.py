"""Testes da classe ``Control`` (control.py): orquestracao das acoes do Jarvis.

Foco: testar O NOSSO codigo (fluxo de captura, encadeamento de futures,
controle da trava ``ACTION``, nomes de arquivo por timestamp e tratamento de
erros do reconhecimento de voz), nao as libs stubadas (cv2, pygame, sr).

Estrategia de isolamento da rede/IA:
- Apos criar ``Control()``, substituimos ``jarvis_system`` e ``menager_system``
  por mocks. Os metodos do jarvis sao corrotinas (chamados via ``asyncio.run``),
  entao usamos ``AsyncMock``; o manager so recebe ``executor.submit(...)`` e pode
  ser ``MagicMock``.
- ``mixer`` vem do stub MagicMock do pygame. ``Sound(...).get_length()`` por
  padrao devolveria um MagicMock (que quebraria ``asyncio.sleep``), entao
  configuramos ``return_value`` para um numero em cada teste que toca som.
"""

from concurrent.futures import Future
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import control as control_mod


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def _make_future(value):
    """Cria um ``concurrent.futures.Future`` ja resolvido com ``value``.

    Util para simular o resultado de ``executor.submit(...).result()`` sem
    rodar nada em outra thread.
    """
    fut = Future()
    fut.set_result(value)
    return fut


@pytest.fixture
def control_instance():
    """Instancia de ``Control`` com jarvis e manager mockados.

    ``mixer.init()`` e ``mixer.Sound`` vem do stub MagicMock do pygame, entao a
    construcao nao toca em hardware. Trocamos as dependencias internas por mocks
    para isolar a orquestracao da rede/IA.
    """
    ctrl = control_mod.Control()
    # jarvis: metodos async -> AsyncMock para casar com asyncio.run(...)
    ctrl.jarvis_system = MagicMock(name="jarvis_system")
    ctrl.jarvis_system.Text_To_Text = AsyncMock(name="Text_To_Text")
    ctrl.jarvis_system.Image_To_Text = AsyncMock(name="Image_To_Text")
    ctrl.jarvis_system.Video_To_Text = AsyncMock(name="Video_To_Text")
    # manager: so recebe submit(uploadMidia, ...), nao precisa ser async
    ctrl.menager_system = MagicMock(name="menager_system")
    return ctrl


@pytest.fixture(autouse=True)
def sound_length_zero():
    """Garante que ``mixer.Sound(...).get_length()`` devolva numero (0.0).

    O stub do pygame e MagicMock; sem isso ``await asyncio.sleep(get_length())``
    receberia um MagicMock e estouraria. Configuramos no objeto ``mixer`` que o
    modulo ``control`` realmente usa (``from pygame import mixer``).
    """
    control_mod.mixer.Sound.return_value.get_length.return_value = 0.0
    yield


class _ImmediateExecutor:
    """Executor falso: roda ``fn`` na hora e devolve um Future ja resolvido.

    Reproduz o contrato de ``ThreadPoolExecutor.submit(...).result()`` sem usar
    threads, deixando os testes deterministicos.
    """

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

    def test_flags_de_controle_iniciam_false(self, control_instance):
        """ACTION e Control_Video comecam desligadas (nenhuma acao em curso)."""
        assert control_instance.ACTION is False
        assert control_instance.Control_Video is False

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
        # nomes nao podem colidir entre si
        assert len(set(sons)) == 4

    def test_subsistemas_jarvis_e_manager_instanciados(self):
        """jarvis_system e menager_system existem apos a construcao."""
        ctrl = control_mod.Control()
        assert ctrl.jarvis_system is not None
        assert ctrl.menager_system is not None


# ---------------------------------------------------------------------------
# 2. play_confirmation_sound (async)
# ---------------------------------------------------------------------------

class TestPlayConfirmationSound:
    """Reproducao de som de confirmacao (corrotina)."""

    async def test_toca_e_para_o_som(self, control_instance):
        """play() e stop() sao chamados; get_length alimenta o sleep."""
        sound_obj = MagicMock(name="sound")
        sound_obj.get_length.return_value = 0.0
        with patch.object(control_mod.mixer, "Sound", return_value=sound_obj) as mk_sound:
            await control_instance.play_confirmation_sound("audios_check/x.wav")

        mk_sound.assert_called_once_with("audios_check/x.wav")
        sound_obj.play.assert_called_once()
        sound_obj.get_length.assert_called_once()
        sound_obj.stop.assert_called_once()


# ---------------------------------------------------------------------------
# 3. Capture_Photo
# ---------------------------------------------------------------------------

class TestCapturePhoto:
    """Captura de foto: grava o arquivo, dispara upload e retorna o caminho."""

    def test_grava_jpg_com_timestamp_e_agenda_upload(self, control_instance, fake_frame):
        """imwrite recebe midia/<timestamp>.jpg; upload e agendado; retorna o caminho."""
        executor = MagicMock(name="executor")
        with patch.object(control_mod, "cv2") as mk_cv2, \
             patch.object(control_mod.time, "strftime", return_value="20260627_120000"):
            caminho = control_instance.Capture_Photo(fake_frame, executor)

        esperado = "midia/20260627_120000.jpg"
        assert caminho == esperado
        mk_cv2.imwrite.assert_called_once_with(esperado, fake_frame)
        executor.submit.assert_called_once_with(
            control_instance.menager_system.uploadMidia, esperado
        )

    def test_toca_som_de_foto(self, control_instance, fake_frame):
        """O som de confirmacao usado e o photo_take_sound."""
        executor = MagicMock(name="executor")
        with patch.object(control_mod, "cv2"), \
             patch.object(control_instance, "play_confirmation_sound", new=AsyncMock()) as mk_play:
            control_instance.Capture_Photo(fake_frame, executor)
        mk_play.assert_awaited_once_with(control_instance.photo_take_sound)


# ---------------------------------------------------------------------------
# 4. Capture_Video
# ---------------------------------------------------------------------------

class TestCaptureVideo:
    """Gravacao de video controlada por Control_Video."""

    def test_sem_gravar_nao_entra_no_loop_mas_finaliza(self, control_instance):
        """Control_Video=False: o while nao roda; VideoWriter criado e released; retorna .avi."""
        cap = MagicMock(name="cap")
        executor = MagicMock(name="executor")
        out = MagicMock(name="out")
        control_instance.Control_Video = False
        with patch.object(control_mod, "cv2") as mk_cv2, \
             patch.object(control_mod.time, "strftime", return_value="20260627_120000"):
            mk_cv2.VideoWriter.return_value = out
            caminho = control_instance.Capture_Video(cap, executor)

        esperado = "midia/20260627_120000.avi"
        assert caminho == esperado
        mk_cv2.VideoWriter.assert_called_once()
        out.release.assert_called_once()
        # while nao executou -> nenhum frame escrito e nenhum read
        out.write.assert_not_called()
        cap.read.assert_not_called()
        executor.submit.assert_called_once_with(
            control_instance.menager_system.uploadMidia, esperado
        )

    def test_uma_iteracao_grava_um_frame(self, control_instance):
        """Com Control_Video ligado e desligado no 1o read, grava exatamente 1 frame."""
        cap = MagicMock(name="cap")
        executor = MagicMock(name="executor")
        out = MagicMock(name="out")
        frame_obj = MagicMock(name="frame")

        control_instance.Control_Video = True

        def read_then_stop():
            # desliga apos a 1a leitura -> o while encerra na proxima checagem
            control_instance.Control_Video = False
            return True, frame_obj

        cap.read.side_effect = read_then_stop

        with patch.object(control_mod, "cv2") as mk_cv2, \
             patch.object(control_mod.time, "strftime", return_value="20260627_120000"):
            mk_cv2.VideoWriter.return_value = out
            caminho = control_instance.Capture_Video(cap, executor)

        assert caminho == "midia/20260627_120000.avi"
        cap.read.assert_called_once()
        out.write.assert_called_once_with(frame_obj)
        out.release.assert_called_once()


# ---------------------------------------------------------------------------
# 5. Capture_Audio
# ---------------------------------------------------------------------------

class TestCaptureAudio:
    """Transcricao de voz e tratamento de erros do reconhecimento."""

    @pytest.fixture
    def recognizer(self):
        """Recognizer falso configuravel; substitui sr.Recognizer no modulo control."""
        rec = MagicMock(name="recognizer")
        with patch.object(control_mod.sr, "Recognizer", return_value=rec), \
             patch.object(control_mod.sr, "Microphone") as mk_mic:
            # `with sr.Microphone() as source` -> entrega um source qualquer
            mk_mic.return_value.__enter__.return_value = MagicMock(name="source")
            yield rec

    def test_retorno_inclui_texto_reconhecido(self, control_instance, recognizer):
        """Happy path: o texto do recognize_google compoe o retorno e ACTION fica True."""
        recognizer.recognize_google.return_value = "ola jarvis"
        executor = _ImmediateExecutor()

        resultado = control_instance.Capture_Audio(executor)

        assert resultado == "ola jarvis"
        assert control_instance.ACTION is True
        recognizer.recognize_google.assert_called_once()
        # language pt-BR deve ser passado ao reconhecedor
        assert recognizer.recognize_google.call_args.kwargs.get("language") == "pt-BR"

    def test_unknown_value_error_retorna_sem_pergunta(self, control_instance, recognizer):
        """UnknownValueError (audio nao compreendido) -> 'Sem Pergunta'."""
        recognizer.recognize_google.side_effect = control_mod.sr.UnknownValueError()
        executor = _ImmediateExecutor()

        assert control_instance.Capture_Audio(executor) == "Sem Pergunta"

    def test_request_error_retorna_erro_de_conexao(self, control_instance, recognizer):
        """RequestError (falha de rede no servico) -> 'Erro de conexão'."""
        recognizer.recognize_google.side_effect = control_mod.sr.RequestError()
        executor = _ImmediateExecutor()

        assert control_instance.Capture_Audio(executor) == "Erro de conexão"

    def test_excecao_generica_retorna_mensagem_inesperada(self, control_instance, recognizer):
        """Qualquer outra excecao vira 'Erro inesperado: <msg>'."""
        recognizer.recognize_google.side_effect = ValueError("boom")
        executor = _ImmediateExecutor()

        assert control_instance.Capture_Audio(executor) == "Erro inesperado: boom"

    def test_configura_parametros_do_microfone(self, control_instance, recognizer):
        """Os parametros de calibracao do recognizer sao ajustados antes de ouvir."""
        recognizer.recognize_google.return_value = "ok"
        executor = _ImmediateExecutor()

        control_instance.Capture_Audio(executor)

        assert recognizer.pause_threshold == 0.8
        assert recognizer.dynamic_energy_threshold is False
        assert recognizer.energy_threshold == 300


# ---------------------------------------------------------------------------
# 6. Fluxos que orquestram o Jarvis
# ---------------------------------------------------------------------------

class TestAudioToAudio:
    """Audio_to_Audio: voz -> Gemini (texto)."""

    def test_chama_text_to_text_e_zera_action(self, control_instance):
        """O prompt transcrito vai para Text_To_Text e ACTION volta a False."""
        executor = MagicMock(name="executor")
        # 1a chamada: Capture_Audio -> prompt; usamos um Future pronto
        executor.submit.return_value = _make_future("qual a previsao?")

        control_instance.Audio_to_Audio(executor)

        control_instance.jarvis_system.Text_To_Text.assert_awaited_once_with("qual a previsao?")
        assert control_instance.ACTION is False

    def test_submete_capture_audio_ao_executor(self, control_instance):
        """A captura de audio e delegada ao executor (Capture_Audio)."""
        executor = MagicMock(name="executor")
        executor.submit.return_value = _make_future("oi")

        control_instance.Audio_to_Audio(executor)

        executor.submit.assert_called_once_with(
            control_instance.Capture_Audio, executor
        )


class TestImageAudio:
    """Image_Audio: foto + voz -> Gemini (imagem+texto)."""

    def test_passa_caminho_da_foto_e_prompt(self, control_instance):
        """Image_To_Text recebe (image_path, prompt) e ACTION volta a False."""
        executor = MagicMock(name="executor")
        # ordem dos submits: Capture_Photo (path), Capture_Audio (prompt)
        executor.submit.side_effect = [
            _make_future("midia/foto.jpg"),
            _make_future("o que e isso?"),
        ]

        control_instance.Image_Audio(MagicMock(name="frame"), executor)

        control_instance.jarvis_system.Image_To_Text.assert_awaited_once_with(
            "midia/foto.jpg", "o que e isso?"
        )
        assert control_instance.ACTION is False


class TestVideoAudio:
    """Video_Audio: video + voz -> Gemini (video+texto).

    BUG conhecido (control.py:108): ``self.Capture_Audio`` e chamado SEM o
    argumento ``executor``, que e obrigatorio. Num executor REAL o future
    captura esse TypeError e ``future_audio.result()`` o re-lanca. Aqui usamos um
    executor MagicMock cujo ``submit`` NAO chama a funcao, justamente para
    contornar o bug e validar o resto do encadeamento. O comportamento real
    quebrado e coberto por ``test_bug_capture_audio_sem_executor`` (xfail).
    """

    def test_passa_caminho_do_video_e_prompt(self, control_instance):
        """Video_To_Text recebe (video_path, prompt) e ACTION volta a False."""
        executor = MagicMock(name="executor")
        executor.submit.side_effect = [
            _make_future("midia/video.avi"),
            _make_future("descreva a cena"),
        ]

        control_instance.Video_Audio(MagicMock(name="cap"), executor)

        control_instance.jarvis_system.Video_To_Text.assert_awaited_once_with(
            "midia/video.avi", "descreva a cena"
        )
        assert control_instance.ACTION is False

    @pytest.mark.xfail(
        reason="control.py:108 chama self.Capture_Audio sem o arg 'executor' obrigatorio",
        strict=False,
    )
    def test_bug_capture_audio_sem_executor(self, control_instance):
        """Documenta o bug: com executor REAL, a captura de audio estoura TypeError.

        Aqui o executor de fato executa a funcao submetida; como Video_Audio
        chama ``self.Capture_Audio`` sem ``executor``, o future resultante carrega
        o TypeError e ``.result()`` o re-lanca. Este teste deve falhar enquanto o
        bug existir (xfail nao-estrito).
        """
        executor = _ImmediateExecutor()

        # Capture_Video tocaria som e usaria cv2; isola para focar no bug do audio.
        with patch.object(control_instance, "Capture_Video", return_value="midia/v.avi"):
            control_instance.Video_Audio(MagicMock(name="cap"), executor)


# ---------------------------------------------------------------------------
# 7. Bug: Recycle_midia declarado sem self
# ---------------------------------------------------------------------------

class TestRecycleMidia:
    """Recycle_midia foi declarado sem ``self`` (control.py:30)."""

    @pytest.mark.xfail(
        reason="Recycle_midia(midia_path) declarado sem self -> chamar via instancia "
               "passa o self como midia_path",
        strict=False,
    )
    def test_bug_recycle_midia_sem_self(self, control_instance):
        """Chamar pela instancia injeta self como 1o arg, deslocando midia_path.

        ``ctrl.Recycle_midia('x')`` vira ``Recycle_midia(ctrl, 'x')`` -> excesso de
        argumentos (TypeError). Documenta a assinatura incorreta.
        """
        with patch.object(control_mod, "os") as mk_os:
            control_instance.Recycle_midia("midia/foto.jpg")
            mk_os.remove.assert_called_once_with("midia/foto.jpg")

    def test_recycle_midia_chamada_diretamente_remove_arquivo(self):
        """Chamada como funcao da classe (sem instancia) funciona: remove o path.

        Demonstra que a logica em si esta certa; o problema e so a falta de self.
        """
        with patch.object(control_mod, "os") as mk_os:
            control_mod.Control.Recycle_midia("midia/foto.jpg")
            mk_os.remove.assert_called_once_with("midia/foto.jpg")
