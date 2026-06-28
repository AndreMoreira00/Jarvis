"""Fluxos de assistente — a 'state machine' das acoes.

Cada fluxo orquestra captura -> assistente (Jarvis) -> fala, sob a trava de
ocupado (``RuntimeState.busy``). Roda em worker threads; as corrotinas do
assistente sao consumidas via ``AsyncBridge``. Esta e a peca que o doc de
arquitetura nomeia como spec da state machine do port Kotlin.
"""

from jarvis.core.async_bridge import AsyncBridge
from jarvis.core.capture import Capture
from jarvis.core.state import RuntimeState
from jarvis.services.jarvis import Jarvis


class Flows:
    def __init__(
        self, capture: Capture, assistant: Jarvis, bridge: AsyncBridge, state: RuntimeState
    ) -> None:
        self.capture = capture
        self.assistant = assistant
        self.bridge = bridge
        self.state = state

    def audio_to_audio(self, executor) -> None:
        """Voz -> Gemini (texto) -> fala."""
        self.state.begin()
        prompt = self.capture.capture_audio(executor)  # Captura e transcreve a fala
        if prompt:  # So consulta o Jarvis se houve pergunta valida
            self.bridge.run(self.assistant.text_to_text(prompt))
        self.state.end()

    def image_audio(self, frame, executor) -> None:
        """Foto + voz -> Gemini (imagem + texto) -> fala."""
        self.state.begin()
        future_foto = executor.submit(self.capture.capture_photo, frame, executor)
        prompt = self.capture.capture_audio(executor)  # Captura e transcreve a fala
        image_path = future_foto.result()  # Caminho da imagem
        if prompt:
            self.bridge.run(self.assistant.image_to_text(image_path, prompt))
        self.state.end()

    def video_audio(self, cap, executor) -> None:
        """Grava video + voz -> Gemini (video + texto) -> fala."""
        self.state.begin()
        self.state.start_recording()  # Inicia a gravacao
        future_video = executor.submit(self.capture.capture_video, cap, executor)
        prompt = self.capture.capture_audio(executor)  # Bloqueia ~5s enquanto o usuario fala
        self.state.stop_recording()  # Encerra a gravacao -> capture_video finaliza
        video_path = future_video.result()  # Caminho do video
        if prompt:
            self.bridge.run(self.assistant.video_to_text(video_path, prompt))
        self.state.end()
