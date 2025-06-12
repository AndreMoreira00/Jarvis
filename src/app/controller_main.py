import cv2
from concurrent.futures import ThreadPoolExecutor
from app.error.error_system_logs import errorSystemLogUser, errorSystemLogDev
from app.controller.modules.controller_actions_hands import ControllerHands


async def controllerMain():
  for modelCamera in range(3): #type: ignore
    try:
      cap = cv2.VideoCapture(1)
    except Exception as e:
      await errorSystemLogUser(f"Error: Failed to start camera, reloading function {e}")  
      errorSystemLogDev(f"Error in controller_main.py - Failed to start camera {e}")
      
  with ThreadPoolExecutor() as executor:
    controllerHands = ControllerHands()
    
    while cap.isOpened(): #type: ignore
      ret, frame = cap.read() #type: ignore
      
      if not ret: # type: ignore
        print("Erro ao capturar o frame.")
        break
  
      rgbFrame: object = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      resultsHands: object = controllerHands.hands.process(rgbFrame) #type: ignore
      
      if resultsHands.multi_hand_landmarks and resultsHands.multi_handedness: #type: ignore
        for hand_landmarks, hand_handedness in zip(resultsHands.multi_hand_landmarks, resultsHands.multi_handedness): #type: ignore
          
          hand_label: tuple[float] = hand_handedness.classification[0].label # type: ignore
          
          h, w, _ = frame.shape
          
          executor.submit(controllerHands.checkGesture, executor, frame, cap, h, w, hand_landmarks, hand_label) #type: ignore
          
          if controllerHands.gestureCooldown > 0:
            controllerHands.gestureCooldown -= 1 

          controllerHands.mpDrawing.draw_landmarks(frame, hand_landmarks, controllerHands.mpHands.HAND_CONNECTIONS) # type: ignore
          
      cv2.imshow("MediaPipe Hands", frame)
      
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    cap.release() #type: ignore
    cv2.destroyAllWindows()
    
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