---
title: App cerebro - framework, camera UVC, LLM on-device e mapeamento do MVP Python
source: https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/android + https://developers.google.com/edge/mediapipe/solutions/genai/llm_inference/android + https://developers.googleblog.com/unlocking-peak-performance-on-qualcomm-npu-with-litert/ + https://github.com/jiangdongguo/AndroidUSBCamera + https://developer.apple.com/videos/play/wwdc2023/10106/
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
tags: [referencia, app, android, mediapipe, llm-on-device, uvc, litert, tema/arquitetura]
---

# App cerebro - framework, camera UVC, LLM on-device e mapeamento do MVP Python

Resumo da pesquisa (fontes 2024-2026) para a dimensao APP do produto: o celular
e o cerebro (LLM on-device + percepcao + transporte BLE/WiFi), os oculos sao
cliente fino. Privacidade/offline e a restricao nº1.

## 1. Framework: nativo Android (Kotlin) e o recomendado

- **MediaPipe HandLandmarker** tem API oficial nativa Android (Kotlin), Tasks API,
  modo `LIVE_STREAM`, retorna **21 landmarks (x,y,z)** + handedness (esquerda/direita)
  - exatamente o mesmo modelo geometrico do MVP Python. Mapeamento 1:1 dos `Map_*`.
  Fonte: https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/android
- **LiteRT-LM** (Kotlin API) e o runtime oficial de LLM on-device; a MediaPipe LLM
  Inference API esta em maintenance-only e Google recomenda migrar para LiteRT-LM.
  Aceleracao NPU via Qualcomm QNN: ate 100x sobre CPU, 10x sobre GPU; Gemma atinge
  50-80+ tokens/s no Hexagon NPU. Modelos: Gemma 3 1B / 3n (int4). Devices alvo:
  Pixel 8+/Samsung S23+.
  Fontes: https://developers.google.com/edge/mediapipe/solutions/genai/llm_inference/android ,
  https://developers.googleblog.com/unlocking-peak-performance-on-qualcomm-npu-with-litert/
- Flutter (fllama/flutter_gemma via FFI) e RN (react-native-llm-mediapipe) existem mas
  ficam atras: dependem do mesmo C/C++ por baixo, adicionam ponte/serializacao e o
  acesso a NPU/AICore e menos direto. KMP serve para LOGICA compartilhada, nao para os
  runtimes nativos (camera/LLM/MediaPipe continuam por `expect/actual` nativo).

## 2. Camera UVC USB-OTG -> decide Android-first

- Android: **AUSBC (jiangdongguo/AndroidUSBCamera)**, Kotlin, abre UVC via OTG sem root,
  raw frames NV21/RGBA via `setPreviewDataCallBack()` (alimenta o HandLandmarker).
  Alternativa: saki4510t/UVCCamera. Fonte: https://github.com/jiangdongguo/AndroidUSBCamera
- iOS: UVC externo so existe no **iPadOS 17+** (AVCaptureDevice), **NAO no iPhone**.
  Fonte: https://developer.apple.com/videos/play/wwdc2023/10106/
- Conclusao: o requisito de webcam UVC pelo celular forca **Android-first**.

## 3. Arquitetura limpa (camadas)

transporte (BLE controle / WiFi video) -> percepcao (gestos MediaPipe) ->
orquestracao (use-cases, antes `Control`) -> inferencia (LiteRT-LM on-device;
Gemini cloud so fallback opcional) -> STT/TTS on-device (Vosk STT, TTS Android) -> UI.
Cada camada isolada por interface; nada de classe monolitica tipo `Control`.

## 4. Mapeamento do MVP Python (descartavel) -> spec vs codigo novo

- `hands.py` (`Map_Ok/Positive/Speak/Squid/Rock`): vira **SPEC** (regras geometricas dos
  21 landmarks) e re-implementacao em Kotlin. Mesmos indices de landmark.
- `jarvis.py` template (persona PT-BR "Mestre"): **ativo reutilizavel** (system prompt),
  agora alimentando LLM local. STT/TTS reescritos (edge-tts/pygame -> on-device).
- `control.py` (orquestracao, ACTION lock, cooldown, Control_Video): vira **SPEC** de
  maquina de estados/use-cases; codigo novo em Kotlin com corrotinas.
- `manager.py` (upload Google Photos): opcional, conflita com privacidade -> rever.
- Gemini cloud (gemini-2.0-flash-lite): rebaixado a **fallback**, nao caminho padrao.
