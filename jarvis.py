import os
import asyncio
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
import google
import pathlib
import speech_recognition as sr
import edge_tts
from pygame import mixer
import time


class Jarvis:
    def __init__(self):
      # Load Key
      load_dotenv()
      self.API_KEY = os.getenv("API_GEMINI")
      # Template
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
      genai.configure(api_key=self.API_KEY)
      self.model = genai.GenerativeModel(
          "gemini-2.0-flash", system_instruction=self.template
      )
      # Config Voice
      VOICES = ["pt-BR-AntonioNeural"]
      self.VOICE = VOICES[0]
      self.OUTPUT_FILE = "response/translate.mp3"
      # Config Paths
      self.PATH_FILE = "./response/translate.mp3"
      mixer.init()
    
    # Delete Cahche Video
    def Delete_Cahche_Files(self):
      for f in genai.list_files():
          myfile = genai.get_file(f.name)
          myfile.delete()
          
    # Translate voice from Jarvis
    async def Translate(self, text) -> None:
      communicate = edge_tts.Communicate(text, self.VOICE)
      await communicate.save(self.OUTPUT_FILE)
    
    # Response Text to Text
    async def Text_To_Text(self, prompt) -> None:
      response = self.model.generate_content(prompt)
      await self.Translate(response.text)
      SOUND = mixer.Sound(self.PATH_FILE)
      SOUND.play()
      t = 0
      while t <= SOUND.get_length():
        time.sleep(1)
        t+=1
      SOUND.stop()
      
    # Response Image to Text
    async def Image_To_Text(self, image_path, prompt) -> None:
      response = self.model.generate_content([{'mime_type':'image/jpeg', 'data': pathlib.Path(f'{image_path}').read_bytes()}, prompt])
      await self.Translate(response.text)
      SOUND = mixer.Sound(self.PATH_FILE)
      SOUND.play()
      t = 0
      while t <= SOUND.get_length():
        time.sleep(1)
        t+=1
      SOUND.stop()
    
    # Response Video to text 
    async def Video_To_Text(self, video_path, prompt) -> None:
      video_file = genai.upload_file(path=video_path)
      while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)
      if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)
      response = self.model.generate_content([video_file, prompt],
                                        request_options={"timeout": 600})
      await self.Translate(response.text)
      SOUND = mixer.Sound(self.PATH_FILE)
      SOUND.play()
      t = 0
      while t <= SOUND.get_length():
        time.sleep(1)
        t+=1
      SOUND.stop()
      self.Delete_Cahche_Files()