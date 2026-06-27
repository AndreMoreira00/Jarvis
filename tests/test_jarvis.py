"""Testes da classe ``Jarvis`` (cliente Gemini + TTS).

Foco: a NOSSA orquestracao/fluxo, nao a lib stubada. ``genai``
(google.generativeai) e ``edge_tts`` sao MagicMock injetados pelo conftest;
o polling de PROCESSING usa ``asyncio.sleep`` (monkeypatchado para nao
dormir). ``dotenv`` e real, mas ``load_dotenv()`` apenas le o ``.env`` local
(efeito colateral inofensivo nos testes).

Como os stubs de ``genai``/``edge_tts`` sao compartilhados em ``sys.modules``,
a fixture ``jarvis_factory`` reseta esses mocks e (re)configura o que precisa
ser ``await``-avel (``Communicate(...).save`` como AsyncMock) e o que precisa
devolver numero/string (``Sound.get_length`` -> float; ``response.text`` ->
str) antes de cada teste.
"""

from unittest.mock import AsyncMock, MagicMock, call

import pytest

import jarvis

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mixer():
    """Mixer falso (pygame.mixer) passado ao construtor do Jarvis.

    ``Sound`` retorna um objeto cujo ``get_length()`` e um float (vira
    ``asyncio.sleep(...)``, que exige numero) e cujo ``play``/``stop`` sao
    mocks inspecionaveis.
    """
    m = MagicMock(name="mixer")
    sound = m.Sound.return_value
    sound.get_length.return_value = 0.0
    return m


@pytest.fixture
def jarvis_factory(mixer):
    """Fabrica de instancias ``Jarvis`` com os stubs em estado limpo.

    Reseta ``genai`` e ``edge_tts`` (compartilhados via sys.modules) para que os
    asserts de "foi chamado" reflitam apenas o teste atual, e configura:
      - ``edge_tts.Communicate(...).save`` como AsyncMock (e await-ado);
      - ``model.generate_content(...).text`` como string default.
    Devolve ``(jarvis_obj, mixer)``.
    """
    jarvis.genai.reset_mock()
    jarvis.edge_tts.reset_mock()

    jarvis.edge_tts.Communicate.return_value.save = AsyncMock(name="save")

    obj = jarvis.Jarvis(mixer)
    obj.model.generate_content.return_value.text = "resposta padrao"
    return obj, mixer


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestInit:
    """Construcao do Jarvis: persona, voz, paths e bootstrap do Gemini."""

    def test_template_contem_jarvis_e_mestre(self, jarvis_factory):
        """A persona PT-BR deve mencionar 'Jarvis' e 'Mestre'."""
        obj, _ = jarvis_factory
        assert "Jarvis" in obj.template
        assert "Mestre" in obj.template

    def test_voice_e_antonio_neural(self, jarvis_factory):
        """A voz escolhida e a brasileira masculina pt-BR-AntonioNeural."""
        obj, _ = jarvis_factory
        assert obj.VOICE == "pt-BR-AntonioNeural"

    def test_path_file_termina_em_translate_mp3(self, jarvis_factory):
        """O audio de resposta e escrito/lido em response/translate.mp3."""
        obj, _ = jarvis_factory
        assert obj.PATH_FILE.endswith("translate.mp3")

    def test_mixer_guardado_na_instancia(self, jarvis_factory):
        """O mixer recebido no construtor fica acessivel em self.mixer."""
        obj, mixer = jarvis_factory
        assert obj.mixer is mixer

    def test_configura_gemini_com_api_key_e_modelo(self, jarvis_factory):
        """__init__ inicializa o Gemini: configure(api_key=...) + GenerativeModel."""
        obj, _ = jarvis_factory
        jarvis.genai.configure.assert_called_once_with(api_key=obj.API_KEY)
        jarvis.genai.GenerativeModel.assert_called_once_with(
            "gemini-2.0-flash-lite", system_instruction=obj.template
        )

    def test_model_e_o_generative_model_retornado(self, jarvis_factory):
        """self.model deve ser o objeto devolvido por genai.GenerativeModel(...)."""
        obj, _ = jarvis_factory
        assert obj.model is jarvis.genai.GenerativeModel.return_value


# ---------------------------------------------------------------------------
# Translate
# ---------------------------------------------------------------------------


