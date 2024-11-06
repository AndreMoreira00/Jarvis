# Speech to Text
import speech_recognition as sr

def ouvirMic():
  # habilitar mic
  microfone = sr.Recognizer()
  print("Diga alguma coisa: ")
  with sr.Microphone() as source:
    # armazena o audio em texto
    audio = microfone.listen(source)
  try:
    frase = microfone.recognize_google(audio, language="pt-BR")
    return frase
  except sr.UnknownValueError:
    print("Não entendi")
  return False

# Agente

import os
import asyncio
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv, find_dotenv

load_dotenv()
key = os.getenv("API_GROQ")

template = """
Você é um assistente e eu sou o seu mestre. Você é designado a me ajudar para solucionar qualquer questão lógica que eu fizer. Sempre me trate e se refira a mim como "Mestre": {text}
"""

prompt = PromptTemplate.from_template(template=template)
chat = ChatGroq(api_key=key , model='llama-3.1-8b-instant')
chain = prompt | chat

# # Tradução

def Translate():
  text = ouvirMic()
  translate = f"{chain.invoke(text).content}"
  return translate
  
translate = Translate()

# Text to Speech

import edge_tts

VOICES = ['pt-BR-AntonioNeural']
VOICE = VOICES[0]
OUTPUT_FILE = 'text_speech.mp3'

async def Voice() -> None:
  communicate = edge_tts.Communicate(translate, VOICE)
  await communicate.save(OUTPUT_FILE)
  
loop = asyncio.get_event_loop_policy().get_event_loop()
try:
  loop.run_until_complete(Voice())
  os.system('text_speech.mp3')
finally:
  loop.close()