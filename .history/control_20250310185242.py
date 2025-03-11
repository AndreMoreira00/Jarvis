import time # Biblioteca de tempo para controle de algumas funções
import cv2 # Biblioteca que da acesso a câmera
# import pyaudio # Vamos remover essa merda
import wave  # Biblioteca para salvar o video gravado
import speech_recognition as sr # Biblioteca para transformar audio em texto
from concurrent.futures import ThreadPoolExecutor # Torna as funções sincronas

import jarvis # Importação da classe do Jarvis

class Control: # Classe de Controle de funções
  def __init__(self): 
    self.ACTION = False # Variavel de controle de funções (Impossibilita que a função execulte varias vezes)
    self.jarvis_system = jarvis.Jarvis() # Criação do objeto Jarvis
    self.estado = False # Variável de controle para o estado de gravação
  
  # Capture Photo
  def Capture_Photo(self, frame):
    self.ACTION = True # Define a ação como em andamento
    timesr = time.strftime("%Y%m%d_%H%M%S") # Salvamos os arquivos com uma nomenclatura de ano/mes/dia/hora/minito/segundo
    cv2.imwrite(f"image/{timesr}.jpg", frame) # Salva a imagem
    self.ACTION = False # Finaliza a ação
    return f"image/{timesr}.jpg" # Retorna o caminho da imagem salva
  
   #Captura de Video
  def Capture_Video(self, cap, gravando):
    self.ACTION = True # Define a ação como em andamento
    self.estado = True  # Define como True para indicar que estamos gravando
    
    print("Iniciando gravação...") # Mensagem de início de gravação
    fourcc = cv2.VideoWriter_fourcc(*'XVID') # Define o codec do vídeo
    timesr = time.strftime("%Y%m%d_%H%M%S") # Define o nome do arquivo com data e hora atual
    fps = 30 # Define a taxa de frames por segundo
    out = cv2.VideoWriter(f'video/{timesr}.avi', fourcc, fps, (640, 480)) # Cria o objeto de gravação de vídeo
    
    while self.estado:  # Continua gravando enquanto self.estado for True
        status, frame = cap.read() # Lê o frame da câmera
        if not status: # Se não conseguir ler o frame
            break # Interrompe o loop
        out.write(frame) # Escreve o frame no vídeo
        # Pequena pausa para evitar uso excessivo da CPU
        time.sleep(0.001) # Pausa de 1 milissegundo
        
    out.release() # Libera o objeto de gravação
    print(f"Gravação salva: video/{timesr}.avi") # Mensagem de finalização com nome do arquivo
    self.ACTION = False  # Reinicia a flag ACTION quando terminar
        
  # Capture Audio
  def Capture_Audio(self):
    self.ACTION = True # Define a ação como em andamento
    microfone = sr.Recognizer() # Cria um objeto de reconhecimento de fala
    microfone.pause_threshold = 0.8 # Define o limiar de pausa em segundos
    microfone.dynamic_energy_threshold = False # Desativa o ajuste dinâmico de energia
    microfone.energy_threshold = 300 # Define o limiar de energia para considerar como fala
    microfone.maxAlternatives = 1 # Define o número máximo de alternativas de reconhecimento
    with sr.Microphone() as source: # Usa o microfone como fonte de áudio
      with ThreadPoolExecutor() as executor: # Cria um executor para rodar em paralelo
        executor.submit(microfone.adjust_for_ambient_noise, source, duration=2) # Ajusta o ruído ambiente
        try:
          audio = executor.submit(microfone.listen, source, timeout=5, phrase_time_limit=5) # Escuta o áudio com timeout e limite de tempo
          self.ACTION = False # Finaliza a ação
          return (""+microfone.recognize_google(audio.result(), language="pt-BR")) # Retorna a transcrição do áudio em português
        except sr.UnknownValueError: # Se não reconhecer o áudio
            return "Sem Pergunta" # Retorna mensagem de erro
        except sr.RequestError: # Se houver erro na requisição ao Google
            return "Erro de conexão" # Retorna mensagem de erro
        except Exception as e: # Se houver qualquer outro erro
            return f"Erro inesperado: {str(e)}" # Retorna a mensagem de erro

  # Functions control Jarvis
  
  ## Audio to Audio
  async def Audio_to_Audio(self) -> None:
    prompt = self.Capture_Audio() # Captura o audio
    await self.jarvis_system.Text_To_Text(prompt) # Envia uma pergunta de texto ao Jarvis
  
  ## Image Audio
  async def Image_Audio(self, frame) -> None:
    with ThreadPoolExecutor() as executor: # Torna as funções sincronas
      future_foto = executor.submit(self.Capture_Photo, frame) # Captura uma foto
      future_audio = executor.submit(self.Capture_Audio) # Captura o audio
      image_path = future_foto.result() # Pega o caminho da imagem
      prompt = future_audio.result() # Pega a transcrição do audio e passa como prompt         
    await self.jarvis_system.Image_To_Text(image_path,prompt) # Envia uma pergunta de texto e imagem ao Jarvis
    
  ## Video Audio
  async def Video_Audio(self, cap) -> None:
    with ThreadPoolExecutor() as executor: # Torna as funções sincronas
      future_video = executor.submit(self.Capture_Video, cap) # Grava um video
      future_audio = executor.submit(self.Capture_Audio) # Captura o audio
      video_path = future_video.result() # Pega o caminho do video
      prompt = future_audio.result() # Pega a transcrição do audio e passa como prompt
      await self.jarvis_system.Video_To_Text(video_path, prompt) # Envia uma pergunta de texto e video ao Jarvis