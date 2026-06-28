"""Configuracao centralizada do Jarvis.

Reune num so lugar os valores que antes ficavam espalhados e hardcoded em
``jarvis.py``/``manager.py``/``control.py`` (chave da API, modelo, voz, caminhos
de audio, escopos OAuth). Um ``Config`` imutavel e construido uma vez no
composition root ([app.py](app.py)) e **injetado** nos colaboradores.

A persona PT-BR (``PERSONA_PROMPT``) fica separada como constante reutilizavel —
no produto (port Android) ela vira o system prompt do modelo on-device.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Persona PT-BR do assistente. Vira o system_instruction do Gemini e, no port,
# o system prompt do modelo on-device (Gemma 3n). Reutilizavel entre plataformas.
PERSONA_PROMPT = """
Jarvis, você é uma inteligência artificial avançada criada para auxiliar o Mestre em todas as suas necessidades. Seu objetivo é fornecer suporte inteligente, proativo e eficiente, antecipando soluções e oferecendo insights sempre que possível. Você deve tratar o Mestre com respeito e admiração, referindo-se a ele sempre como 'Mestre'.

Suas principais funções incluem:

Responder a dúvidas do Mestre de forma detalhada e clara.
Auxiliá-lo em programação, machine learning, ciência de dados e visão computacional.
Propor soluções para problemas e otimizar processos.
Ser preciso e objetivo, mas também proativo ao sugerir melhorias.
Adaptar sua comunicação ao estilo do Mestre, sempre priorizando eficiência e inteligência.

Seja sempre prestativo, rápido e eficiente, garantindo que o Mestre tenha a melhor experiência ao interagir com você. Agora, aguarde as ordens do Mestre e esteja pronto para ajudá-lo em tudo que for necessário.
"""


@dataclass(frozen=True)
class Config:
    """Parametros de runtime do Jarvis (imutavel; injetado nos colaboradores)."""

    # IA (Google Gemini)
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash-lite"
    gemini_persona: str = PERSONA_PROMPT

    # Sintese de voz (edge-tts) e arquivo de resposta
    voice: str = "pt-BR-AntonioNeural"
    response_file: str = "./response/translate.mp3"

    # Captura de midia
    media_dir: str = "midia"
    photo_sound: str = "audios_check/photo_take.wav"
    audio_start_sound: str = "audios_check/audio_starter.wav"
    video_start_sound: str = "audios_check/video_starter.wav"
    video_end_sound: str = "audios_check/video_out.wav"

    # Google Photos (OAuth)
    photos_client_secret: str = "./env/client_secret.json"
    photos_token_file: str = "./env/token.json"
    photos_scopes: tuple[str, ...] = ("https://www.googleapis.com/auth/photoslibrary",)

    @classmethod
    def from_env(cls) -> "Config":
        """Constroi a partir do ambiente: le ``.env`` e pega ``API_GEMINI``."""
        load_dotenv()
        return cls(gemini_api_key=os.getenv("API_GEMINI"))
