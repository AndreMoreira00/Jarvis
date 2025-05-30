class Voice:
  def __init__(self):
    self._char_removed: dict = {
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
    
    async def _dictate(self, text: str) -> None:
      for old, new in self._char_removed.items():
        text: str = text.replace(old, new)
      text: str = text.strip()
        
      try:  
        communicate = edge_tts.Communicate(text, self._voice)
      except RuntimeError:
        errorSystemLogUser(f"Error: Runtime Error in dictate of Jarvis")
        errorSystemLogDev(f"Error voice.py - Runtime Error in dictate of Jarvis {e}")
      finally:
        await communicate.save(self._pathToResponse)