import  pyaudio
import wave
import speech_recognition as sr
import cv2
import numpy as np
import time
import asyncio
from threading import Thread

def save_video():
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    timesr = time.strftime("%Y%m%d_%H%M%S")
    
    duration_in_seconds = 5
    fps = 30
    
    out = cv2.VideoWriter(f'Video/{timesr}.avi', fourcc, fps, (640, 480))
    
    total_frames = duration_in_seconds * fps

    frame_count = 0
    while frame_count < total_frames:
        
        status, frame = cap.read()
        out.write(frame)
        frame_count+=1
        
def Video_Audio():  
  audio = pyaudio.PyAudio()
  
  stream = audio.open(
    input = True,
    format = pyaudio.paInt16,
    channels = 1,
    rate = 44000,
    frames_per_buffer = 1024,
  )
  
  frames = []
  
  timeout = 5
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
      print("" + r.recognize_google(audio, language="pt-BR"))   
  except LookupError:         
      print("Sem Falas!")
      
t1 = Thread(target=Video_Audio)
t2 = Thread(target=save_video)
t1.start()
t2.start()
time.sleep(0.5)