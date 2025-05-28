import edge_tts
from pygame import mixer
import asyncio

mixer.init()

_voice: str = "pt-BR-AntonioNeural"
_mixer: object = mixer
_pathFile: str = "./src/app/error/error.mp3"

async def errorSystemLogUser(error: str) -> None:
  error_text: str = error.strip()
  communicate = edge_tts.Communicate(error_text, _voice)
  await communicate.save(_pathFile)
  sound = _mixer.Sound(_pathFile) 
  sound.play()
  await asyncio.sleep(sound.get_length())
  sound.stop()
  
def errorSystemLogDev(error: str) -> None:
  pass