import time  # Biblioteca de tempo para controle de algumas funcoes
import cv2  # Biblioteca que da acesso a camera
import speech_recognition as sr  # Biblioteca para transformar audio em texto
import threading  # Event de gravacao thread-safe + event loop por thread
import asyncio
import jarvis  # Importacao da classe do Jarvis
import manager
from pygame import mixer
import os


class Control:  # Classe de Controle de funcoes
    def __init__(self):
        mixer.init()  # Servico de audio do pygame (aqui dentro: evita efeito colateral no import)
        self.ACTION = False  # Impede que uma funcao execute varias vezes em paralelo
        self.jarvis_system = jarvis.Jarvis(mixer)  # Criacao do objeto Jarvis
        self.menager_system = manager.Manager()
        self._recording = threading.Event()  # Estado de gravacao de video (thread-safe)
        self._tls = threading.local()  # Guarda um event loop por worker thread

        self.photo_take_sound = "audios_check/photo_take.wav"  # Som para tirar fotos
        self.audio_start_sound = "audios_check/audio_starter.wav"  # Som para inicio de captura de audio
        self.video_start_sound = "audios_check/video_starter.wav"  # Som para inicio de gravacao de video
        self.video_end_sound = "audios_check/video_out.wav"  # Som para termino de gravacao de video

    def _run(self, coro):
        """Roda uma coroutine num event loop reutilizavel por thread.

        Os metodos de captura rodam em threads do ThreadPoolExecutor. Antes,
        cada chamada usava asyncio.run, que criava e destruia um event loop por
        vez (fragil e custoso). Aqui mantemos um unico loop por thread.
        """
        loop = getattr(self._tls, "loop", None)
        if loop is None:
            loop = asyncio.new_event_loop()
            self._tls.loop = loop
        return loop.run_until_complete(coro)

    def play_confirmation_sound(self, sound_file):
        """Toca um som de confirmacao de forma sincrona (roda em worker thread)."""
        sound = mixer.Sound(sound_file)
        sound.play()
        time.sleep(sound.get_length())
        sound.stop()

    def toggle_recording(self) -> bool:
        """Alterna o estado de gravacao de video. Retorna True se passou a gravar."""
        if self._recording.is_set():
            self._recording.clear()
            return False
        self._recording.set()
        return True

    def is_recording(self) -> bool:
        return self._recording.is_set()

    def Recycle_midia(midia_path):
        os.remove(midia_path)

    # Capture Photo
    def Capture_Photo(self, frame, executor):
        timesr = time.strftime(
            "%Y%m%d_%H%M%S"
        )  # Nomenclatura ano/mes/dia/hora/minuto/segundo
        cv2.imwrite(f"midia/{timesr}.jpg", frame)  # Salva a imagem
        self.play_confirmation_sound(self.photo_take_sound)
        executor.submit(self.menager_system.uploadMidia, f"midia/{timesr}.jpg")
        return f"midia/{timesr}.jpg"

    # Capture Video
    def Capture_Video(self, cap, executor):
        fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Codec do video
        timesr = time.strftime("%Y%m%d_%H%M%S")
        fps = 30  # Varia com a camera, mas o padrao e 30fps
        out = cv2.VideoWriter(f"midia/{timesr}.avi", fourcc, fps, (640, 480))
        frame_interval = 1 / fps
        self.play_confirmation_sound(self.video_start_sound)
        while self._recording.is_set():  # Grava enquanto o Event estiver setado
            status, frame = cap.read()
            if not status:  # Camera falhou: encerra a gravacao
                break
            out.write(frame)
            time.sleep(frame_interval)  # Respiro: evita busy-loop a 100% de CPU
        out.release()
        self.play_confirmation_sound(self.video_end_sound)
        executor.submit(self.menager_system.uploadMidia, f"midia/{timesr}.avi")
        return f"midia/{timesr}.avi"

    # Capture Audio
    def Capture_Audio(self, executor):
        self.ACTION = True
        microfone = sr.Recognizer()
        microfone.pause_threshold = 0.8  # Pausa para fechar o mic
        microfone.dynamic_energy_threshold = False  # Supressor de ruido
        microfone.energy_threshold = 300  # Sensibilidade do microfone
        microfone.maxAlternatives = 1  # Numero de palavras para a previsao
        with sr.Microphone() as source:
            executor.submit(
                microfone.adjust_for_ambient_noise, source, duration=2
            )  # Calibra o microfone para o ruido ambiente
            self.play_confirmation_sound(self.video_start_sound)
            try:
                audio = executor.submit(
                    microfone.listen, source, timeout=5, phrase_time_limit=5
                )
                text = microfone.recognize_google(audio.result(), language="pt-BR")
                return text or None  # None sinaliza "sem pergunta valida"
            except (sr.UnknownValueError, sr.RequestError):
                return None  # Falha de reconhecimento/conexao: nao e uma pergunta
            except Exception:
                return None

    # Functions control Jarvis

    ## Audio to Audio
    def Audio_to_Audio(self, executor) -> None:
        self.ACTION = True
        prompt = self.Capture_Audio(executor)  # Captura e transcreve a fala
        if prompt:  # So consulta o Jarvis se houve pergunta valida
            self._run(self.jarvis_system.Text_To_Text(prompt))
        self.ACTION = False

    ## Image Audio
    def Image_Audio(self, frame, executor) -> None:
        self.ACTION = True
        future_foto = executor.submit(self.Capture_Photo, frame, executor)  # Captura uma foto
        prompt = self.Capture_Audio(executor)  # Captura e transcreve a fala
        image_path = future_foto.result()  # Caminho da imagem
        if prompt:
            self._run(self.jarvis_system.Image_To_Text(image_path, prompt))
        self.ACTION = False

    ## Video Audio
    def Video_Audio(self, cap, executor) -> None:
        self.ACTION = True
        self._recording.set()  # Inicia a gravacao
        future_video = executor.submit(self.Capture_Video, cap, executor)  # Grava em paralelo
        prompt = self.Capture_Audio(executor)  # Bloqueia ~5s enquanto o usuario fala
        self._recording.clear()  # Encerra a gravacao -> Capture_Video finaliza
        video_path = future_video.result()  # Caminho do video
        if prompt:
            self._run(self.jarvis_system.Video_To_Text(video_path, prompt))
        self.ACTION = False