class TestTranslate:
    """Limpeza de texto + sintese de voz (edge_tts)."""

    async def test_chama_communicate_com_voz_e_salva_no_path(self, jarvis_factory):
        """Translate usa edge_tts.Communicate(text, VOICE) e await save(PATH_FILE)."""
        obj, _ = jarvis_factory
        await obj.Translate("ola mestre")

        jarvis.edge_tts.Communicate.assert_called_once_with("ola mestre", obj.VOICE)
        jarvis.edge_tts.Communicate.return_value.save.assert_awaited_once_with(obj.PATH_FILE)

    @pytest.mark.parametrize(
        "bruto,esperado",
        [
            ("\tola", "ola"),  # tab vira espaco e strip remove
            ("*negrito*", "negrito"),  # asteriscos viram espaco + strip
            ("a​b", "a b"),  # zero-width space -> espaco
            ("a‌b", "a b"),  # zero-width non-joiner -> espaco
            ("a‍b", "a b"),  # zero-width joiner -> espaco
            ("﻿ola", "ola"),  # BOM/zero-width no-break -> espaco + strip
            ("ola  mestre", "ola mestre"),  # duplo-espaco vira espaco unico
            ("  ola mestre  ", "ola mestre"),  # strip nas pontas
        ],
    )
    async def test_normaliza_caracteres_especiais(self, jarvis_factory, bruto, esperado):
        """Caracteres de controle/zero-width/asterisco viram espaco e o texto e stripado."""
        obj, _ = jarvis_factory
        await obj.Translate(bruto)

        texto_passado = jarvis.edge_tts.Communicate.call_args.args[0]
        assert texto_passado == esperado

    async def test_retorna_none(self, jarvis_factory):
        """Translate nao tem valor de retorno util (-> None)."""
        obj, _ = jarvis_factory
        assert await obj.Translate("texto") is None


# ---------------------------------------------------------------------------
# Text_To_Text
# ---------------------------------------------------------------------------


class TestTextToText:
    """Pergunta em texto -> Gemini -> fala."""

    async def test_fluxo_completo_gera_traduz_e_toca(self, jarvis_factory):
        """generate_content(prompt) -> Translate(text) -> Sound.play()/stop()."""
        obj, mixer = jarvis_factory
        obj.model.generate_content.return_value.text = "resposta"
        obj.Translate = AsyncMock(name="Translate")  # isola a sintese de voz

        await obj.Text_To_Text("qual a hora?")

        obj.model.generate_content.assert_called_once_with("qual a hora?")
        obj.Translate.assert_awaited_once_with("resposta")
        mixer.Sound.assert_called_once_with(obj.PATH_FILE)
        mixer.Sound.return_value.play.assert_called_once_with()
        mixer.Sound.return_value.stop.assert_called_once_with()

    async def test_usa_get_length_para_o_sleep(self, jarvis_factory, monkeypatch):
        """A duracao do sleep vem de Sound.get_length() (passado a asyncio.sleep)."""
        obj, mixer = jarvis_factory
        mixer.Sound.return_value.get_length.return_value = 1.5
        obj.Translate = AsyncMock()

        dorme = AsyncMock(name="asyncio.sleep")
        monkeypatch.setattr(jarvis.asyncio, "sleep", dorme)

        await obj.Text_To_Text("oi")

        mixer.Sound.return_value.get_length.assert_called_once_with()
        dorme.assert_awaited_once_with(1.5)


# ---------------------------------------------------------------------------
# Image_To_Text
# ---------------------------------------------------------------------------


class TestImageToText:
    """Imagem + pergunta -> Gemini -> fala."""

    async def test_envia_imagem_jpeg_e_prompt(self, jarvis_factory, tmp_path):
        """generate_content recebe [dict(image/jpeg, bytes do arquivo), prompt]."""
        obj, mixer = jarvis_factory
        obj.Translate = AsyncMock()

        img = tmp_path / "foto.jpg"
        conteudo = b"\xff\xd8\xff\xe0bytes-de-imagem"
        img.write_bytes(conteudo)

        await obj.Image_To_Text(str(img), "o que e isso?")

        args = obj.model.generate_content.call_args.args[0]
        assert isinstance(args, list) and len(args) == 2
        bloco_img, prompt = args
        assert bloco_img == {"mime_type": "image/jpeg", "data": conteudo}
        assert prompt == "o que e isso?"

    async def test_traduz_resposta_e_toca_audio(self, jarvis_factory, tmp_path):
        """A resposta do Gemini e falada (Translate + Sound.play/stop)."""
        obj, mixer = jarvis_factory
        obj.model.generate_content.return_value.text = "um gato"
        obj.Translate = AsyncMock()

        img = tmp_path / "foto.jpg"
        img.write_bytes(b"dados")

        await obj.Image_To_Text(str(img), "descreva")

        obj.Translate.assert_awaited_once_with("um gato")
        mixer.Sound.assert_called_once_with(obj.PATH_FILE)
        mixer.Sound.return_value.play.assert_called_once_with()
        mixer.Sound.return_value.stop.assert_called_once_with()


# ---------------------------------------------------------------------------
# Video_To_Text
# ---------------------------------------------------------------------------


def _fake_video_file(states):
    """Cria um mock de video_file cujo .state.name percorre ``states`` a cada leitura.

    O ultimo estado em ``states`` "gruda" (repete) para chamadas subsequentes,
    imitando o objeto retornado por upload_file/get_file ao longo do while.
    """
    vf = MagicMock(name="video_file")
    vf.name = "files/abc123"
    state_iter = iter(states)
    ultimo = {"v": states[-1]}

    def _name():
        try:
            ultimo["v"] = next(state_iter)
        except StopIteration:
            pass
        return ultimo["v"]

    type(vf.state).name = property(lambda self: _name())
    return vf


