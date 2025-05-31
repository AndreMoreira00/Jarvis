import pathlib
import time
import google.generativeai as genai
from app.apis.modules.google_gemini import Gemini
from app.error.error_system_logs import errorSystemLogUser, errorSystemLogDev
from app.controller.modules.controller_check_audio import AudiosChecks
from app.apis.modules.voices.voice import Voice

class RoutesGemini(Gemini):
  def __init__(self):
    super().__init__()
    
    self.audios: object = AudiosChecks()
    self.voice: object = Voice()
  
  @staticmethod
  def __deleteChacheFiles() -> None:
    for file in genai.list_files(): #type: ignore
      myfile: str = genai.get_file(file.name) #type: ignore
      myfile.delete() #type: ignore
  
  async def textToText(self, prompt: str) -> None:
    try:
      response: str = self._model.generate_content(prompt) #type: ignore
    except TypeError:
      await errorSystemLogUser(f"Error: Type input in text to text is not valid! The function is reloading")
      errorSystemLogDev(f"Error google_gemini_routes.py - Type input in text to text is not valid")
      await self.textToText(str(prompt))
      
    await self.voice._dictate(str(response.text)) # type: ignore
    self.audio.playConfirmationSound(self.voice._pathToResponse) # type: ignore
    
  async def imageToText(self, image_path: str, prompt: str) -> None:
    try:
      response: str = self._model.generate_content([{ # type: ignore
        'mime_type':'image/jpeg', 
        'data': pathlib.Path(f'{image_path}').read_bytes()}, 
        prompt])
    except TypeError:
      errorSystemLogDev(f"Error google_gemini_routes.py - Type input in image to text is not valid") # type: ignore
      await self.imageToText(image_path, prompt)
      
    await self.voice._dictate(str(response.text)) #type: ignore
    self.audio.playConfirmationSound(self.voice._pathToResponse) # type: ignore
    
  async def videoToText(self, video_path: str, prompt: str) -> None:
    try:
      video_file = genai.upload_file(path=video_path) # type: ignore
      while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(10) 
        video_file = genai.get_file(video_file.name) # type: ignore
      if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)
    except:
      await errorSystemLogUser(f"Error: in upload video! The function is reloading")
      errorSystemLogDev(f"Error google_gemini_routes.py - Error in upload video")
    try:
      response: str = self._model.generate_content([video_file, prompt], request_options={"timeout": 600}) # type: ignore
    except Exception as e:
      await errorSystemLogUser(f"Error: Generate response about the video {e}")
      errorSystemLogDev(f"Error google_gemini_routes.py - Generate response about the video {e}")
      
    await self.voice._dictate(str(response.text)) # type: ignore
    self.audio.playConfirmationSound(self.voice._pathToResponse) # type: ignore
    self.__deleteChacheFiles()