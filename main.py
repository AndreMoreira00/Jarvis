import hands # Importação da classe do Hands
import control # Importação da classe do Control
import cv2 # Biblioteca que da acessoa câmera
import time # Biblioteca de tempo para controle de algumas funções
import asyncio  # Torna as funções assincronas
from concurrent.futures import ThreadPoolExecutor # Torna as funções sincronas

gesture_cooldown = 0

async def main(): # Função de execução principal 
  
  global gesture_cooldown
  
  hands_task = asyncio.create_task(init_hands())
  control_task = asyncio.create_task(init_control())

  hands_system, control_functions = await asyncio.gather(hands_task, control_task) # Criação do objeto Hands e Control
  
  # Preferencia de camera
  cap = cv2.VideoCapture(0)
  
  with ThreadPoolExecutor() as executor: # Torna as funções sincronas
    
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
                
                checks = [
                  # Verificação do gesto de mão OK
                  (lambda: executor.submit(control_functions.Capture_Photo, frame), lambda: hands_system.Map_Ok(h, w, hand_landmarks, frame), "Right", "Async", 20), # Chamada para o controle tirar uma foto
                  # Verificação do gesto de mão Positivo
                  (lambda: executor.submit(control_functions.Capture_Video, cap), lambda: hands_system.Map_Positive(h, w, hand_landmarks, frame), "Left", "Async", 30), # Chamada para o controle gravar um video
                  # Verificação do gesto de mão Levantar dedo
                  (lambda: control_functions.Audio_to_Audio(), lambda: hands_system.Map_Speak(h, w, hand_landmarks, frame), "Right", "Sync", 20), # Chamada para o controle para fazer uma pergunta e agauarda a resposta
                  # Verificação do gesto de mão Faz o L
                  (lambda: control_functions.Image_Audio(frame), lambda: hands_system.Map_Squid(h, w, hand_landmarks, frame), "Left", "Sync", 20), # Chamada para o controle para fazer uma pergunta, analisar uma imagem e agauardar a resposta
                  # Verificação do gesto de mão Rock
                  (lambda: control_functions.Video_Audio(cap), lambda: hands_system.Map_Rock(h, w, hand_landmarks, frame), "Right", "Sync", 20), # Chamada para o controle para fazer uma pergunta, analisar um video e agauardar a resposta
                ]
                
                for func_exe, func_act, side, state, cooldown in checks:
                  if control_functions.ACTION != True and gesture_cooldown == 0:
                    await Check_Gesture(func_exe, func_act, side, hand_label, state, cooldown, control_functions)
                
                # Reduz o cooldown a cada frame
                if gesture_cooldown > 0:
                  gesture_cooldown -= 1
                
                hands_system.mp_drawing.draw_landmarks(frame, hand_landmarks, hands_system.mp_hands.HAND_CONNECTIONS) # Reenderizar os pontos e retas na tela
            
        cv2.imshow("MediaPipe Hands", frame) # Criar uam tela com a visao da camera
        
        if cv2.waitKey(1) & 0xFF == ord('q'): # Encerra o programa clicando Q
          break
        
    cap.release() # Fecha a camera
    cv2.destroyAllWindows() # Destroi a tela da camera

# Funcoes da Main!
async def init_hands(): # Função par tornar a iniciação sincrona
  loop = asyncio.get_running_loop() # Aguarda terminar a funçõao
  with ThreadPoolExecutor() as executor:
      return await loop.run_in_executor(executor, hands.Hands)

async def init_control(): # Função par tornar a iniciação sincrona 
    loop = asyncio.get_running_loop() # Aguarda terminar a funçõao
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, control.Control)
      
async def Check_Gesture(func_exe, func_act, side, hand_label, state, cooldown, control_functions):
  global gesture_cooldown
  if func_act() and hand_label == side:
    gesture_cooldown = cooldown
    if state == "Async":
      control_functions.Control_Video = not control_functions.Control_Video
      func_exe()
    else:
      await func_exe()

if __name__ == "__main__": # Verificação de arquivo principal com prioridade de execução
  asyncio.run(main()) # Execultar a função principal de forma assincrona