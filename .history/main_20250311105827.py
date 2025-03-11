import hands # Importação da classe do Hands
import control # Importação da classe do Control
import cv2 # Biblioteca que da acessoa câmera
import time # Biblioteca de tempo para controle de algumas funções
import asyncio # Torna as funções assincronas
from concurrent.futures import ThreadPoolExecutor # Torna as funções sincronas

async def main(): # Função de execução principal
  hands_system = hands.Hands() # Criação do objeto Hands
  control_functions = control.Control() # Criação do objeto Control
  
  # Preferencia de camera
  cap = cv2.VideoCapture(0)
  out = None # Variável para armazenar o objeto de gravação

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
            
            h, w, _ = frame.shape # Constantes de proporção da camera h = heigth, w = width, _ = canais

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

        # Reduz o cooldown a cada frame
        if gesture_cooldown > 0:
            gesture_cooldown -= 1

      rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Configuração de cores para a identificação das mãos
      results = hands_system.hands.process(rgb_frame) # Resposta da identificação das mãos
      
      # Indicador visual para mostrar quando está gravando
      if gravando:
          cv2.putText(frame, "Gravando...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
          # Grava o frame atual se estiver gravando
          if out is not None:
              out.write(frame)
      
      if results.multi_hand_landmarks and results.multi_handedness and gesture_cooldown == 0: # Marcaçãos dos pontos e retas nas mãos
          for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness): # Obtemos as previsões em tempo real dos pontos e das retas
              
              hand_label = hand_handedness.classification[0].label # Identificação da mão direita e esquerda
              
              h, w, _ = frame.shape # Constantes de proporção da camera h = heigth, w = width, _ = depth

              # Verificação do gesto de mão OK
              if hand_label == "Right" and hands_system.Map_Ok(h, w, hand_landmarks, frame) and not control_functions.ACTION:
                  executor = ThreadPoolExecutor(max_workers=1)
                  executor.submit(control_functions.Capture_Photo, frame) # Chamada para o controle tirar uma foto
                  gesture_cooldown = 15  # Previne múltiplas detecções
              
              # Verificação do gesto de mão Positivo (joinha) para iniciar/parar a gravação
              if hand_label == "Left" and hands_system.Map_Positive(h, w, hand_landmarks, frame):
                  if not gravando:
                      # Inicia a gravação
                      print("Iniciando gravação com gesto de joinha...")
                      fourcc = cv2.VideoWriter_fourcc(*'XVID')
                      timesr = time.strftime("%Y%m%d_%H%M%S")
                      out = cv2.VideoWriter(f'video/{timesr}.avi', fourcc, 30, (640, 480))
                      gravando = True
                  else:
                      # Para a gravação
                      print("Parando gravação com gesto de joinha...")
                      if out is not None:
                          out.release()
                          out = None
                      gravando = False
                  gesture_cooldown = 30  # Cooldown maior para evitar múltiplas detecções
              
              # Verificação do gesto de mão Levantar dedo
              if hand_label == "Right" and hands_system.Map_Speak(h, w, hand_landmarks, frame) and not control_functions.ACTION:
                  await control_functions.Audio_to_Audio() # Chamada para o controle para fazer uma pergunta e agauarda a resposta
                  gesture_cooldown = 15  # Previne múltiplas detecções
              
              # Verificação do gesto de mão Faz o L
              if hand_label == "Left" and hands_system.Map_Squid(h, w, hand_landmarks, frame) and not gravando:
                  await control_functions.Image_Audio(frame) # Chamada para o controle para fazer uma pergunta, analisar uma imagem e agauardar a resposta
                  gesture_cooldown = 15  # Previne múltiplas detecções

              # Verificação do gesto de mão Rock
              if hand_label == "Right" and hands_system.Map_Rock(h, w, hand_landmarks, frame) and not gravando:
                  await control_functions.Video_Audio(cap) # Chamada para o controle para fazer uma pergunta, analisar um video e agauardar a resposta
                  gesture_cooldown = 15  # Previne múltiplas detecções
                  
              # Reenderizar os pontos e retas na tela
              hands_system.mp_drawing.draw_landmarks(frame, hand_landmarks, hands_system.mp_hands.HAND_CONNECTIONS)
          
      cv2.imshow("MediaPipe Hands", frame) # Criar uma tela com a visao da camera
      
      if cv2.waitKey(1) & 0xFF == ord('q'): # Encerra o programa clicando Q
          break
      
  # Libera recursos ao finalizar
  if out is not None:
      out.release()
  cap.release() # Fecha a camera
  cv2.destroyAllWindows() # Destroi a tela da camera

if __name__ == "__main__": # Verificação de arquivo principal com prioridade de execução
  asyncio.run(main()) # Execultar a função principal de forma assincrona