import cv2
import mediapipe as mp
import time



# Inicializa o MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Funções de comando:

# Foto:
def save_foto(frame):
    timesr = time.strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(f"Images/{timesr}.jpg", frame)
    time.sleep(0.5)

# Gravar Video:

# Audio:

# Gravar Video com audio:

# Foto e audio:

# Descrever o ambinete:


# Funções de Gestos:

# OK:
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

# []:

# |]:
            
# OK|:
            
# \/:
            
# |:


# Captura de vídeo
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
            
            # "Right" ou "Left":
            hand_label = hand_handedness.classification[0].label  
            
            # Converte para pixels
            h, w, _ = frame.shape
            
            # Definindo variaves dos pontos da mão
            
            # Palmo:
            # palmo = hand_landmarks.landmark[0]
            # palmo_x, palmo_y = int(palmo.x * w), int(palmo.y * h)
            
            # Polegar:
            # polegar_4 = hand_landmarks.landmark[4]
            # polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h)
            
            # polegar_3 = hand_landmarks.landmark[3]
            # polegar_3_x, polegar_3_y = int(polegar_3.x * w), int(polegar_3.y * h)
    
            # polegar_2 = hand_landmarks.landmark[2]
            # polegar_2_x, polegar_2_y = int(polegar_2.x * w), int(polegar_2.y * h)
            
            # polegar_1 = hand_landmarks.landmark[1]
            # polegar_1_x, polegar_1_y = int(polegar_1.x * w), int(polegar_1.y * h)
            
            # Indicador:
            # indicador_8 = hand_landmarks.landmark[8]
            # indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h)
            
            # indicador_7 = hand_landmarks.landmark[7]
            # indicador_7_x, indicador_7_y = int(indicador_7.x * w), int(indicador_7.y * h)
            
            # indicador_6 = hand_landmarks.landmark[6]
            # indicador_6_x, indicador_6_y = int(indicador_6.x * w), int(indicador_6.y * h)
            
            # indicador_5 = hand_landmarks.landmark[5]
            # indicador_5_x, indicador_5_y = int(indicador_5.x * w), int(indicador_5.y * h)
            
            # Meio:
            # meio_12 = hand_landmarks.landmark[12]
            # meio_12_x, meio_12_y = int(meio_12.x * w), int(meio_12.y * h)
            
            # meio_11 = hand_landmarks.landmark[11]
            # meio_11_x, meio_11_y = int(meio_11.x * w), int(meio_11.y * h)
            
            # meio_10 = hand_landmarks.landmark[10]
            # meio_10_x, meio_10_y = int(meio_10.x * w), int(meio_10.y * h)
            
            # meio_9 = hand_landmarks.landmark[9]
            # meio_9_x, meio_9_y = int(meio_9.x * w), int(meio_9.y * h)
            
            # Anelar:
            # anelar_16 = hand_landmarks.landmark[16]
            # anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * h)
            
            # anelar_15 = hand_landmarks.landmark[15]
            # anelar_15_x, anelar_15_y = int(anelar_15.x * w), int(anelar_15.y * h)
            
            # anelar_14 = hand_landmarks.landmark[14]
            # anelar_14_x, anelar_14_y = int(anelar_14.x * w), int(anelar_14.y * h)
            
            # anelar_13 = hand_landmarks.landmark[13]
            # anelar_13_x, anelar_13_y = int(anelar_13.x * w), int(anelar_13.y * h)
            
            # Mindinho:
            # mindinho_20 = hand_landmarks.landmark[20]
            # mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * h)
            
            # mindinho_19 = hand_landmarks.landmark[19]
            # mindinho_19_x, mindinho_19_y = int(mindinho_19.x * w), int(mindinho_19.y * h)
            
            # mindinho_18 = hand_landmarks.landmark[18]
            # mindinho_18_x, mindinho_18_y = int(mindinho_18.x * w), int(mindinho_18.y * h)
            
            # mindinho_17 = hand_landmarks.landmark[17]
            # mindinho_17_x, mindinho_17_y = int(mindinho_17.x * w), int(mindinho_17.y * h)
            
            # Verificação de Gestos: 

            # OK:
            if hand_label == "Left" and ok(h, w, hand_landmarks, frame):
                print("Gesto Realizado: 'OK'")

            # []:
            
            # |]:
            
            # OK|:
            
            # \/:
            
            # |:
            
            # Desenha todos os pontos da mão
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("MediaPipe Hands - Gestos Especificos", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
