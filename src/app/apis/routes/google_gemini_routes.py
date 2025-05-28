import asyncio
import edge_tts
import google.generativeai as genai
from app.apis.modules.google_gemini import Gemini
from app.error.error_system_logs import errorSystemLogUser, errorSystemLogDev
from app.controller.modules.controller_check_audio import AudiosChecks

class RoutesGemini(Gemini):
  def __init__(self):
    super().__init__()
    self._char_removed: dict = {
      '\t': ' ',
      '*': ' ',
      '\u200b': ' ',
      '\u200c': ' ',
      '\u200d': ' ',
      '\ufeff': ' ',
      '  ': ' ',
    }
    self.audios = AudiosChecks()
    self._pathFile = "/src/app/data/response.mp3"
  
  @staticmethod
  def __deleteChacheFiles() -> None:
    for files in genai.list_files():
      myfile: str = genai.get_file(file.name)
      myfile.delete()
  
  async def _dictate(self, text: str) -> None:
    
    for old, new in self._char_removed.items():
      text: str = text.replace(old, new)
    text: str = text.strip()
      
    try:  
      communicate = edge_tts.Communicate(text, self._voice)
    except RuntimeError:
      errorSystemLogUser(f"Error: Runtime Error in dictate of Jarvis")
      errorSystemLogDev(f"Error google_gemini_routes.py - Runtime Error in dictate of Jarvis {e}")
    finally:
      await communicate.save(self._pathFile)
  
  async def textToText(self, prompt: str) -> None:
    try:
      response: str = self._model.generate_content(prompt) 
    except TypeError:
      errorSystemLogUser(f"Error: Type input in text to text is not valid! The function is reloading")
      errorSystemLogDev(f"Error google_gemini_routes.py - Type input in text to text is not valid {e}")
      await self.textToText(str(prompt))
      
    await self._dictate(str(response.text)) 
    self.audio.playConfirmationSound(self._pathFile)
    
  async def imageToText(self, image_path: str, prompt: str) -> None:
    try:
      response = self._model.generate_content([{
        'mime_type':'image/jpeg', 
        'data': pathlib.Path(f'{image_path}').read_bytes()}, 
        prompt])
    except TypeError:
      errorSystemLogUser(f"Error: Type input in image to text is not valid! The function is reloading")
      errorSystemLogDev(f"Error google_gemini_routes.py - Type input in image to text is not valid {e}")
      await self.imageToText(image_path, prompt)
      
    await self._dictate(str(response.text))
    self.audio.playConfirmationSound(self._pathFile)
    
  async def videoToText(self, video_path: str, prompt: str) -> None:
    try:
      video_file = genai.upload_file(path=video_path) 
      while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(10) 
        video_file = genai.get_file(video_file.name)
      if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)
    except:
      errorSystemLogUser(f"Error: in upload video! The function is reloading")
      errorSystemLogDev(f"Error google_gemini_routes.py - Error in upload video {e}")
    try:
      response = self._model.generate_content([video_file, prompt], request_options={"timeout": 600})
    except Exception as e:
      errorSystemLogUser(f"Error: Generate response about the video {e}")
      errorSystemLogDev(f"Error google_gemini_routes.py - Generate response about the video {e}")
      
    await self._dictate(str(response.text))
    self.audio.playConfirmationSound(self._pathFile)
    self.__deleteChacheFiles()