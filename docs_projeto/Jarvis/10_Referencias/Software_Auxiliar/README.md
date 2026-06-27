---
title: Software_Auxiliar — Jarvis
area: Referencias/Software_Auxiliar
tags: [readme, template, projeto, pendente::ingestao]
project: Jarvis
created: 2026-04-24
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Software Auxiliar

Referências das bibliotecas e serviços de terceiros usados pelo software do
**Jarvis** (óculos inteligentes com controle por gestos). Cada nota descreve o que é
a biblioteca, **como o Jarvis a usa** (classe/método e parâmetros reais do código),
pontos de atenção e o link oficial.

## Índice de referências

| Referência | Papel no Jarvis | Onde é usada |
|---|---|---|
| [[Ref_MediaPipe_Hands\|MediaPipe Hands]] | Detecção das mãos (21 landmarks) p/ reconhecer gestos | `Hands` ([hands.py](hands.py)) |
| [[Ref_Google_Gemini_API\|Google Gemini API]] | IA multimodal (texto/imagem/vídeo) que responde | `Jarvis` ([jarvis.py](jarvis.py)) |
| [[Ref_Edge_TTS\|edge-tts]] | Síntese de voz (TTS) da resposta | `Jarvis.Translate` ([jarvis.py](jarvis.py)) |
| [[Ref_OpenCV\|OpenCV (cv2)]] | Câmera, conversão de cor, foto/vídeo, janela | [main.py](main.py) / [control.py](control.py) |
| [[Ref_Google_Photos_API\|Google Photos Library API]] | Upload das mídias via OAuth2 | `Manager` ([manager.py](manager.py)) |
| [[Ref_SpeechRecognition\|SpeechRecognition]] | Captura e transcrição de voz (STT) | `Control.Capture_Audio` ([control.py](control.py)) |
| [[Ref_Pygame_Mixer\|pygame.mixer]] | Reprodução de sons de confirmação e da resposta | `Control` / `Jarvis` |

## Fluxo (por frame)

câmera ([[Ref_OpenCV\|OpenCV]]) → mãos ([[Ref_MediaPipe_Hands\|MediaPipe]]) →
gesto → ação ([control.py](control.py)) → IA ([[Ref_Google_Gemini_API\|Gemini]])
e/ou upload ([[Ref_Google_Photos_API\|Google Photos]]) → voz
([[Ref_SpeechRecognition\|STT]] + [[Ref_Edge_TTS\|edge-tts]] +
[[Ref_Pygame_Mixer\|pygame.mixer]]).

## Referências relacionadas

- [[Arquitetura_Software|Arquitetura do Software]]
- [[Referencia_Modulos|Referência de Módulos]]
- [[Home|Home do projeto]]
