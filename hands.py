import mediapipe as mp
from mediapipe.tasks import python
import math

class Hands:
  def __init__(self):
    self.mp_hands = mp.solutions.hands
    self.hands = self.mp_hands.Hands(static_image_mode=False,
                          max_num_hands=2,
                          min_detection_confidence=0.5,
                          min_tracking_confidence=0.5)
    self.mp_drawing = mp.solutions.drawing_utils
  
  def Calculate_Distance(self, point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
  
  def Map_Ok(self, h, w, hand_landmarks, frame):
    polegar_1 = hand_landmarks.landmark[1]
    polegar_1_x, polegar_1_y = int(polegar_1.x * w), int(polegar_1.y * h) 
    polegar_4 = hand_landmarks.landmark[4]
    polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h)
    polegar_3 = hand_landmarks.landmark[3]
    polegar_3_x, polegar_3_y = int(polegar_3.x * w), int(polegar_3.y * h)
    
    indicador_8 = hand_landmarks.landmark[8]
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h)
    indicador_6 = hand_landmarks.landmark[6]
    indicador_6_x, indicador_6_y = int(indicador_6.x * w), int(indicador_6.y * h)
    indicador_5 = hand_landmarks.landmark[5]
    indicador_5_x, indicador_5_y = int(indicador_5.x * w), int(indicador_5.y * h)
    
    medio_12 = hand_landmarks.landmark[12]
    medio_12_y = int(medio_12.y * h)
    
    anelar_16 = hand_landmarks.landmark[16]
    anelar_16_y = int(anelar_16.y * h)
    
    mindinho_20 = hand_landmarks.landmark[20]
    mindinho_20_y = int(mindinho_20.y * h)
    
    distancia_polegar_indicador = self.Calculate_Distance(
        (polegar_4_x, polegar_4_y),
        (indicador_8_x, indicador_8_y)
    )
    
    if (distancia_polegar_indicador < 0.05 * w and 
        indicador_5_y > indicador_6_y and
        polegar_1_y > indicador_6_y and  
        polegar_3_x > indicador_5_x):  
            # return save_foto(frame)
            return True
  
  def Map_Positive(self, h, w, hand_landmarks, frame):
    polegar_1 = hand_landmarks.landmark[1]
    polegar_1_x, polegar_1_y = int(polegar_1.x * w), int(polegar_1.y * h)
    polegar_4 = hand_landmarks.landmark[4]
    polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h)
    indicador_8 = hand_landmarks.landmark[8]
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h)
    indicador_5 = hand_landmarks.landmark[5]
    indicador_5_x, indicador_5_y = int(indicador_5.x * w), int(indicador_5.y * h)
    medio_12 = hand_landmarks.landmark[12]
    medio_12_x, medio_12_y = int(medio_12.x * w), int(medio_12.y * h)
    medio_9 = hand_landmarks.landmark[9]
    medio_9_x, medio_9_y = int(medio_9.x * w), int(medio_9.y * h)
    anelar_16 = hand_landmarks.landmark[16]
    anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * h)
    anelar_13 = hand_landmarks.landmark[13]
    anelar_13_x, anelar_13_y = int(anelar_13.x * w), int(anelar_13.y * h)
    mindinho_20 = hand_landmarks.landmark[20]
    mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * h)
    mindinho_17 = hand_landmarks.landmark[17]
    mindinho_17_x, mindinho_17_y = int(mindinho_17.x * w), int(mindinho_17.y * h)
    if (polegar_4_y < polegar_1_y - 0.05 * h and  
        indicador_8_y > indicador_5_y and         
        medio_12_y > medio_9_y and               
        anelar_16_y > anelar_13_y and            
        mindinho_20_y > mindinho_17_y):          
        # return save_video()
        return True
  
  def Map_Speak(self,h, w, hand_landmarks, frame):
    indicador_8 = hand_landmarks.landmark[8]
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h)
    indicador_5 = hand_landmarks.landmark[5]
    indicador_5_x, indicador_5_y = int(indicador_5.x * w), int(indicador_5.y * h)
    polegar_4 = hand_landmarks.landmark[4]
    polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h)
    polegar_1 = hand_landmarks.landmark[1]
    polegar_1_x, polegar_1_y = int(polegar_1.x * w), int(polegar_1.y * h)
    medio_12 = hand_landmarks.landmark[12]
    medio_12_x, medio_12_y = int(medio_12.x * w), int(medio_12.y * h)
    medio_9 = hand_landmarks.landmark[9]
    medio_9_x, medio_9_y = int(medio_9.x * w), int(medio_9.y * h)
    anelar_16 = hand_landmarks.landmark[16]
    anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * h)
    anelar_13 = hand_landmarks.landmark[13]
    anelar_13_x, anelar_13_y = int(anelar_13.x * w), int(anelar_13.y * h)
    mindinho_20 = hand_landmarks.landmark[20]
    mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * h)
    mindinho_17 = hand_landmarks.landmark[17]
    mindinho_17_x, mindinho_17_y = int(mindinho_17.x * w), int(mindinho_17.y * h)
    palma_0 = hand_landmarks.landmark[0]
    palma_y = int(palma_0.y * h) 
    if (indicador_8_y < indicador_5_y - 0.05 * h and 
        polegar_4_x > polegar_1_x and                 
        medio_12_y > medio_9_y and                   
        anelar_16_y > anelar_13_y and                
        mindinho_20_y > mindinho_17_y):              
        return True
  
  def Map_Squid(self,h, w, hand_landmarks, frame):
    indicador_8 = hand_landmarks.landmark[8]
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h)
    indicador_6 = hand_landmarks.landmark[6]
    indicador_6_x, indicador_6_y = int(indicador_6.x * w), int(indicador_6.y * h)
    polegar_4 = hand_landmarks.landmark[4]
    polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h)
    polegar_2 = hand_landmarks.landmark[2]
    polegar_2_x, polegar_2_y = int(polegar_2.x * w), int(polegar_2.y * h)
    medio_12 = hand_landmarks.landmark[12]
    medio_12_x, medio_12_y = int(medio_12.x * w), int(medio_12.y * h)
    medio_9 = hand_landmarks.landmark[9]
    medio_9_x, medio_9_y = int(medio_9.x * w), int(medio_9.y * h)
    anelar_16 = hand_landmarks.landmark[16]
    anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * h)
    anelar_13 = hand_landmarks.landmark[13]
    anelar_13_x, anelar_13_y = int(anelar_13.x * w), int(anelar_13.y * h)
    mindinho_20 = hand_landmarks.landmark[20]
    mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * h)
    mindinho_17 = hand_landmarks.landmark[17]
    mindinho_17_x, mindinho_17_y = int(mindinho_17.x * w), int(mindinho_17.y * h)
    if (indicador_8_y < indicador_6_y - 0.05 * h and
          polegar_4_x < polegar_2_x and
          mindinho_20_y > mindinho_17_y and                  
          medio_12_y > medio_9_y and                   
          anelar_16_y > anelar_13_y): 
          return True
  
  def Map_Rock(self,h, w, hand_landmarks, frame):
    indicador_8 = hand_landmarks.landmark[8]
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h)
    indicador_6 = hand_landmarks.landmark[6]
    indicador_6_x, indicador_6_y = int(indicador_6.x * w), int(indicador_6.y * h)
    mindinho_20 = hand_landmarks.landmark[20]
    mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * h)
    mindinho_18 = hand_landmarks.landmark[18]
    mindinho_18_x, mindinho_18_y = int(mindinho_18.x * w), int(mindinho_18.y * h)
    medio_12 = hand_landmarks.landmark[12]
    medio_12_x, medio_12_y = int(medio_12.x * w), int(medio_12.y * h)
    medio_9 = hand_landmarks.landmark[9]
    medio_9_x, medio_9_y = int(medio_9.x * w), int(medio_9.y * h)
    anelar_16 = hand_landmarks.landmark[16]
    anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * h)
    anelar_13 = hand_landmarks.landmark[13]
    anelar_13_x, anelar_13_y = int(anelar_13.x * w), int(anelar_13.y * h)
    if (indicador_8_y < indicador_6_y - 0.05 * h and
          mindinho_20_y < mindinho_18_y - 0.05 * h and                  
          medio_12_y > medio_9_y and                   
          anelar_16_y > anelar_13_y): 
          return True