class TestVideoToText:
    """Upload de video -> espera processamento -> Gemini -> fala -> limpa cache."""

    @pytest.fixture(autouse=True)
    def _no_sleep(self, monkeypatch):
        """Nao dormir de verdade no polling de PROCESSING (agora via asyncio.sleep)."""
        monkeypatch.setattr(jarvis.asyncio, "sleep", AsyncMock(name="sleep"))

    async def test_video_ja_ativo_segue_direto(self, jarvis_factory):
        """Estado ACTIVE de cara: nao entra no while, gera resposta e fala."""
        obj, mixer = jarvis_factory
        obj.Translate = AsyncMock()
        obj.Delete_Cahche_Files = MagicMock(name="Delete_Cahche_Files")
        obj.model.generate_content.return_value.text = "video descrito"

        vf = MagicMock(name="video_file")
        vf.name = "files/v1"
        vf.state.name = "ACTIVE"
        jarvis.genai.upload_file.return_value = vf

        await obj.Video_To_Text("/caminho/video.mp4", "resuma")

        jarvis.genai.upload_file.assert_called_once_with(path="/caminho/video.mp4")
        # generate_content com [video_file, prompt] + timeout de 600s
        chamada = obj.model.generate_content.call_args
        assert chamada.args[0] == [vf, "resuma"]
        assert chamada.kwargs == {"request_options": {"timeout": 600}}
        obj.Translate.assert_awaited_once_with("video descrito")
        mixer.Sound.return_value.play.assert_called_once_with()
        mixer.Sound.return_value.stop.assert_called_once_with()
        obj.Delete_Cahche_Files.assert_called_once_with()

    async def test_processing_ate_active_faz_poll(self, jarvis_factory):
        """PROCESSING->PROCESSING->ACTIVE: re-busca via get_file ate ficar pronto."""
        obj, _ = jarvis_factory
        obj.Translate = AsyncMock()
        obj.Delete_Cahche_Files = MagicMock()

        # upload retorna PROCESSING; cada get_file avanca o estado.
        upload_vf = _fake_video_file(["PROCESSING", "PROCESSING"])
        jarvis.genai.upload_file.return_value = upload_vf
        # get_file devolve um objeto cujo state vira ACTIVE na 1a leitura.
        active_vf = _fake_video_file(["ACTIVE"])
        jarvis.genai.get_file.return_value = active_vf

        await obj.Video_To_Text("/v.mp4", "p")

        # Entrou no loop: get_file foi consultado pelo menos uma vez.
        assert jarvis.genai.get_file.call_count >= 1
        jarvis.genai.get_file.assert_called_with(upload_vf.name)
        obj.model.generate_content.assert_called_once()
        obj.Delete_Cahche_Files.assert_called_once_with()

    async def test_estado_failed_levanta_valueerror(self, jarvis_factory):
        """Estado FAILED apos o processamento deve abortar com ValueError."""
        obj, _ = jarvis_factory
        obj.Translate = AsyncMock()
        obj.Delete_Cahche_Files = MagicMock()

        vf = MagicMock(name="video_file")
        vf.name = "files/bad"
        vf.state.name = "FAILED"
        jarvis.genai.upload_file.return_value = vf

        with pytest.raises(ValueError, match="FAILED"):
            await obj.Video_To_Text("/ruim.mp4", "p")

        # Falhou antes de gerar conteudo e de limpar cache.
        obj.model.generate_content.assert_not_called()
        obj.Delete_Cahche_Files.assert_not_called()


# ---------------------------------------------------------------------------
# Delete_Cahche_Files
# ---------------------------------------------------------------------------


class TestDeleteCacheFiles:
    """Limpeza dos arquivos que ficam na memoria do Gemini."""

    def test_deleta_cada_arquivo_listado(self, jarvis_factory):
        """Para cada item de list_files, get_file(nome).delete() e chamado."""
        obj, _ = jarvis_factory

        f1 = MagicMock(name="f1")
        f1.name = "files/aaa"
        f2 = MagicMock(name="f2")
        f2.name = "files/bbb"
        jarvis.genai.list_files.return_value = [f1, f2]

        # get_file devolve um mock distinto por nome para checar .delete() em cada.
        arquivos = {"files/aaa": MagicMock(name="m1"), "files/bbb": MagicMock(name="m2")}
        jarvis.genai.get_file.side_effect = lambda nome: arquivos[nome]

        obj.Delete_Cahche_Files()

        jarvis.genai.get_file.assert_has_calls(
            [call("files/aaa"), call("files/bbb")], any_order=True
        )
        for m in arquivos.values():
            m.delete.assert_called_once_with()

    def test_lista_vazia_nao_faz_nada(self, jarvis_factory):
        """Sem arquivos na memoria, nenhum get_file/delete e disparado."""
        obj, _ = jarvis_factory
        jarvis.genai.get_file.reset_mock()
        jarvis.genai.get_file.side_effect = None
        jarvis.genai.list_files.return_value = []

        obj.Delete_Cahche_Files()

        jarvis.genai.get_file.assert_not_called()
