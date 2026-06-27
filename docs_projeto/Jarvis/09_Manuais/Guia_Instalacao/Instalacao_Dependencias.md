---
title: Instalacao de Dependencias do Jarvis
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 09_Manuais
categoria: manual
tags:
  - manual
  - instalacao
  - module/software
  - layer/manual
---

# Instalacao de Dependencias do Jarvis

Guia de instalacao das dependencias do Jarvis (oculos inteligentes, controle por gestos, alvo Raspberry Pi 3). Para o passo a passo de execucao, ver [[Guia_Rapido_Execucao]]; para erros de instalacao, ver [[Troubleshooting_Jarvis]].

## Ressalva sobre `requirements.txt`

O `requirements.txt` versionado contem entradas **problematicas** que podem quebrar o `pip install`:

- **Pseudo-pacotes da stdlib:** `time`, `os`, `pathlib` — ja vem com o Python; nao instale via pip.
- **Nome generico:** `google` — pacote guarda-chuva que costuma conflitar/falhar; o que o codigo usa de fato e `google-generativeai` e `google-auth-oauthlib`.

Tente primeiro:

```powershell
pip install -r requirements.txt
```

Se falhar, **instale manualmente** as dependencias reais da tabela abaixo, ignorando as entradas da stdlib.

## Dependencias reais

| Pacote (pip) | Import / uso | Para que serve |
|---|---|---|
| `opencv-python` | `cv2` | Captura de camera, IO de imagem/video, janela de visualizacao |
| `mediapipe` | `mediapipe` | Deteccao de mao (Hands, 21 landmarks) |
| `google-generativeai` | `google.generativeai` | Cliente do Gemini (`gemini-2.0-flash-lite`), multimodal |
| `edge-tts` | `edge_tts` | TTS (voz `pt-BR-AntonioNeural`) |
| `pygame` | `pygame.mixer` | Playback dos audios (resposta falada e sons de confirmacao) |
| `SpeechRecognition` | `speech_recognition` | STT via `recognize_google` (pt-BR) |
| `PyAudio` | backend de `sr.Microphone` | Acesso ao microfone (necessario para capturar voz) |
| `python-dotenv` | `dotenv` | Carrega `API_GEMINI` do `.env` |
| `requests` | `requests` | Chamadas HTTP ao Google Photos |
| `google-auth-oauthlib` | `google_auth_oauthlib`, `google.oauth2` | Fluxo OAuth2 do Google Photos |

Instalacao manual sugerida:

```powershell
pip install opencv-python mediapipe google-generativeai edge-tts pygame SpeechRecognition PyAudio python-dotenv requests google-auth-oauthlib
```

> **PyAudio no Windows:** se `pip install PyAudio` falhar (precisa de toolchain de build), instale um wheel pre-compilado compativel com a sua versao do Python. Sem PyAudio, o `sr.Microphone()` nao abre e os gestos de voz falham — ver [[Troubleshooting_Jarvis]] e [[Ref_SpeechRecognition]].

## Apos instalar

1. `python ProjectConfig.py` — cria `response/`, `midia/` e o `.env` vazio (idempotente).
2. Preencha `.env` com `API_GEMINI=<sua_chave>`.
3. Coloque `env/client_secret.json` para o upload no Google Photos.
4. `python main.py`.

Detalhes em [[Guia_Rapido_Execucao]].

## Referencias

- [[Guia_Rapido_Execucao|Guia rapido de execucao]]
- [[Troubleshooting_Jarvis|Troubleshooting do Jarvis]]
- [[Ref_OpenCV|Referencia OpenCV]]
- [[Ref_MediaPipe_Hands|Referencia MediaPipe Hands]]
- [[Ref_Google_Gemini_API|Referencia Google Gemini API]]
- [[Ref_Edge_TTS|Referencia edge-tts]]
- [[Ref_Pygame_Mixer|Referencia pygame.mixer]]
- [[Ref_SpeechRecognition|Referencia SpeechRecognition]]
- [[Ref_Google_Photos_API|Referencia Google Photos API]]
