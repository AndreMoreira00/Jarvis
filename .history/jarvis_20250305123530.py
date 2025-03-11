import os # Acessa o sistema operacinal
import asyncio # Torna as funções assincronas
from dotenv import load_dotenv, find_dotenv # Carrega a variavel de ambiente que da acesso a API da Gemini
import google.generativeai as genai # API da Gemini
import google # Biblioteca de serviços da google
import pathlib # Biblioteca que transforma os dados de imagem para serem enviados para o Gemini 
import edge_tts # Biblioteca para tranformar a resposta do Gemini na voz do Jarvis
from pygame import mixer # Biblioteca que execulta a voz do Jarvis
import time # Biblioteca de tempo para controle de algumas funções

mixer.init() # Iniciando o serviço de audio do pygame

class Jarvis: # Classe do Jarvis
    def __init__(self): # Função que inicia as "caracteristicas" do Jarvis
      load_dotenv() # Carrega a variavel de ambiente (Key de acesso a API Gemini)
      self.API_KEY = os.getenv("API_GEMINI")
      # Criação do Template que da a personalidade do Jarvis
      self.template = """
        Jarvis, você é uma inteligência artificial avançada criada para auxiliar o Mestre em todas as suas necessidades. Seu objetivo é fornecer suporte inteligente, proativo e eficiente, antecipando soluções e oferecendo insights sempre que possível. Você deve tratar o Mestre com respeito e admiração, referindo-se a ele sempre como 'Mestre'.

        Suas principais funções incluem:

        Responder a dúvidas do Mestre de forma detalhada e clara.
        Auxiliá-lo em programação, machine learning, ciência de dados e visão computacional.
        Propor soluções para problemas e otimizar processos.
        Ser preciso e objetivo, mas também proativo ao sugerir melhorias.
        Adaptar sua comunicação ao estilo do Mestre, sempre priorizando eficiência e inteligência.

        Seja sempre prestativo, rápido e eficiente, garantindo que o Mestre tenha a melhor experiência ao interagir com você. Agora, aguarde as ordens do Mestre e esteja pronto para ajudá-lo em tudo que for necessário.
      """
      # Config model Genai
      genai.configure(api_key=self.API_KEY) # Inicia os serviços da Gemini passando a Key de acesso
      self.model = genai.GenerativeModel( # Configurando o Serviço
          "gemini-2.0-flash-lite", system_instruction=self.template # Escolhendo o modelo do Gemini
      )
      # Config Voice
      VOICES = ["pt-BR-AntonioNeural"] # Escolhendo a voz do Jarvis
      self.VOICE = VOICES[0] 
      # self.OUTPUT_FILE = "response/translate.mp3" # Caminho onde o audio da resposta do Jarvis vai ser salva
      # Config Paths
      self.PATH_FILE = "./response/translate.mp3" # Caminho onde o audio da resposta do Jarvis vai ser executado
      
    
    # Delete Cahche Video
    # Função que apaga os arquivos salvos na memoria do Gemini. (É preciso para não sobrecarregar a memória)
    def Delete_Cahche_Files(self): 
      for f in genai.list_files(): # Acesso a lista de arquivos salvos e deleta um por um
          myfile = genai.get_file(f.name)
          myfile.delete()
          
    # Translate voice from Jarvis
    # Função que recebe a resposta do Gemini em texto e tranforma em audio com a voz do Jarvis
    async def Translate(self, text) -> None:
      communicate = edge_tts.Communicate(text, self.VOICE) # Conversão de texto para audio
      await communicate.save(self.PATH_FILE) # Salva a conversão
    
    # Response Text to Text
    # Função que recebe nossa pergunta e manda para Gemini, depois que ele retorna a resposta ela é transformada em audio
    async def Text_To_Text(self, prompt) -> None:
      response = self.model.generate_content(prompt) # Salva a resposta da Gemini
      await self.Translate(response.text) # Aguarda a função de Translate
      SOUND = mixer.Sound(self.PATH_FILE) 
      SOUND.play() # Execulta a resposta
      t = 0
      while t <= SOUND.get_length():
        time.sleep(1)
        t+=1
      SOUND.stop()
      
    # Response Image to Text
    async def Image_To_Text(self, image_path, prompt) -> None:
      response = self.model.generate_content([{'mime_type':'image/jpeg', 'data': pathlib.Path(f'{image_path}').read_bytes()}, prompt]) # Salva a resposta da Gemini
      await self.Translate(response.text) # Aguarda a função de Translate
      SOUND = mixer.Sound(self.PATH_FILE)
      SOUND.play() # Execulta a resposta
      t = 0
      while t <= SOUND.get_length():
        time.sleep(1)
        t+=1
      SOUND.stop()
    
    # Response Video to text 
    async def Video_To_Text(self, video_path, prompt) -> None:
      video_file = genai.upload_file(path=video_path) # Sobe o video na memoria da Gemini
      while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)
      if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)
      response = self.model.generate_content([video_file, prompt], request_options={"timeout": 600}) # Salva a resposta da Gemini
      await self.Translate(response.text) # Aguarda a função de Translate
      SOUND = mixer.Sound(self.PATH_FILE)
      SOUND.play() # Execulta a resposta
      t = 0
      while t <= SOUND.get_length():
        time.sleep(1)
        t+=1
      SOUND.stop()
      self.Delete_Cahche_Files()