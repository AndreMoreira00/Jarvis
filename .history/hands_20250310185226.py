import mediapipe as mp # Biblioteca para detecção de mãos e landmarks
from mediapipe.tasks import python # Módulo de tarefas do mediapipe
from mediapipe.tasks.python import vision # Módulo de visão do mediapipe
import math # Biblioteca para cálculos matemáticos
import cv2 # Biblioteca para processamento de imagens

class Hands:
  def __init__(self):
    self.mp_hands = mp.solutions.hands # Carrega o módulo de detecção de mãos
    self.hands = self.mp_hands.Hands(static_image_mode=False, # Configura o detector de mãos para vídeos (não imagens estáticas)
                          max_num_hands=2, # Número máximo de mãos detectáveis
                          min_detection_confidence=0.5, # Confiança mínima para considerar uma detecção válida
                          min_tracking_confidence=0.5) # Confiança mínima para continuar rastreando
    self.mp_drawing = mp.solutions.drawing_utils # Utilidades para desenhar os pontos e conexões
  
  def Calculate_Distance(self, point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) # Calcula a distância euclidiana entre dois pontos
  
  def Map_Ok(self, h, w, hand_landmarks, frame):
    # Extrai as coordenadas do polegar
    polegar_1 = hand_landmarks.landmark[1] # Base do polegar
    polegar_1_x, polegar_1_y = int(polegar_1.x * w), int(polegar_1.y * h) # Converte para coordenadas de pixel
    polegar_4 = hand_landmarks.landmark[4] # Ponta do polegar
    polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h) # Converte para coordenadas de pixel
    polegar_3 = hand_landmarks.landmark[3] # Articulação do polegar
    polegar_3_x, polegar_3_y = int(polegar_3.x * w), int(polegar_3.y * h) # Converte para coordenadas de pixel
    
    # Extrai as coordenadas do dedo indicador
    indicador_8 = hand_landmarks.landmark[8] # Ponta do indicador
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h) # Converte para coordenadas de pixel
    indicador_6 = hand_landmarks.landmark[6] # Articulação do indicador
    indicador_6_x, indicador_6_y = int(indicador_6.x * w), int(indicador_6.y * h) # Converte para coordenadas de pixel
    indicador_5 = hand_landmarks.landmark[5] # Base do indicador
    indicador_5_x, indicador_5_y = int(indicador_5.x * w), int(indicador_5.y * h) # Converte para coordenadas de pixel
    
    # Extrai coordenadas dos outros dedos (apenas Y é usado)
    medio_12 = hand_landmarks.landmark[12] # Ponta do dedo médio
    medio_12_y = int(medio_12.y * h) # Converte para coordenada Y de pixel
    
    anelar_16 = hand_landmarks.landmark[16] # Ponta do dedo anelar
    anelar_16_y = int(anelar_16.y * h) # Converte para coordenada Y de pixel
    
    mindinho_20 = hand_landmarks.landmark[20] # Ponta do dedo mindinho
    mindinho_20_y = int(mindinho_20.y * h) # Converte para coordenada Y de pixel
    
    # Calcula a distância entre a ponta do polegar e a ponta do indicador
    distancia_polegar_indicador = self.Calculate_Distance(
        (polegar_4_x, polegar_4_y),
        (indicador_8_x, indicador_8_y)
    )
    
    # Verifica se os dedos estão na posição "OK" (polegar e indicador formando um círculo)
    if (distancia_polegar_indicador < 0.05 * w and # Distância pequena entre polegar e indicador (formando círculo)
        indicador_5_y > indicador_6_y and # Base do indicador está abaixo da articulação
        polegar_1_y > indicador_6_y and # Base do polegar está abaixo da articulação do indicador 
        polegar_3_x > indicador_5_x):  # Articulação do polegar está à direita da base do indicador
            # return save_foto(frame)
            return True # Retorna True se reconhecer o gesto "OK"
  
  def Map_Positive(self,h, w, hand_landmarks, frame):
    # Extrai as coordenadas necessárias para o gesto "positivo" (joinha)
    polegar_1 = hand_landmarks.landmark[1] # Base do polegar
    polegar_1_x, polegar_1_y = int(polegar_1.x * w), int(polegar_1.y * h) # Converte para coordenadas de pixel
    polegar_4 = hand_landmarks.landmark[4] # Ponta do polegar
    polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h) # Converte para coordenadas de pixel
    indicador_8 = hand_landmarks.landmark[8] # Ponta do indicador
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h) # Converte para coordenadas de pixel
    indicador_5 = hand_landmarks.landmark[5] # Base do indicador
    indicador_5_x, indicador_5_y = int(indicador_5.x * w), int(indicador_5.y * h) # Converte para coordenadas de pixel
    medio_12 = hand_landmarks.landmark[12] # Ponta do dedo médio
    medio_12_x, medio_12_y = int(medio_12.x * w), int(medio_12.y * h) # Converte para coordenadas de pixel
    medio_9 = hand_landmarks.landmark[9] # Base do dedo médio
    medio_9_x, medio_9_y = int(medio_9.x * w), int(medio_9.y * h) # Converte para coordenadas de pixel
    anelar_16 = hand_landmarks.landmark[16] # Ponta do dedo anelar
    anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * h) # Converte para coordenadas de pixel
    anelar_13 = hand_landmarks.landmark[13] # Base do dedo anelar
    anelar_13_x, anelar_13_y = int(anelar_13.x * w), int(anelar_13.y * h) # Converte para coordenadas de pixel
    mindinho_20 = hand_landmarks.landmark[20] # Ponta do dedo mindinho
    mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * h) # Converte para coordenadas de pixel
    mindinho_17 = hand_landmarks.landmark[17] # Base do dedo mindinho
    mindinho_17_x, mindinho_17_y = int(mindinho_17.x * w), int(mindinho_17.y * h) # Converte para coordenadas de pixel
    
    # Verifica se os dedos estão na posição "positivo" (joinha)
    if (polegar_4_y < polegar_1_y - 0.05 * h and # Ponta do polegar está acima da base do polegar  
        indicador_8_y > indicador_5_y and # Ponta do indicador está abaixo da base do indicador      
        medio_12_y > medio_9_y and # Ponta do dedo médio está abaixo da base do dedo médio             
        anelar_16_y > anelar_13_y and # Ponta do dedo anelar está abaixo da base do dedo anelar           
        mindinho_20_y > mindinho_17_y): # Ponta do dedo mindinho está abaixo da base do dedo mindinho          
        # return save_video()
        return True # Retorna True se reconhecer o gesto "positivo"
  
  def Map_Speak(self,h, w, hand_landmarks, frame):
    # Extrai as coordenadas necessárias para o gesto "falar" (indicador apontando para cima)
    indicador_8 = hand_landmarks.landmark[8] # Ponta do indicador
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h) # Converte para coordenadas de pixel
    indicador_5 = hand_landmarks.landmark[5] # Base do indicador
    indicador_5_x, indicador_5_y = int(indicador_5.x * w), int(indicador_5.y * h) # Converte para coordenadas de pixel
    polegar_4 = hand_landmarks.landmark[4] # Ponta do polegar
    polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h) # Converte para coordenadas de pixel
    polegar_1 = hand_landmarks.landmark[1] # Base do polegar
    polegar_1_x, polegar_1_y = int(polegar_1.x * w), int(polegar_1.y * h) # Converte para coordenadas de pixel
    medio_12 = hand_landmarks.landmark[12] # Ponta do dedo médio
    medio_12_x, medio_12_y = int(medio_12.x * w), int(medio_12.y * h) # Converte para coordenadas de pixel
    medio_9 = hand_landmarks.landmark[9] # Base do dedo médio
    medio_9_x, medio_9_y = int(medio_9.x * w), int(medio_9.y * h) # Converte para coordenadas de pixel
    anelar_16 = hand_landmarks.landmark[16] # Ponta do dedo anelar
    anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * h) # Converte para coordenadas de pixel
    anelar_13 = hand_landmarks.landmark[13] # Base do dedo anelar
    anelar_13_x, anelar_13_y = int(anelar_13.x * w), int(anelar_13.y * h) # Converte para coordenadas de pixel
    mindinho_20 = hand_landmarks.landmark[20] # Ponta do dedo mindinho
    mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * h) # Converte para coordenadas de pixel
    mindinho_17 = hand_landmarks.landmark[17] # Base do dedo mindinho
    mindinho_17_x, mindinho_17_y = int(mindinho_17.x * w), int(mindinho_17.y * h) # Converte para coordenadas de pixel
    palma_0 = hand_landmarks.landmark[0] # Centro da palma
    palma_y = int(palma_0.y * h) # Converte para coordenada Y de pixel
    
    # Verifica se os dedos estão na posição "falar" (indicador apontando para cima)
    if (indicador_8_y < indicador_5_y - 0.05 * h and # Ponta do indicador está acima da base do indicador
        polegar_4_x > polegar_1_x and # Ponta do polegar está à direita da base do polegar                
        medio_12_y > medio_9_y and # Ponta do dedo médio está abaixo da base do dedo médio                  
        anelar_16_y > anelar_13_y and # Ponta do dedo anelar está abaixo da base do dedo anelar              
        mindinho_20_y > mindinho_17_y): # Ponta do dedo mindinho está abaixo da base do dedo mindinho             
        return True # Retorna True se reconhecer o gesto "falar"
  
  def Map_Squid(self,h, w, hand_landmarks, frame):
    # Extrai as coordenadas necessárias para o gesto "L" (indicador para cima e polegar para o lado)
    indicador_8 = hand_landmarks.landmark[8] # Ponta do indicador
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h) # Converte para coordenadas de pixel
    indicador_6 = hand_landmarks.landmark[6] # Articulação do indicador
    indicador_6_x, indicador_6_y = int(indicador_6.x * w), int(indicador_6.y * h) # Converte para coordenadas de pixel
    polegar_4 = hand_landmarks.landmark[4] # Ponta do polegar
    polegar_4_x, polegar_4_y = int(polegar_4.x * w), int(polegar_4.y * h) # Converte para coordenadas de pixel
    polegar_2 = hand_landmarks.landmark[2] # Articulação do polegar
    polegar_2_x, polegar_2_y = int(polegar_2.x * w), int(polegar_2.y * h) # Converte para coordenadas de pixel
    medio_12 = hand_landmarks.landmark[12] # Ponta do dedo médio
    medio_12_x, medio_12_y = int(medio_12.x * w), int(medio_12.y * h) # Converte para coordenadas de pixel
    medio_9 = hand_landmarks.landmark[9] # Base do dedo médio
    medio_9_x, medio_9_y = int(medio_9.x * w), int(medio_9.y * h) # Converte para coordenadas de pixel
    anelar_16 = hand_landmarks.landmark[16] # Ponta do dedo anelar
    anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * h) # Converte para coordenadas de pixel
    anelar_13 = hand_landmarks.landmark[13] # Base do dedo anelar
    anelar_13_x, anelar_13_y = int(anelar_13.x * w), int(anelar_13.y * h) # Converte para coordenadas de pixel
    mindinho_20 = hand_landmarks.landmark[20] # Ponta do dedo mindinho
    mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * h) # Converte para coordenadas de pixel
    mindinho_17 = hand_landmarks.landmark[17] # Base do dedo mindinho
    mindinho_17_x, mindinho_17_y = int(mindinho_17.x * w), int(mindinho_17.y * h) # Converte para coordenadas de pixel
    
    # Verifica se os dedos estão na posição "L" (indicador para cima e polegar para o lado)
    if (indicador_8_y < indicador_6_y - 0.05 * h and # Ponta do indicador está acima da articulação do indicador
          polegar_4_x < polegar_2_x and # Ponta do polegar está à esquerda da articulação do polegar
          mindinho_20_y > mindinho_17_y and # Ponta do dedo mindinho está abaixo da base do dedo mindinho                 
          medio_12_y > medio_9_y and # Ponta do dedo médio está abaixo da base do dedo médio                  
          anelar_16_y > anelar_13_y): # Ponta do dedo anelar está abaixo da base do dedo anelar
          return True # Retorna True se reconhecer o gesto "L"
  
  def Map_Rock(self,h, w, hand_landmarks, frame):
    # Extrai as coordenadas necessárias para o gesto "rock" (indicador e mindinho levantados)
    indicador_8 = hand_landmarks.landmark[8] # Ponta do indicador
    indicador_8_x, indicador_8_y = int(indicador_8.x * w), int(indicador_8.y * h) # Converte para coordenadas de pixel
    indicador_6 = hand_landmarks.landmark[6] # Articulação do indicador
    indicador_6_x, indicador_6_y = int(indicador_6.x * w), int(indicador_6.y * h) # Converte para coordenadas de pixel
    mindinho_20 = hand_landmarks.landmark[20] # Ponta do dedo mindinho
    mindinho_20_x, mindinho_20_y = int(mindinho_20.x * w), int(mindinho_20.y * h) # Converte para coordenadas de pixel
    mindinho_18 = hand_landmarks.landmark[18] # Articulação do dedo mindinho
    mindinho_18_x, mindinho_18_y = int(mindinho_18.x * w), int(mindinho_18.y * h) # Converte para coordenadas de pixel
    medio_12 = hand_landmarks.landmark[12] # Ponta do dedo médio
    medio_12_x, medio_12_y = int(medio_12.x * w), int(medio_12.y * h) # Converte para coordenadas de pixel
    medio_9 = hand_landmarks.landmark[9] # Base do dedo médio
    medio_9_x, medio_9_y = int(medio_9.x * w), int(medio_9.y * h) # Converte para coordenadas de pixel
    anelar_16 = hand_landmarks.landmark[16] # Ponta do dedo anelar
    anelar_16_x, anelar_16_y = int(anelar_16.x * w), int(anelar_16.y * h) # Converte para coordenadas de pixel
    anelar_13 = hand_landmarks.landmark[13] # Base do dedo anelar
    anelar_13_x, anelar_13_y = int(anelar_13.x * w), int(anelar_13.y * h) # Converte para coordenadas de pixel
    
    # Verifica se os dedos estão na posição "rock" (indicador e mindinho levantados)
    if (indicador_8_y < indicador_6_y - 0.05 * h and # Ponta do indicador está acima da articulação do indicador
          mindinho_20_y < mindinho_18_y - 0.05 * h and # Ponta do mindinho está acima da articulação do mindinho                 
          medio_12_y > medio_9_y and # Ponta do dedo médio está abaixo da base do dedo médio                  
          anelar_16_y > anelar_13_y): # Ponta do dedo anelar está abaixo da base do dedo anelar
          return True # Retorna True se reconhecer o gesto "rock"