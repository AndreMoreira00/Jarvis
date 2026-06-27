---
title: SpeechRecognition (speech_recognition)
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 10_Referencias
categoria: audio
tags: [referencia, biblioteca, module/software, tema/voz]
---

# SpeechRecognition (speech_recognition)

## O que e

Biblioteca Python (`speech_recognition`, importada como `sr`) que abstrai captura de
audio do microfone e transcricao por varios motores de **Speech-to-Text**. No Jarvis
e a **entrada de voz**: transforma a pergunta falada do usuario no texto (prompt) que
sera enviado ao [[Ref_Google_Gemini_API|Gemini]].

## Como o Jarvis usa

Na classe `Control` ([control.py](control.py)), metodo `Capture_Audio(executor)`.

| Item | Detalhe no codigo |
|---|---|
| Reconhecedor | `microfone = sr.Recognizer()` |
| `pause_threshold` | `0.8` (silencio que encerra a fala) |
| `dynamic_energy_threshold` | `False` |
| `energy_threshold` | `300` |
| `maxAlternatives` | `1` |
| Fonte | `with sr.Microphone() as source:` |
| Calibracao de ruido | `microfone.adjust_for_ambient_noise(source, duration=2)` |
| Escuta | `microfone.listen(source, timeout=5, phrase_time_limit=5)` |
| Transcricao | `microfone.recognize_google(audio, language="pt-BR")` |

A calibracao e a escuta sao despachadas via `executor.submit(...)`. O texto
retornado vira `prompt` em `Audio_to_Audio`, `Image_Audio` e `Video_Audio`.
Tratamento de erros: `UnknownValueError` -> `"Sem Pergunta"`; `RequestError` ->
`"Erro de conexao"`; demais -> `"Erro inesperado: ..."`. Requisito relacionado:
[[RF-003_Pergunta_Voz_Resposta_Falada|RF-003]].

## Pontos de atencao

- **`recognize_google` depende de internet**: usa a API web do Google
  ([[RNF-006_Dependencia_Conectividade|RNF-006]]); offline gera `RequestError`.
- **Janela curta**: `timeout=5` e `phrase_time_limit=5` limitam a captura a poucos
  segundos — perguntas longas sao cortadas.
- **Calibracao de 2 s**: `adjust_for_ambient_noise(..., duration=2)` adiciona latencia
  fixa antes de cada escuta ([[RNF-004_Latencia_Resposta|RNF-004]]).
- **Som de confirmacao trocado**: `Capture_Audio` toca `video_start_sound` (som de
  inicio de **video**) ao iniciar a captura de audio — quirk do codigo.
- **`Video_Audio` chama `Capture_Audio` sem `executor`**: bug conhecido, ver
  [[BUG-001_Video_Audio_Sem_Executor|BUG-001]].
- **Idioma fixo `pt-BR`**: alinhado ao [[RNF-003_Idioma_PT_BR|RNF-003]].
- **Versao**: pacote `SpeechRecognition`; backend de microfone (PyAudio) pode exigir
  setup no Pi — **verificar**.

## Link oficial

- https://github.com/Uberi/speech_recognition

## Referencias

- [[control.py|Codigo: control.py (Capture_Audio)]]
- [[RF-003_Pergunta_Voz_Resposta_Falada|RF-003 — Pergunta por voz]]
- [[BUG-001_Video_Audio_Sem_Executor|BUG-001 — Video_Audio sem executor]]
- [[Ref_Google_Gemini_API|Referencia: Google Gemini API]]
- [[Ref_Pygame_Mixer|Referencia: pygame.mixer]]
