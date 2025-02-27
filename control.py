import time # Biblioteca de tempo para controle de algumas funções
import cv2 # Biblioteca que da acessoa câmera
import pyaudio # Vamos remover essa merda
import wave  # Biblioteca para salvar o video gravado
import speech_recognition as sr # Biblioteca para transformar audio em texto
from concurrent.futures import ThreadPoolExecutor # Torna as funções sincronas

import jarvis # Importação da classe do Jarvis

class Control: # Classe de Controle de funções
  def __init__(self): 
    self.ACTION = False # Variavel de controle de funções (Impossibilita que a função execulte varias vezes)
    self.jarvis_system = jarvis.Jarvis() # Criação do objeto Jarvis
  
  # Capture Photo
  def Capture_Photo(self, frame):
    self.ACTION = True
    timesr = time.strftime("%Y%m%d_%H%M%S") # Salvamos os arquivos com uma nomenclatura de ano/mes/dia/hora/minito/segundo
    cv2.imwrite(f"image/{timesr}.jpg", frame) # Salva a imagem
    self.ACTION = False
    return f"image/{timesr}.jpg"
  
  # Capture Video
  def Capture_Video(self, cap):
    self.ACTION = True
    fourcc = cv2.VideoWriter_fourcc(*'XVID') # Inicia uma camera temporaria só para gravar
    timesr = time.strftime("%Y%m%d_%H%M%S") # Salvamos os arquivos com uma nomenclatura de ano/mes/dia/hora/minito/segundo
    duration_in_seconds = 15 # Duração do video 15s mas isso preecisa ser ajustado para o usuario escolher
    fps = 30 # Varia com a qualidade da camera mas o padrão é 30fps
    out = cv2.VideoWriter(f'video/{timesr}.avi', fourcc, fps, (640, 480)) # Objeto para salvar o video e suas caracteristicas (nome, formato, fps, tamanho da tela)
    total_frames = duration_in_seconds * fps # Calculo para saber quantos frames são necessarios para gravar 15 segundos
    frame_count = 0 # Controlador dos frames
    while frame_count < total_frames: # Gravação do video
        status, frame = cap.read() # Captura de cada frame da camera. Ret é um parametro para verificar a captura
        out.write(frame) # Salva cada frame no formato de video
        frame_count+=1
    self.ACTION = False
    return f'video/{timesr}.avi'
  
  # Capture Audio
  def Capture_Audio(self):
    self.ACTION = True
    microfone = sr.Recognizer()
    microfone.pause_threshold = 0.8
    microfone.dynamic_energy_threshold = False
    microfone.energy_threshold = 300
    microfone.maxAlternatives = 1
    with sr.Microphone() as source:
      with ThreadPoolExecutor() as executor:
        executor.submit(microfone.adjust_for_ambient_noise, source, duration=2)
        try:
          audio = executor.submit(microfone.listen, source, timeout=5, phrase_time_limit=5)
          self.ACTION = False
          return (""+microfone.recognize_google(audio.result(), language="pt-BR")) 
        except sr.UnknownValueError:
            return "Sem Pergunta"
        except sr.RequestError:
            return "Erro de conexão"
        except Exception as e:
            return f"Erro inesperado: {str(e)}"

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