import asyncio
from pygame import mixer

mixer.init()

class AudiosChecks():
  def __init__(self): 
    self.photoTakeSound = "src/app/data/sounds/photo_take.wav"
    self.audioStartSound = "src/app/data/sounds/audio_starter.wav"
    self.videoStartSound = "src/app/data/sounds/video_starter.wav" 
    self.videoEndSound = "src/app/data/sounds/video_out.wav"
    self._mixer = mixer
    
  async def playConfirmationSound(self, soundPath: str) -> None:
    sound = self._mixer.Sound(soundPath) 
    sound.play()
    await asyncio.sleep(sound.get_length())
    sound.stop()