import time  # Biblioteca de tempo para controle de algumas funções
import cv2  # Biblioteca que da acessoa câmera
import wave  # Biblioteca para salvar o video gravado
import speech_recognition as sr  # Biblioteca para transformar audio em texto
from concurrent.futures import ThreadPoolExecutor  # Torna as funções sincronas
import jarvis  # Importação da classe do Jarvis
import asyncio
import hands
import pygame # Biblioteca (nesse caso) usada para som


class Control:  # Classe de Controle de funções
    def __init__(self):
        self.ACTION = False  # Variavel de controle de funções (Impossibilita que a função execulte varias vezes)
        self.jarvis_system = jarvis.Jarvis()  # Criação do objeto Jarvis
        self.Control_Video = False
        # Caminhos para as funções de Captura de Áudio e Vídeo
        self.audio_start_sound = "sounds/audio_start.wav"  # Som para início de captura de áudio
        self.video_start_sound = "sounds/video_start.wav"  # Som para início de gravação de vídeo
        self.video_end_sound = "sounds/video_end.wav"  # Som para término de gravação de vídeo
        pygame.mixer.init()

    # Função para reproduzir sons de confirmação
    def play_confirmation_sound(self, sound_file):
        try:
            sound = pygame.mixer.Sound(sound_file)
            sound.play()
            # Pequena pausa para garantir que o som seja reproduzido
            pygame.time.wait(int(sound.get_length() * 1000))
        except Exception as e:
            print(f"Erro ao reproduzir som: {str(e)}")
    # Função para limpar os recursos do pygame       
    def cleanup(self):
        pygame.mixer.quit()
        
    # Capture Photo
    def Capture_Photo(self, frame):
        self.ACTION = True
        timesr = time.strftime(
            "%Y%m%d_%H%M%S"
        )  # Salvamos os arquivos com uma nomenclatura de ano/mes/dia/hora/minito/segundo
        cv2.imwrite(f"image/{timesr}.jpg", frame)  # Salva a imagem
        self.ACTION = False
        return f"image/{timesr}.jpg"

    # Capture Video
    def Capture_Video(self, cap): #entrada e saida
        self.ACTION = True
        # self.Control_Video = not self.Control_Video
        if self.Control_Video:
            fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Inicia uma camera temporaria só para gravar
            timesr = time.strftime("%Y%m%d_%H%M%S")  # Salvamos os arquivos com uma nomenclatura de ano/mes/dia/hora/minito/segundo
            fps = 30  # Varia com a qualidade da camera mas o padrão é 30fps
            out = cv2.VideoWriter(f"video/{timesr}.avi", fourcc, fps, (640, 480))  # Objeto para salvar o video e suas caracteristicas (nome, formato, fps, tamanho da tela)
            # print("gravacao iniciada")
        self.ACTION = False
        while self.Control_Video:  # Gravação do video
            status, frame = cap.read()  # Captura de cada frame da camera. Ret é um parametro para verificar a captura
            out.write(frame)  # Salva cada frame no formato de video
        # if not self.Control_Video:
        #     print("gravacao finalizada")
        out.release()
        return f"video/{timesr}.avi"

    # Capture Audio
    def Capture_Audio(self):
        self.ACTION = True
        microfone = sr.Recognizer()  # Instancia de camera
        microfone.pause_threshold = 0.8  # Pausa para fechar o mic
        microfone.dynamic_energy_threshold = False  # Supressor de ruido
        microfone.energy_threshold = 300  # Hrz do microfine
        microfone.maxAlternatives = 1  # Numero de palavras para a previsão
        with sr.Microphone() as source:  # Enquanto o microfone estiver aberto
            with ThreadPoolExecutor() as executor:  # Execulta as funções sincronas
                executor.submit(
                    microfone.adjust_for_ambient_noise, source, duration=2
                )  # Configuração do microfone
                try:  # Tratamentos de erros
                    audio = executor.submit(
                        microfone.listen, source, timeout=5, phrase_time_limit=5
                    )  # Transcrição de voz
                    self.ACTION = False
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
    async def Audio_to_Audio(self) -> None: #apenas entrada
        prompt = self.Capture_Audio()  # Captura o audio
        await asyncio.create_task(self.jarvis_system.Text_To_Text(prompt))  # Envia uma pergunta de texto ao Jarvis

    ## Image Audio
    async def Image_Audio(self, frame) -> None: #apenas entrada
        with ThreadPoolExecutor() as executor:  # Torna as funções sincronas
            future_foto = executor.submit(self.Capture_Photo, frame)  # Captura uma foto
            future_audio = executor.submit(self.Capture_Audio)  # Captura o audio
            image_path = future_foto.result()  # Pega o caminho da imagem
            prompt = (
                future_audio.result()
            )  # Pega a transcrição do audio e passa como prompt
        await asyncio.create_task(self.jarvis_system.Image_To_Text(image_path, prompt))  # Envia uma pergunta de texto e imagem ao Jarvis

    ## Video Audio
    async def Video_Audio(self, cap) -> None: #entrada
        with ThreadPoolExecutor() as executor:  # Torna as funções sincronas
            future_video = executor.submit(self.Capture_Video, cap)  # Grava um video
            future_audio = executor.submit(self.Capture_Audio)  # Captura o audio
            video_path = future_video.result()  # Pega o caminho do video
            prompt = (
                future_audio.result()
            )  # Pega a transcrição do audio e passa como prompt
            await asyncio.create_task(self.jarvis_system.Video_To_Text(video_path, prompt))  # Envia uma pergunta de texto e video ao Jarvis
