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
  
  def controllerVideo(self):
    self.controlVideo = not self.controlVideo
  
  def captureVideo(self, cap: object, executor: object) -> str:
    self.controllerVideo()
    fourcc: object = cv2.VideoWriter_fourcc(*"XVID") # type: ignore
    timesr = time.strftime("%Y%m%d_%H%M%S")
    fps = 30 
    out = cv2.VideoWriter(f"{self._pathSaveDataVideo}/{timesr}.avi", fourcc, fps, (640, 480)) #type: ignore
    asyncio.run(self.audiosChecks.playConfirmationSound(self.audiosChecks.videoStartSound)) #type: ignore
    while self.controlVideo:
        ret, frame = cap.read()  # type: ignore
        out.write(frame)  # type: ignore
    out.release()
    asyncio.run(self.audiosChecks.playConfirmationSound(self.audiosChecks.videoEndSound)) #type: ignore
    # executor.submit(self.menager_system.uploadMidia, f'midia/{timesr}.avi')
    return f"{self._pathSaveDataVideo}/{timesr}.avi"
  
  
# Copyright 2025 André Fernandes Nascimento Moreira
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.