import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

def save_foto(frame):
    timesr = time.strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(f"Images/{timesr}.jpg", frame)
    time.sleep(0.5)
    
def ok(h, w, hand_landmarks, frame):
    
    polegar_4 = hand_landmarks.landmark[4]
    polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h)
    
    polegar_1 = hand_landmarks.landmark[1]
    polegar_1_x, polegar_1_y = int(polegar_1.x * w), int(polegar_1.y * h)
    
    polegar_3 = hand_landmarks.landmark[3]
    polegar_3_x, polegar_3_y = int(polegar_3.x * w), int(polegar_3.y * h)
    
    indicador_8 = hand_landmarks.landmark[8]
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h)
    
    indicador_5 = hand_landmarks.landmark[5]
    indicador_5_x, indicador_5_y = int(indicador_5.x * w), int(indicador_5.y * h)
    
    indicador_6 = hand_landmarks.landmark[6]
    indicador_6_x, indicador_6_y = int(indicador_6.x * w), int(indicador_6.y * h)
    
    if (polegar_4_x - indicador_8_x) < 7 and (polegar_4_y - indicador_8_y) < 14 and (indicador_5_y - indicador_6_y) > 14 and (polegar_1_y - indicador_6_y) > 20 and (polegar_3_x - indicador_5_x) > 10:
        return save_foto(frame)

        
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar o frame.")
        break
    
    frame = cv2.flip(frame, 1)    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            
            hand_label = hand_handedness.classification[0].label  
            
            h, w, _ = frame.shape
            
            if hand_label == "Left" and ok(h, w, hand_landmarks, frame):
                print("Gesto Realizado: 'OK'")
            
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
    cv2.imshow("MediaPipe Hands - Gestos Especificos", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()