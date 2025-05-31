from app.error.error_system_logs import errorSystemLogDev, errorSystemLogUser


class Voice:
  def __init__(self):
    self._charRemoved: dict[str, str]  = {
      '\t': ' ',
      '*': ' ',
      '\u200b': ' ',
      '\u200c': ' ',
      '\u200d': ' ',
      '\ufeff': ' ',
      '  ': ' ',
    }
    
    self._voice: str = "pt-BR-AntonioNeural"
    self._pathToResponse = "./src/app/data/response.mp3"
    
    async def _dictate(self, text: str) -> None: # type: ignore
      for old, new in self._charRemoved.items(): # type: ignore
        text: str = text.replace(old, new) # type: ignore
      text: str = text.strip()
        
      try:  
        communicate: object = edge_tts.Communicate(text, self._voice) #type: ignore
      except RuntimeError:
        await errorSystemLogUser("Error: Runtime Error in dictate of Jarvis")
        errorSystemLogDev("Error voice.py - Runtime Error in dictate of Jarvis")
      finally:
        await communicate.save(self._pathToResponse) #type: ignore