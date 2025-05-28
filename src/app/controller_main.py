import cv2
import asyncio
from concurrent.futures import ThreadPoolExecutor
from error.error_system_logs import errorSystemLogUser
import math
from app.controller.modules.controller_actions_hands import ControllerHands

modelCamera = 0

async def controllerMain():
  global modelCamera
  for i in range(3): 
    try:
      cap = cv2.VideoCapture(modelCamera)
    except Exception as e:
      errorSystemLogUser(f"Error: Failed to start camera, reloading function{e}")  
      modelCamera += 1
      
  with ThreadPoolExecutor() as executor:
    controllerHands = ControllerHands()
    
    while cap.isOpened():
      ret, frame = cap.read()
      
      rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      resultsHands = controllerHands.hands.process(rgbFrame)
      
      if resultsHands.multi_hand_landmarks and resultsHands.multi_handedness:
        for hand_landmarks, hand_handedness in zip(resultsHands.multi_hand_landmarks, resultsHands.multi_handedness):
          hand_label = hand_handedness.classification[0].label
          
          h, w, _ = frame.shape
          
          executor.submit(controllerHands.checkGesture, executor, frame, cap, h, w, hand_landmarks)
          
          if controllerHands.gestureCooldown > 0:
            controllerHands.gestureCooldown -= 1 

          controllerHands.mpDrawing.draw_landmarks(frame, hand_landmarks, controllerHands.mpHands.HAND_CONNECTIONS)
          
      cv2.imshow("MediaPipe Hands", frame)
      
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    cap.release()
    cv2.destroyAllWindows()
    
asyncio.run(controllerMain())