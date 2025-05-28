from app.controller.modules.controller_check_audio import AudiosChecks

class BasicFunctions():
  def __init__(self):
    self.audiosChecks: object = AudiosChecks()
    self._pathSaveDataImages: str = "/src/app/data/images"
    self._pathSaveDataVideo: str = "/src/app/data/videos"
    
  def recycleMidia(midiaPath) -> None:
    os.remove(midiaPath)

  def capturePhoto(self, frame, executor) -> str:
    timesr = time.strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(f"{self._pathSaveDataImages}/{timesr}.jpg", frame)
    asyncio.run(self.audiosChecks.playConfirmationSound(self.audiosChecks.photoTakeSound))
    executor.submit(self.menager_system.uploadMidia, f'midia/{timesr}.jpg')
    return f"{self._pathSaveDataImages}/{timesr}.jpg"