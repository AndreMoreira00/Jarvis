import jarvis
import hands
import control
# from ProjectConfig import Config_Project

import cv2
import time
import asyncio

from concurrent.futures import ThreadPoolExecutor

async def main():
  
  jarvis_model = jarvis.Jarvis()
  control_functions = control.Control()
  hands_system = hands.Hands()
  with ThreadPoolExecutor() as executor:
    
    # Preferencia de camera
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Erro ao capturar o frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands_system.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks and results.multi_handedness:

            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                
                hand_label = hand_handedness.classification[0].label
                
                h, w, _ = frame.shape
              
                if hand_label == "Right" and hands_system.Map_Ok(h, w, hand_landmarks, frame) and control_functions.ACTION == False:
                  executor.submit(control_functions.Capture_Photo, frame)
                  # time.sleep(0.5)
                
                if hand_label == "Left" and hands_system.Map_Positive(h, w, hand_landmarks, frame) and control_functions.ACTION == False:
                  executor.submit(control_functions.Capture_Video, cap)
                  # time.sleep(0.5)
                  
                if hand_label == "Right" and hands_system.Map_Speak(h, w, hand_landmarks, frame) and control_functions.ACTION == False:
                  print('speak')
                  await control_functions.Audio_to_Audio()
                  time.sleep(0.5)
                  
                if hand_label == "Left" and hands_system.Map_Squid(h, w, hand_landmarks, frame):
                  await control_functions.Image_Audio(frame)
                  time.sleep(0.5)
                    
                if hand_label == "Right" and hands_system.Map_Rock(h, w, hand_landmarks, frame):
                  await control_functions.Video_Audio(cap)
                  time.sleep(0.5) 
                      
                hands_system.mp_drawing.draw_landmarks(frame, hand_landmarks, hands_system.mp_hands.HAND_CONNECTIONS)
            
        cv2.imshow("MediaPipe Hands", frame) 
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
          break
        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
  # try:
  #   Config_Project()
  #   asyncio.run(main())
  # except:
  asyncio.run(main())