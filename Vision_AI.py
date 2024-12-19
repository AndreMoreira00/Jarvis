import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import speech_recognition as sr

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
def save_video():
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    timesr = time.strftime("%Y%m%d_%H%M%S")
    
    duration_in_seconds = 15
    fps = 30
    
    out = cv2.VideoWriter(f'Video/{timesr}.avi', fourcc, fps, (640, 480))
    
    total_frames = duration_in_seconds * fps

    frame_count = 0
    while frame_count < total_frames:
        
        status, frame = cap.read()
        out.write(frame)
        frame_count+=1
        
# Audio:
def Translate():
  def ouvirMic():
    # habilitar mic
    microfone = sr.Recognizer()
    print("Diga alguma coisa: ")
    with sr.Microphone() as source:
      # armazena o audio em texto
      audio = microfone.listen(source)
    try:
      frase = microfone.recognize_google(audio, language="pt-BR")
      return frase
    except sr.UnknownValueError:
      print("Não entendi")
    return False
  text = ouvirMic()
  print(text)
  
# Gravar Video com audio:

# Foto e audio:

# Descrever o ambinete:


# Funções de Gestos:

# OK:
def ok(h, w, hand_landmarks, frame):
    return save_foto(frame)

# []:
def cam(h, w, hand_landmarks, frame):
    return save_video()

# |]:
            
# OK|:
            
# \/:
            
# |:
def audio(h, w, hand_landmarks, frame):
    return Translate()

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
            
            # Verificação de Gestos: 

            # OK:
            # if hand_label == "Left" and ok(h, w, hand_landmarks, frame):
            #     print("Gesto Realizado: 'OK'")

            # []:
            # if cam(h, w, hand_landmarks, frame):
            #     print("Gesto Realizado: 'Camera'")
                
            # |]:
            
            # OK|:
            
            # \/:
            
            # |:
            # if hand_label == "Right" and audio(h, w, hand_landmarks, frame):
            #     print("Gesto Realizado: 'Audio'")
            
            # Desenha todos os pontos da mão
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("MediaPipe Hands - Gestos Especificos", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()