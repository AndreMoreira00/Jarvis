---
title: VLM offline no celular (Gemma 3n) e pipeline STT/TTS PT-BR on-device
source: https://ai.google.dev/gemma/docs/gemma-3n + https://developers.googleblog.com/en/introducing-gemma-3n-developer-guide/ + https://github.com/ggml-org/whisper.cpp + https://github.com/k2-fsa/sherpa-onnx + https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
tags: [referencia, app, llm-on-device, vlm, stt, tts, gemma, privacidade, tema/ia]
---

# VLM offline no celular (Gemma 3n) e pipeline STT/TTS PT-BR on-device

Resumo da pesquisa (fontes 2024-2026) para a dimensao **LLM offline no celular**.
Atende a restricao nº1 (privacidade/offline) do projeto.

## VLM offline para "foto + pergunta" e viavel (verificado: confirmado, com nuance)

- **Gemma 3n E2B** (Google, 2025): multimodal nativo (texto+imagem+audio), roda **offline**
  via Google AI Edge / LiteRT (arquivo `.task`), INT4, ~2GB (E2B) / ~3GB (E4B). Caso de uso
  de bandeira = **image question answering offline**. Aposta principal do projeto.
- Confirmacao independente: BlueLM-V-3B (vivo, CVPR 2025) roda 4-bit, 2.2GB RAM, 24.4 tok/s,
  2.53s/imagem em flagship; linha MiniCPM-V / FastVLM (Apple) reforca.
- **Nuance critica**: os numeros bons (~24 tok/s, ~2.5s/imagem) sao de **NPUs flagship**
  (Dimensity 9300 / Snapdragon 8 Gen 3). Em **mid-range**: 5-15 tok/s, RAM no limite
  (precisa >=6-8GB) e TTFT de imagem de varios segundos. Aceleracao NPU em mid-range nao e
  garantida (depende de SDK do fabricante: Qualcomm QNN / MediaTek NeuroPilot).

## Runtimes (5+ maduros)

- **Embutiveis no app**: llama.cpp (GGUF), MLC LLM (TVM), MediaPipe LLM Inference / **LiteRT-LM**
  (recomendado pela Google; MediaPipe LLM esta em maintenance-only).
- **API de sistema**: Gemini Nano via ML Kit GenAI (Android, AICore; Prompt API multimodal em
  alpha, so NPUs especificas) e Apple Foundation Models (~3B, iOS-only).
- **Texto/voz puro**: 1B-2B (Gemma 3 1B, Qwen2.5 1.5B forte em PT) a 25-40 tok/s em flagship.

## STT offline (PT)

- **whisper.cpp** (tiny/base, suporta PT): INT4-8 <500MB RAM, WER <10% em fala limpa; flagship
  ~1.5-2x real-time, mid-range/budget 2-4x (mais lento). Alternativa: **Vosk** (~50MB).

## TTS offline PT-BR (substitui edge-tts, que e online)

- **Piper pt_BR** (faber-medium ~63MB) via **sherpa-onnx** (100% offline, Android/iOS).
  Qualidade "medium" natural para assistente, abaixo do pt-BR-AntonioNeural. Aplicar EQ de
  realce de agudos para compensar a conducao ossea.

## Pipeline recomendado (offline)

STT (whisper.cpp/Vosk) -> VLM Gemma 3n E2B (LiteRT-LM + NPU) -> TTS Piper pt_BR (sherpa-onnx).
Gemini cloud rebaixado a fallback opt-in.

## Riscos / acao

- **Validar empiricamente** qualidade do VQA e do TTS **em PT-BR** com piloto antes de congelar.
- Isolar o runtime atras de uma interface (a API ja migrou uma vez).
- Definir device de referencia high-end; modo degradado (1B) em mid-range.

Ver [[../decisoes/2026-06-27_arquitetura_tres_pilares]] e [[app-cerebro-android-ondevice]].
