import os
import asyncio
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
import google
import pathlib
import speech_recognition as sr
import edge_tts
from playsound import playsound
import time

class Jarvis:
    def __init__(self):
      # Load Key
      load_dotenv()
      self.API_KEY = os.getenv("API_GEMINI")
      # Template
      self.template = """
      Você é um assistente e eu sou o seu mestre. Você é designado a me ajudar para solucionar qualquer questão lógica que eu fizer. Sempre me trate e se refira a mim como "Mestre". Não use na sua resposta caracteres especiais como (***): 
      """
      # Config model Genai
      genai.configure(api_key=self.API_KEY)
      self.model = genai.GenerativeModel(
          "gemini-1.5-flash", system_instruction=self.template
      )
      # Config Voice
      VOICES = ["pt-BR-AntonioNeural"]
      self.VOICE = VOICES[0]
      self.OUTPUT_FILE = "response/translate.mp3"
      # Config Paths
      self.PATH_FILE = 'C:/Users/andre/OneDrive/Documentos/Jarvis/response/translate.mp3'
    
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
      playsound(self.PATH_FILE)
      
    # Response Image to Text
    async def Image_To_Text(self, image_path, prompt) -> None:
      response = self.model.generate_content([{'mime_type':'image/jpeg', 'data': pathlib.Path(f'{image_path}').read_bytes()}, prompt])
      await self.Translate(response.text)
      playsound(self.PATH_FILE)
    
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
      playsound(self.PATH_FILE)
      self.Delete_Cahche_Files()