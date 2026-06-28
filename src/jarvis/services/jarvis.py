import asyncio  # Torna as funções assincronas
import pathlib  # Biblioteca que transforma os dados de imagem para serem enviados para o Gemini

import edge_tts  # Biblioteca para tranformar a resposta do Gemini na voz do Jarvis
import google.generativeai as genai  # API da Gemini

from jarvis.config import Config


class Jarvis:  # Classe do Jarvis
    def __init__(self, mixer, config: Config):  # Inicia as "caracteristicas" do Jarvis
        self.mixer = mixer
        self.config = config
        self.API_KEY = config.gemini_api_key  # Key de acesso a API Gemini (via Config)
        self.template = config.gemini_persona  # Persona PT-BR (system prompt do modelo)
        # Config model Genai
        genai.configure(
            api_key=self.API_KEY
        )  # Inicia os serviços da Gemini passando a Key de acesso
        self.model = genai.GenerativeModel(  # Configurando o Serviço
            config.gemini_model,
            system_instruction=self.template,  # Escolhendo o modelo do Gemini
        )
        # Config Voice
        self.VOICE = config.voice  # Voz do Jarvis (edge-tts)
        # Config Paths
        self.PATH_FILE = config.response_file  # Caminho do audio de resposta (grava/toca)

    # Delete Cahche Video
    # Função que apaga os arquivos salvos na memoria do Gemini. (É preciso para não sobrecarregar a memória)
    def delete_cache_files(self):
        for f in genai.list_files():  # Acesso a lista de arquivos salvos e deleta um por um
            myfile = genai.get_file(f.name)
            myfile.delete()

    # translate voice from Jarvis
    # Função que recebe a resposta do Gemini em texto e tranforma em audio com a voz do Jarvis
    async def translate(self, text) -> None:
        char_removidos = {
            "\t": " ",
            "*": " ",
            "\u200b": " ",
            "\u200c": " ",
            "\u200d": " ",
            "\ufeff": " ",
            "  ": " ",
        }

        for antigo, novo in char_removidos.items():
            text = text.replace(antigo, novo)

        text = text.strip()
        communicate = edge_tts.Communicate(text, self.VOICE)
        await communicate.save(self.PATH_FILE)

    # Response Text to Text
    # Função que recebe nossa pergunta e manda para Gemini, depois que ele retorna a resposta ela é transformada em audio
    async def text_to_text(self, prompt) -> None:
        response = self.model.generate_content(prompt)  # Salva a resposta da Gemini
        await self.translate(response.text)  # Aguarda a função de translate
        sound = self.mixer.Sound(self.PATH_FILE)
        sound.play()  # Execulta a resposta
        await asyncio.sleep(sound.get_length())
        sound.stop()

    # Response Image to Text
    async def image_to_text(self, image_path, prompt) -> None:
        response = self.model.generate_content(
            [
                {"mime_type": "image/jpeg", "data": pathlib.Path(f"{image_path}").read_bytes()},
                prompt,
            ]
        )  # Salva a resposta da Gemini
        await self.translate(response.text)  # Aguarda a função de translate
        sound = self.mixer.Sound(self.PATH_FILE)
        sound.play()  # Execulta a resposta
        await asyncio.sleep(sound.get_length())
        sound.stop()

    # Response Video to text
    async def video_to_text(self, video_path, prompt) -> None:
        video_file = genai.upload_file(path=video_path)  # Sobe o video na memoria da Gemini
        backoff = 1
        while video_file.state.name == "PROCESSING":
            print(".", end="")
            await asyncio.sleep(
                backoff
            )  # polling nao-bloqueante (antes era time.sleep(10), a "Bomba")
            backoff = min(backoff * 2, 10)  # backoff exponencial, teto de 10s
            video_file = genai.get_file(video_file.name)
        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)
        response = self.model.generate_content(
            [video_file, prompt], request_options={"timeout": 600}
        )  # Salva a resposta da Gemini
        await self.translate(response.text)  # Aguarda a função de translate
        sound = self.mixer.Sound(self.PATH_FILE)
        sound.play()  # Execulta a resposta
        await asyncio.sleep(sound.get_length())
        sound.stop()
        self.delete_cache_files()
