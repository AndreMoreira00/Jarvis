"""Captura de midia: foto, video e audio (+ sons de confirmacao).

I/O puro de camera/microfone/disco. NAO orquestra o assistente (isso e papel de
[flows.py](flows.py)). Colaboradores (config, uploader, estado, mixer) chegam por
construtor — testavel sem hardware real.
"""

import time

import cv2  # Biblioteca que da acesso a camera
import speech_recognition as sr  # Biblioteca para transformar audio em texto

from jarvis.config import Config
from jarvis.core.state import RuntimeState
from jarvis.services.manager import Manager


class Capture:
    def __init__(self, config: Config, uploader: Manager, state: RuntimeState, mixer) -> None:
        self.config = config
        self.uploader = uploader
        self.state = state
        self.mixer = mixer

    def play_confirmation_sound(self, sound_file: str) -> None:
        """Toca um som de confirmacao de forma sincrona (roda em worker thread)."""
        sound = self.mixer.Sound(sound_file)
        sound.play()
        time.sleep(sound.get_length())
        sound.stop()

    def capture_photo(self, frame, executor) -> str:
        """Tira uma foto, toca o som, agenda o upload e retorna o caminho."""
        timesr = time.strftime("%Y%m%d_%H%M%S")  # ano/mes/dia/hora/minuto/segundo
        path = f"{self.config.media_dir}/{timesr}.jpg"
        cv2.imwrite(path, frame)  # Salva a imagem
        self.play_confirmation_sound(self.config.photo_sound)
        executor.submit(self.uploader.upload_media, path)
        return path

    def capture_video(self, cap, executor) -> str:
        """Grava video enquanto ``state.is_recording()``; depois agenda o upload."""
        fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Codec do video
        timesr = time.strftime("%Y%m%d_%H%M%S")
        fps = 30  # Varia com a camera, mas o padrao e 30fps
        path = f"{self.config.media_dir}/{timesr}.avi"
        out = cv2.VideoWriter(path, fourcc, fps, (640, 480))
        frame_interval = 1 / fps
        self.play_confirmation_sound(self.config.video_start_sound)
        while self.state.is_recording():  # Grava enquanto o Event estiver setado
            status, frame = cap.read()
            if not status:  # Camera falhou: encerra a gravacao
                break
            out.write(frame)
            time.sleep(frame_interval)  # Respiro: evita busy-loop a 100% de CPU
        out.release()
        self.play_confirmation_sound(self.config.video_end_sound)
        executor.submit(self.uploader.upload_media, path)
        return path

    def capture_audio(self, executor) -> str | None:
        """Captura a fala e transcreve. Retorna None em qualquer falha."""
        self.state.begin()
        microfone = sr.Recognizer()
        microfone.pause_threshold = 0.8  # Pausa para fechar o mic
        microfone.dynamic_energy_threshold = False  # Supressor de ruido
        microfone.energy_threshold = 300  # Sensibilidade do microfone
        microfone.maxAlternatives = 1  # Numero de palavras para a previsao
        with sr.Microphone() as source:
            executor.submit(
                microfone.adjust_for_ambient_noise, source, duration=2
            )  # Calibra o microfone para o ruido ambiente
            self.play_confirmation_sound(self.config.video_start_sound)
            try:
                audio = executor.submit(microfone.listen, source, timeout=5, phrase_time_limit=5)
                text = microfone.recognize_google(audio.result(), language="pt-BR")
                return text or None  # None sinaliza "sem pergunta valida"
            except (sr.UnknownValueError, sr.RequestError):
                return None  # Falha de reconhecimento/conexao: nao e uma pergunta
            except Exception:
                return None
