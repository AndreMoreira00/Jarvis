---
title: OBJ-002 · Assistente de IA multimodal
id: OBJ-002
type: objetivo
status: aprovado
prioridade: alta
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 00_SGI_Aplicado
tags: [objetivo, module/software, prio/alta, tema/ia]
---

# OBJ-002 · Assistente de IA multimodal

## Descricao

Oferecer um assistente que entende **voz, imagem e video** e responde **falando**, com a persona "Jarvis" (PT-BR, trata o usuario como "Mestre", foco em programacao, machine learning, ciencia de dados e visao computacional). A IA e o **Google Gemini** (`gemini-2.0-flash-lite`), acessado pela classe `Jarvis`, e a resposta textual e convertida em fala por **edge-tts** (voz `pt-BR-AntonioNeural`) e tocada via **pygame.mixer**.

A multimodalidade e o que diferencia o Jarvis de um assistente so de voz: o usuario pode pedir analise do que esta vendo (foto ou video capturados na hora) alem de perguntas de texto.

## Escopo

Tres modos de interacao com a IA, cada um disparado por um gesto:

| Modo | Metodo (`Jarvis`) | Entrada | Gesto |
|---|---|---|---|
| Texto → fala | `Text_To_Text` | voz transcrita (STT) | dedo levantado |
| Imagem + pergunta | `Image_To_Text` | foto + voz | "L" |
| Video + pergunta | `Video_To_Text` | video + voz | rock |

A captura de voz usa **SpeechRecognition** (`recognize_google`, `language="pt-BR"`). A persona e injetada como `system_instruction` no modelo.

## Criterio mensuravel

| Metrica | Meta |
|---|---|
| Modos multimodais funcionais | 3/3 (texto, imagem, video) retornam resposta falada |
| Idioma da resposta | 100% em PT-BR, voz `pt-BR-AntonioNeural` |
| Persona | resposta trata o usuario como "Mestre" e mantem o tom definido no `template` |

Validacao manual via [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002]].

## Referencias

- [[RF-003_Pergunta_Voz_Resposta_Falada|RF-003]]
- [[RF-004_Foto_Mais_Pergunta_Analise|RF-004]]
- [[RF-005_Video_Mais_Pergunta_Analise|RF-005]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007]]
- [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini multimodal]]
- [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003 · TTS edge-tts + pygame]]
- [[Home|Home — Jarvis]]
