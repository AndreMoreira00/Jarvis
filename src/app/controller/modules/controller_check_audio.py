class AudiosChecks():
  def __init__(self): 
    self.photoTakeSound = "src/app/data/sounds/photo_take.wav"
    self.audioStartSound = "src/app/data/sounds/audio_starter.wav"
    self.videoStartSsound = "src/app/data/sounds/video_starter.wav" 
    self.videoEndSound = "src/app/data/sounds/video_out.wav"
    
  async def playConfirmationSound(self, soundPath):
    sound = mixer.Sound(soundPath) 
    sound.play()
    await asyncio.sleep(sound.get_length())
    sound.stop()