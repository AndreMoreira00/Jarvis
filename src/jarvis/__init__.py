"""Jarvis: oculos inteligente por controle de gestos.

Pacote organizado em camadas simples:

- ``jarvis.vision``   captura/reconhecimento de gestos (MediaPipe).
- ``jarvis.core``     orquestracao das acoes e o loop principal da camera.
- ``jarvis.services`` integracoes externas (Gemini/TTS e Google Photos).

Entry points: ``python -m jarvis`` (canonico) ou ``python main.py`` (shim na raiz).
"""
