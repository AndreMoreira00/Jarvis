import time
import cv2 
import pyaudio
import wave
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor

import jarvis

class Control:
  def __init__(self):
    self.ACTION = False
    self.jarvis_system = jarvis.Jarvis()
  
  # Capture Photo
  def Capture_Photo(self, frame):
    self.ACTION = True
    timesr = time.strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(f"image/{timesr}.jpg", frame)
    # time.sleep(0.5)
    self.ACTION = False
    return f"image/{timesr}.jpg"
  
  # Capture Video
  def Capture_Video(self, cap):
    self.ACTION = True
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    timesr = time.strftime("%Y%m%d_%H%M%S")
    duration_in_seconds = 15
    fps = 30
    out = cv2.VideoWriter(f'video/{timesr}.avi', fourcc, fps, (640, 480))
    total_frames = duration_in_seconds * fps
    frame_count = 0
    while frame_count < total_frames:
        status, frame = cap.read()
        out.write(frame)
        frame_count+=1
    self.ACTION = False
    return f'video/{timesr}.avi'
  
  # Capture Audio
  def Capture_Audio(self):
    self.ACTION = True
    audio = pyaudio.PyAudio()
    stream = audio.open(
      input = True,
      format = pyaudio.paInt16,
      channels = 1,
      rate = 44000,
      frames_per_buffer = 1024,
    )
    frames = []
    timeout = 15
    timeout_start = time.time()
    try:
      while time.time() < timeout_start + timeout:
        bloco = stream.read(1024)
        frames.append(bloco)
    except KeyboardInterrupt:
        pass
    arquivo_final = wave.open("audio/gravacao.wav", "wb")
    arquivo_final.setnchannels(1)
    arquivo_final.setframerate(44000)
    arquivo_final.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    arquivo_final.writeframes(b"".join(frames))
    arquivo_final.close()
    r = sr.Recognizer()
    with sr.WavFile("audio/gravacao.wav") as source:              
      audio = r.record(source)                        
    try:
      self.ACTION = False
      return (""+r.recognize_google(audio, language="pt-BR"))
    except LookupError:         
      self.ACTION = False
      return("Sem perguntas!")

  # Functions control Jarvis
  
  ## Audio to Audio
  async def Audio_to_Audio(self) -> None:
    self.ACTION = True
    prompt = self.Capture_Audio()
    await self.jarvis_system.Text_To_Text(prompt)
  
  ## Image Audio
  async def Image_Audio(self, frame) -> None:
    self.ACTION = True
    with ThreadPoolExecutor() as executor:
      future_foto = executor.submit(self.Capture_Photo, frame)
      future_audio = executor.submit(self.Capture_Audio)
      image_path = future_foto.result()
      prompt = future_audio.result()                       
    await self.jarvis_system.Image_To_Text(image_path,prompt)
    
  ## Video Audio
  async def Video_Audio(self, cap) -> None:
    self.ACTION = True
    with ThreadPoolExecutor() as executor:
      future_video = executor.submit(self.Capture_Video, cap)
      future_audio = executor.submit(self.Capture_Audio)
      video_path = future_video.result()
      prompt = future_audio.result()
    
      await self.jarvis_system.Video_To_Text(video_path, prompt)