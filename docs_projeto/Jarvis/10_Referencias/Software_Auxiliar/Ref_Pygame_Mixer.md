---
title: pygame.mixer
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 10_Referencias
categoria: audio
tags: [referencia, biblioteca, module/software, tema/audio]
---

# pygame.mixer

## O que e

Modulo de audio do **pygame** (`from pygame import mixer`) para reproducao de sons e
efeitos. No Jarvis e a **saida sonora**: toca os sons de confirmacao das acoes e
reproduz o `.mp3` com a resposta falada gerada pelo [[Ref_Edge_TTS|edge-tts]].

## Como o Jarvis usa

Dividido entre `Control` ([control.py](control.py)) e `Jarvis` ([jarvis.py](jarvis.py)).

| Item | Onde | Detalhe no codigo |
|---|---|---|
| Inicializacao | [control.py](control.py) | `mixer.init()` no `__init__` da `Control` |
| Injecao | [control.py](control.py) | `jarvis.Jarvis(mixer)` recebe o mixer |
| Som de confirmacao | [control.py](control.py) | `play_confirmation_sound(sound_file)` (async) |
| Carregar som | ambos | `SOUND = mixer.Sound(arquivo)` |
| Tocar | ambos | `SOUND.play()` |
| Aguardar fim | ambos | `await asyncio.sleep(SOUND.get_length())` |
| Parar | ambos | `SOUND.stop()` |

Sons de confirmacao em `audios_check/`: `photo_take.wav`, `audio_starter.wav`,
`video_starter.wav`, `video_out.wav`. A resposta falada e tocada a partir de
`./response/translate.mp3` em `Text_To_Text`, `Image_To_Text` e `Video_To_Text`.
Requisito relacionado: [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007]].

## Pontos de atencao

- **`mixer.init()` no construtor da `Control`**: movido para la de proposito para
  evitar efeito colateral no import e permitir importar/testar `control` sem
  dispositivo de audio (comentario no codigo).
- **Bloqueio por `asyncio.sleep(get_length())`**: a duracao do som vira espera; em
  midias longas isso segura o fluxo (mas respeita a [[RF-008_Debounce_Cooldown_E_Trava_Acao|trava ACTION]]).
- **Som de audio usa o WAV de video**: `Capture_Audio` reaproveita
  `video_start_sound` — ver [[Ref_SpeechRecognition|SpeechRecognition]].
- **Dependencia de hardware de audio**: no [[ADR-0007_Alvo_Raspberry_Pi3|Raspberry Pi 3]]
  o backend de som (ALSA/SDL) precisa estar configurado, senao `mixer.init()` falha.
- **Arquivos `.wav` obrigatorios**: a pasta `audios_check/` deve conter os quatro
  sons, senao `mixer.Sound(...)` lanca erro.
- **Versao**: pacote `pygame`; versao exata **verificar**.

## Link oficial

- https://www.pygame.org

## Referencias

- [[control.py|Codigo: control.py (play_confirmation_sound)]]
- [[jarvis.py|Codigo: jarvis.py (reproducao da resposta)]]
- [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003 — TTS com edge-tts + pygame]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007 — Resposta falada]]
- [[Ref_Edge_TTS|Referencia: edge-tts]]
- [[Ref_SpeechRecognition|Referencia: SpeechRecognition]]
