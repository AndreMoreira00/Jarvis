import hands # Importação da classe do Hands
import control # Importação da classe do Control
import cv2 # Biblioteca que da acessoa câmera
import time # Biblioteca de tempo para controle de algumas funções
import asyncio  # Torna as funções assincronas
from concurrent.futures import ThreadPoolExecutor # Torna as funções sincronas

async def init_hands(): # Função par tornar a iniciação sincrona
  loop = asyncio.get_running_loop() # Aguarda terminar a funçõao
  with ThreadPoolExecutor() as executor:
      return await loop.run_in_executor(executor, hands.Hands)

async def init_control(): # Função par tornar a iniciação sincrona 
    loop = asyncio.get_running_loop() # Aguarda terminar a funçõao
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, control.Control)
      
def verificar_gesto(gesto, func, *args):
    return gesto if func(*args) else None

async def main(): # Função de execução principal
  hands_task = asyncio.create_task(init_hands())
  control_task = asyncio.create_task(init_control())
  
  hands_system, control_functions = await asyncio.gather(hands_task, control_task) # Criação do objeto Hands e Control 
  
  # Preferencia de camera
  cap = cv2.VideoCapture(0)
  
  with ThreadPoolExecutor() as executor: # Torna as funções sincronas
    
    verificacoes = [
      (lambda: control_functions.Capture_Photo(frame), hands_system.Map_Ok, "Right"),
      (lambda: control_functions.Capture_Video(cap), hands_system.Map_Positive, "Left"),
      (lambda: control_functions.Audio_to_Audio(), hands_system.Map_Speak, "Right"),
      (lambda: control_functions.Image_Audio(frame), hands_system.Map_Squid, "Left"),
      (lambda: control_functions.Video_Audio(cap), hands_system.Map_Rock, "Right"),
    ]
    
    while cap.isOpened(): # Execulta as funçõoes de dentro enquanto a camera está aberta
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
                
                futures = {
                  executor.submit(verificar_gesto, act, func, h, w, hand_landmarks, frame): act
                  for act, func, lado in verificacoes
                  if hand_label == lado
                }
                
                for future in futures:
                  future.result()
                      
                hands_system.mp_drawing.draw_landmarks(frame, hand_landmarks, hands_system.mp_hands.HAND_CONNECTIONS) # Reenderizar os pontos e retas na tela
            
        cv2.imshow("MediaPipe Hands", frame) # Criar uam tela com a visao da camera
        
        if cv2.waitKey(1) & 0xFF == ord('q'): # Encerra o programa clicando Q
          break
        
    cap.release() # Fecha a camera
    cv2.destroyAllWindows() # Destroi a tela da camera

if __name__ == "__main__": # Verificação de arquivo principal com prioridade de execução
  asyncio.run(main()) # Execultar a função principal de forma assincrona