import hands # Importação da classe do Hands
import control # Importação da classe do Control

import cv2 # Biblioteca que da acessoa câmera
import time # Biblioteca de tempo para controle de algumas funções
import asyncio  # Torna as funções assincronas
from concurrent.futures import ThreadPoolExecutor # Torna as funções sincronas

async def main(): # Função de execução principal
  
  hands_system = hands.Hands() # Criação do objeto Hands
  control_functions = control.Control() # Criação do objeto Control
  with ThreadPoolExecutor() as executor: # Torna as funções sincronas
    
    # Preferencia de camera
    cap = cv2.VideoCapture(1)

    # Execulta as funçõoes de dentro enquanto a camera está aberta
    while cap.isOpened():
        ret, frame = cap.read() # Captura de cada frame da camera. Ret é um parametro para verificar a captura

        if not ret:
            print("Erro ao capturar o frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Configuração de cores para a identificação das mãos
        results = hands_system.hands.process(rgb_frame) # Resposta da identificação das mãos
        
        if results.multi_hand_landmarks and results.multi_handedness: # Marcaçãos dos pontos e retas nas mãos

            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness): # Obtemos as previsões em tempo real dos pontos e das retas
                
                hand_label = hand_handedness.classification[0].label # Identificação da mão direita e esquerda
                
                h, w, _ = frame.shape # Constantes de proporção da camera h = heigth, w = width, _ = depth

                # Verificação do gesto de mão OK
                if hand_label == "Right" and hands_system.Map_Ok(h, w, hand_landmarks, frame) and control_functions.ACTION == False:
                  executor.submit(control_functions.Capture_Photo, frame) # Chamada para o controle tirar uma foto
                
                # Verificação do gesto de mão Positivo
                if hand_label == "Left" and hands_system.Map_Positive(h, w, hand_landmarks, frame) and control_functions.ACTION == False:
                  executor.submit(control_functions.Capture_Video, cap) # Chamada para o controle gravar um video
                  
                # Verificação do gesto de mão Levantar dedo
                if hand_label == "Right" and hands_system.Map_Speak(h, w, hand_landmarks, frame) and control_functions.ACTION == False:
                  await control_functions.Audio_to_Audio() # Chamada para o controle para fazer uma pergunta e agauarda a resposta
                  time.sleep(0.5)
                
                # Verificação do gesto de mão Faz o L
                if hand_label == "Left" and hands_system.Map_Squid(h, w, hand_landmarks, frame):
                  await control_functions.Image_Audio(frame) # Chamada para o controle para fazer uma pergunta, analisar uma imagem e agauardar a resposta
                  time.sleep(0.5)

                # Verificação do gesto de mão Rock
                if hand_label == "Right" and hands_system.Map_Rock(h, w, hand_landmarks, frame):
                  await control_functions.Video_Audio(cap) # Chamada para o controle para fazer uma pergunta, analisar um video e agauardar a resposta
                  time.sleep(0.5) 
                      
                hands_system.mp_drawing.draw_landmarks(frame, hand_landmarks, hands_system.mp_hands.HAND_CONNECTIONS) # Reenderizar os pontos e retas na tela
            
        cv2.imshow("MediaPipe Hands", frame) # Criar uam tela com a visao da camera
        
        if cv2.waitKey(1) & 0xFF == ord('q'): # Encerra o programa clicando Q
          break
        
    cap.release() # Fecha a camera
    cv2.destroyAllWindows() # Destroi a tela da camera

if __name__ == "__main__": # Verificação de arquivo principal com prioridade de execução
  asyncio.run(main()) # Execultar a função principal de forma assincrona