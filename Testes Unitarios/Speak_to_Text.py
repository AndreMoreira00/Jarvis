import speech_recognition as sr

def Translate():
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
  text = ouvirMic()
  print(text)
  
Translate()