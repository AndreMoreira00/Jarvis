from app.controller.modules.controller_check_audio import AudiosChecks
import time
import cv2
import asyncio
import os
import numpy as np

class BasicFunctions():
  def __init__(self):
    self.audiosChecks: object = AudiosChecks()
    self._pathSaveDataImages: str = "./src/app/data/images"
    self._pathSaveDataVideo: str = "./src/app/data/videos"
    self.controlVideo: bool = False
  
  @staticmethod
  def recycleMidia(midiaPath: str) -> None:
    os.remove(midiaPath)

  def capturePhoto(self, frame: np.ndarray, executor: object) -> str: # type: ignore
    timesr = time.strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(f"{self._pathSaveDataImages}/{timesr}.jpg", frame) # type: ignore
    asyncio.run(self.audiosChecks.playConfirmationSound(self.audiosChecks.photoTakeSound)) # type: ignore
    # executor.submit(self.menager_system.uploadMidia, f'midia/{timesr}.jpg') # type: ignore
    return f"{self._pathSaveDataImages}/{timesr}.jpg"
  
  def Capture_Video(self, cap: object, executor: object) -> str:
    fourcc: object = cv2.VideoWriter_fourcc(*"XVID") # type: ignore
    timesr = time.strftime("%Y%m%d_%H%M%S")
    fps = 30 
    out = cv2.VideoWriter(f"midia/{timesr}.avi", fourcc, fps, (640, 480)) #type: ignore
    asyncio.run(self.audiosChecks.playConfirmationSound(self.audiosChecks.videoStartSound)) #type: ignore
    while self.controlVideo:
        ret, frame = cap.read()  # type: ignore
        out.write(frame)  # type: ignore
    out.release()
    asyncio.run(self.audiosChecks.playConfirmationSound(self.audiosChecks.videoEndSound)) #type: ignore
    # executor.submit(self.menager_system.uploadMidia, f'midia/{timesr}.avi')
    return f"midia/{timesr}.avi"