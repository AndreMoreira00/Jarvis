import time  # Biblioteca de tempo para controle de algumas funções
import cv2  # Biblioteca que da acessoa câmera
import speech_recognition as sr  # Biblioteca para transformar audio em texto
from concurrent.futures import ThreadPoolExecutor  # Torna as funções sincronas 
import jarvis  # Importação da classe do Jarvis
import manager
import asyncio
from pygame import mixer
import os

mixer.init() # Iniciando o serviço de audio do pygame

class Control:  # Classe de Controle de funções
    def __init__(self):
        self.ACTION = False  # Variavel de controle de funções (Impossibilita que a função execulte varias vezes)
        self.jarvis_system = jarvis.Jarvis(mixer) # Criação do objeto Jarvis
        self.menager_system = manager.Manager()
        self.Control_Video = False # Variavel de controle de video
        
        self.photo_take_sound = "audios_check/photo_take.wav" # Som para tirar fotos
        self.audio_start_sound = "audios_check/audio_starter.wav"  # Som para início de captura de áudio
        self.video_start_sound = "audios_check/video_starter.wav"  # Som para início de gravação de vídeo
        self.video_end_sound = "audios_check/video_out.wav"  # Som para término de gravação de vídeo
        
    async def play_confirmation_sound(self, sound_file):
        SOUND = mixer.Sound(sound_file) 
        SOUND.play() # Execulta a resposta
        await asyncio.sleep(SOUND.get_length())
        SOUND.stop()
    
    def Recycle_midia(midia_path):
        os.remove(midia_path)
    
    # Capture Photo
    def Capture_Photo(self, frame, executor):
        # self.ACTION = True
        timesr = time.strftime(
            "%Y%m%d_%H%M%S"
        )  # Salvamos os arquivos com uma nomenclatura de ano/mes/dia/hora/minito/segundo
        cv2.imwrite(f"midia/{timesr}.jpg", frame)  # Salva a imagem
        asyncio.run(self.play_confirmation_sound(self.photo_take_sound))
        executor.submit(self.menager_system.uploadMidia, f'midia/{timesr}.jpg')
        # self.ACTION = False
        return f"midia/{timesr}.jpg"

    # Capture Video
    def Capture_Video(self, cap, executor):
        # self.ACTION = True
        # self.Control_Video = not self.Control_Video
        fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Inicia uma camera temporaria só para gravar
        timesr = time.strftime("%Y%m%d_%H%M%S")  # Salvamos os arquivos com o nome de ano/mes/dia/hora/minito/segundo
        fps = 30  # Varia com a qualidade da camera mas o padrão é 30fps
        out = cv2.VideoWriter(f"midia/{timesr}.avi", fourcc, fps, (640, 480))  # Objeto para salvar o video e suas caracteristicas (nome, formato, fps, tamanho da tela)
        # print("gravacao iniciada")
        # self.ACTION = False
        # print("Gravando")
        asyncio.run(self.play_confirmation_sound(self.video_start_sound))
        while self.Control_Video:  # Gravação do video
            status, frame = cap.read()  # Captura de cada frame da camera. Ret é um parametro para verificar a captura
            out.write(frame)  # Salva cada frame no formato de video
        # if not self.Control_Video:
        #     print("gravacao finalizada")
        out.release()
        # print("Gravação finalizada")
        asyncio.run(self.play_confirmation_sound(self.video_end_sound))
        executor.submit(self.menager_system.uploadMidia, f'midia/{timesr}.avi')
        return f"midia/{timesr}.avi"

    # Capture Audio
    def Capture_Audio(self, executor):
        self.ACTION = True
        microfone = sr.Recognizer()  # Instancia de camera
        microfone.pause_threshold = 0.8  # Pausa para fechar o mic
        microfone.dynamic_energy_threshold = False  # Supressor de ruido
        microfone.energy_threshold = 300  # Hrz do microfine
        microfone.maxAlternatives = 1  # Numero de palavras para a previsão
        with sr.Microphone() as source:  # Enquanto o microfone estiver aberto
            # with ThreadPoolExecutor() as executor:  # Execulta as funções sincronas
            executor.submit(
                microfone.adjust_for_ambient_noise, source, duration=2
            )  # Configuração do microfone
            # print("Audio")
            asyncio.run(self.play_confirmation_sound(self.video_start_sound))
            try:  # Tratamentos de erros
                audio = executor.submit(
                    microfone.listen, source, timeout=5, phrase_time_limit=5
                )  # Transcrição de voz
                # self.ACTION = False                
                return "" + microfone.recognize_google(
                    audio.result(), language="pt-BR"
                )  # Retorno do audio
            except sr.UnknownValueError:
                return "Sem Pergunta"
            except sr.RequestError:
                return "Erro de conexão"
            except Exception as e:
                return f"Erro inesperado: {str(e)}"

    # Functions control Jarvis

    ## Audio to Audio
    def Audio_to_Audio(self, executor) -> None:
        self.ACTION = True
        future_audio = executor.submit(self.Capture_Audio, executor)  # Captura o audio
        prompt = future_audio.result()
        asyncio.run(self.jarvis_system.Text_To_Text(prompt))  # Envia uma pergunta de texto ao Jarvis
        # print(prompt) # Testar esse jeito
        self.ACTION = False

    ## Image Audio
    def Image_Audio(self, frame, executor) -> None:
    # with ThreadPoolExecutor() as executor:  # Torna as funções sincronas
        self.ACTION = True
        future_foto = executor.submit(self.Capture_Photo, frame, executor)  # Captura uma foto
        future_audio = executor.submit(self.Capture_Audio, executor)  # Captura o audio
        image_path = future_foto.result()  # Pega o caminho da imagem
        prompt = future_audio.result() # Pega a transcrição do audio e passa como prompt
        asyncio.run(self.jarvis_system.Image_To_Text(image_path, prompt))  # Envia uma pergunta de texto e imagem ao Jarvis
        self.ACTION = False

    ## Video Audio
    def Video_Audio(self, cap, executor) -> None:
        print("Ate aqui!")
        # with ThreadPoolExecutor() as executor:  # Torna as funções sincronas
        future_video = executor.submit(self.Capture_Video, cap, executor)  # Grava um video 
        future_audio = executor.submit(self.Capture_Audio)  # Captura o audio # Trava o programa. Conflito com Thread # Await aqui! 
        video_path = future_video.result()  # Pega o caminho do video
        prompt = future_audio.result() # Pega a transcrição do audio e passa como prompt
        self.ACTION = True
        asyncio.run(self.jarvis_system.Video_To_Text(video_path, prompt)) # Envia uma pergunta de texto e video ao Jarvis # Precisa aguardar os thread terminarem
        self.ACTION = False