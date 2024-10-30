import cv2
import mediapipe as mp
import time

# Funções de comando

def save_foto(frame):
    timesr = time.strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(f"Images/{timesr}.jpg", frame)
    print(f"Foto tirada e salva como '{timesr}.jpg'")
    time.sleep(0.5)

# Funções de Gestos

def ok(polegar_4_x, indicador_8_x, polegar_4_y, indicador_8_y, frame):
    if (polegar_4_x - indicador_8_x) < 20 and (polegar_4_y - indicador_8_y) < 20:
        return save_foto(frame)

def camera(polegar_4_y, indicador_8_y, mindinho_20_x, mindinho_20_y, meio_12_x, meio_12_y):
    if (polegar_y - indicador_y) > 90 and (mindinho_x - meio_x) < 10 and (mindinho_y - meio_y) < 2:
        time.sleep(0.5)
        return print("Gesto Realizado: 'Camera'")

# Inicializa MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar o frame.")
        break

    frame = cv2.flip(frame, 1)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)
    
    # Verifica se alguma mão foi detectada
    if results.multi_hand_landmarks:
        for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_label = hand_handedness.classification[0].label  # "Right" ou "Left"
            
            # Desenha os pontos e conexões das mãos detectadas na imagem
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Definindo os pontos da mão baseado nos dedos
            
            # Polegar:
            polegar_4 = hand_landmarks.landmark[4]
            
            # Indicador:
            indicador_8 = hand_landmarks.landmark[8]
            
            # Meio:
            meio_12 = hand_landmarks.landmark[12]

            # Anelar:
            anelar_16 = hand_landmarks.landmark[16]
            
            # Mindinho:
            mindinho_20 = hand_landmarks.landmark[20]
            
            # Convertendo coordenadas dos pontos
            h, w, _ = frame.shape
            
            # Polegar:
            polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h)
            
            # Indicador:
            indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h)
            
            # Meio:
            meio_12_x, meio_12_y = int(meio_12.x * w), int(meio_12.y * w)
            
            # Anelar:
            anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * w)
            
            # Mindinho:
            mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * w)
            
            # Verificação de Gestos: 
            if hand_label == "Left" and ok(polegar_4_x, indicador_8_x, polegar_4_y, indicador_8_y, frame):
                print("Gesto Realizado: 'OK'")
            
            if camera(polegar_4_y, indicador_8_y, mindinho_20_x, mindinho_20_y, meio_12_x, meio_12_y):
                print("Gesto Realizado: 'CAMERA'")
                
            # Acessa as coordenadas dos pontos da mão (21 pontos por mão)
            for i, landmark in enumerate(hand_landmarks.landmark):
                # Converte as coordenadas para valores em pixels
                h, w, _ = frame.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)

                # Exibe as coordenadas do ponto-chave na imagem
                cv2.putText(frame, f'{i}', (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1, cv2.LINE_AA)
            

    # Exibe o frame com as mãos detectadas
    cv2.imshow("MediaPipe Hands", frame)

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera os recursos
cap.release()
cv2.destroyAllWindows()
