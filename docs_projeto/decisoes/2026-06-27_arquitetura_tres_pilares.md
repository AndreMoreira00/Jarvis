---
title: Arquitetura de produto - tres pilares (firmware, hardware, app)
type: decisao-repo
status: aprovado
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
tags: [decisao, arquitetura, hardware, firmware, app, esp32-s3, llm-on-device, tema/arquitetura]
---

# Arquitetura de produto - tres pilares (firmware, hardware, app)

Decisao consolidada apos pesquisa multi-agente com verificacao adversarial (13 agentes,
~170 buscas web, fontes 2024-2026). Define o rumo do projeto Jarvis nos tres componentes
que o dono quer evoluir: **firmware**, **hardware** e **app**.

## Contexto

Hoje o sistema e um app **Python desktop** (OpenCV + MediaPipe Hands -> Gemini API ->
edge-tts/pygame -> upload Google Photos), sem nenhum microcontrolador integrado. O dono
quer migrar para um produto vestivel e levantou tres caminhos de compute: ESP32 (API/LLM
local), Raspberry Pi (potente porem consome muito) ou Teensy (firmware C/C++).

### Restricoes firmes (decididas pelo dono)

| Tema | Decisao |
|------|---------|
| Topologia | **Oculos = cliente fino (sensor node) + celular = cerebro** (tethered wireless). Standalone na cabeca descartado. |
| IA/LLM | **Offline/on-device no celular** (modelo quantizado na NPU). Cloud so como fallback opcional. |
| Restricao nº1 | **Privacidade / offline.** |
| Objetivo do ciclo | **Base para produto futuro** (arquitetura "certa", firmware C/C++, app reescrito). |

### Hardware ja em maos

ESP32 DevKitC (classico, WROOM-32), camera CSI "Mini 5MP para Raspberry Pi" (FPC 15 pinos),
webcam UVC USB 1080p 130/150 graus, DCDCs, amplificador "digital/analogico", fone de
conducao ossea, Raspberry Pi 3, microfone.

## Achados que mudaram a decisao (verificados)

1. **A camera CSI 5MP e Pi-only para o hardware do dono.** MIPI CSI-2 nao conecta no ESP32
   (que usa DVP paralelo) nem direto no celular. Adaptadores CSI->USB UVC existem (Arducam),
   mas sao casados com o modulo HQ IMX477, nao com este Mini 5MP. -> bancada no Pi 3.
2. **O ESP32 DevKitC classico nao faz USB host** (sem USB-OTG no silicio) -> nao captura a
   webcam UVC. So ESP32-S2/S3/P4 fazem host USB. *(verificado: confirmado)*
3. **Mesmo o ESP32-S3 tem UVC host limitado**: USB Full-Speed (12 Mbps, MPS 512B, ~0.5 MB/s)
   -> teto ~640x480@15fps; 1080p esta fora de alcance. *(confirmado)*
4. **BLE nao transmite video**: teto real ~1.4 Mbps no 2M PHY (~0.5-0.7 em BLE 4.2 do DevKitC).
   Video utilizavel (>=480p) precisa de **WiFi**. *(confirmado)*
5. **VLM offline no celular para "foto + pergunta" e viavel** em 2025-2026 (Gemma 3n E2B INT4),
   mas os numeros bons (~24 tok/s, ~2.5s/imagem) sao de **flagships**; em mid-range cai para
   5-15 tok/s, RAM no limite (>=6-8GB) e TTFT de imagem de varios segundos. *(confirmado, com nuance)*
6. **Teensy 4.x e a escolha errada**: zero radio nativo (viraria "Teensy+ESP32", redundante)
   e UVC host so experimental. O MCU certo e o **ESP32-S3**. *(confirmado)*

## Decisao

### Estrategia em DUAS FASES

Separar "validar o cerebro" (maior risco: NPU do celular, latencia fim-a-fim, qualidade
VLM/TTS em PT-BR) de "construir o cliente-fino" (decisoes de hardware caras), para nao
misturar riscos nao validados com compras irreversiveis.

- **Fase 1 — Cerebro no celular** (sem firmware novo, sem comprar nada): app Android Kotlin
  com a webcam UVC plugada direto no celular por OTG valida TODO o pipeline (gestos + VQA + voz).
- **Fase 2 — Cliente-fino real**: oculos como sensor node ESP32-S3 com dois canais de radio.

### Pilar APP (cerebro) — detalhado em [[../referencias/app-cerebro-android-ondevice]]

- **Android nativo (Kotlin), Android-first.** Decidido pela camera: UVC externa via OTG so
  funciona no Android (AUSBC/UVCCamera, sem root); iPhone nao suporta (so iPadOS).
- Pipeline offline: camera -> **MediaPipe HandLandmarker** (21 landmarks, port 1:1 de `hands.py`)
  -> orquestracao em corrotinas (state machine derivada de `control.py`, quebrada por
  responsabilidade) -> **Gemma 3n E2B (INT4, multimodal)** via **LiteRT-LM** + NPU (QNN) ->
  **STT** whisper.cpp/Vosk + **TTS** Piper pt_BR (sherpa-onnx). Gemini cloud = fallback opt-in.
- Persona PT-BR de `jarvis.py` vira system prompt reutilizavel; `manager.py` (upload Photos)
  e descartado/opt-in por contrariar a privacidade.

### Pilar FIRMWARE — detalhado em [[../referencias/audio-i2s-esp32-mems-max98357a-conducao-ossea]] e [[../referencias/ble-wifi-video-audio-esp32]]

- **ESP-IDF em C/C++** (nao Arduino): controle fino de PSRAM, DMA da camera, dual-core e
  power management.
- O MCU **nunca roda IA pesada**; so captura/encaminha: camera DVP -> MJPEG por WiFi (sob
  demanda), audio I2S bidirecional (mic + saida class-D), wake word local (ESP-SR/WakeNet),
  gestos de cabeca via IMU.
- **Dois canais**: BLE GATT always-on (controle/eventos/voz Opus 16k) + WiFi/WebSocket sob
  demanda (video). Sem video por BLE; sem A2DP/SBC para audio (latencia ~500ms).

### Pilar HARDWARE — detalhado em [[../referencias/camera-esp32-csi-dvp-uvc]] e [[../referencias/energia-mcu-esp32s3-cliente-fino]]

- **MCU final: ESP32-S3 N16R8** (16MB flash / 8MB PSRAM) — unico chip com WiFi+BLE5+DVP+
  USB-OTG+I2S+PSRAM. DevKitC classico vai para bancada.
- **Camera: OV2640 DVP** (2MP, JPEG por HW), captura modesta (VGA@15fps / 480x320@30fps em
  MJPEG) — suficiente para VQA. 1080p continuo impossivel no S3 (sem encoder HW; teto ~720p);
  ESP32-P4 fica registrado como evolucao futura.
- **Audio**: MAX98357A do dono (entrada I2S, saida class-D = ja e DAC+amp) drivando o exciter
  de conducao ossea 4 ohm direto, com ganho limitado. Mic MEMS I2S (INMP441/ICS-43434, 3.3V).
  **CONFIRMAR a sigla impressa no amp** antes de fechar (pode ser PCM5102/PAM8403).
- **Energia**: arquitetura event-driven (captura sob gesto + deep sleep, nunca video 24/7),
  PMIC LiPo baixo Iq, bateria 150-300 mAh. DevKitC drena 5-15 mA parado -> produto exige
  WROOM-S3 bare/PCB custom.
- **IMU novo** para gestos de cabeca (canal de banda ~zero por BLE), hibrido com visao.

## BOM — veredito item a item

| Componente | Decisao | Por que |
|---|---|---|
| ESP32 DevKitC classico | reaproveitar em bancada | Sem USB-OTG, standby 5-15 mA, PSRAM apertada |
| Camera CSI Mini 5MP | reaproveitar em bancada (Pi 3) | MIPI CSI-2 Pi-only para este modulo |
| Webcam UVC USB 1080p | reaproveitar em bancada (celular, Fase 1) | Peca certa para validar o cerebro via OTG |
| Amp "digital/analogico" | manter (confirmar sigla) | Provavel MAX98357A; serve no produto |
| Exciter conducao ossea | manter | 4 ohm compativel direto com o amp |
| Microfone | trocar | Adotar mic MEMS I2S (INMP441/ICS-43434) |
| DCDCs | reaproveitar em bancada | Produto pede DCDC baixo Iq / PMIC |
| Raspberry Pi 3 | reaproveitar em bancada | Inviavel na cabeca (1.4-4.7W, ~68C) |
| ESP32-S3 N16R8 | adicionar | MCU do produto |
| OV2640 (DVP) | adicionar | Caminho de camera nativo do S3 |
| IMU (MPU-6050/BNO055) | adicionar | Gestos de cabeca via BLE |
| PMIC LiPo + bateria 150-300 mAh | adicionar | Energia do cliente-fino |
| `manager.py` / Gemini cloud | descartar / fallback | Contrariam privacidade/offline |

## Roadmap

0. **Fase 0** — Confirmar a sigla do amp (foto); definir celular Android de referencia
   (Snapdragon recente, NPU, >=8GB RAM); comprar ESP32-S3 N16R8, OV2640, ICS-43434, IMU,
   PMIC LiPo + bateria.
1. **Fase 1** — Cerebro no celular (Android Kotlin): AUSBC (webcam UVC OTG) -> MediaPipe
   HandLandmarker (5 gestos port 1:1) -> orquestracao em corrotinas -> Gemma 3n E2B via
   LiteRT-LM/NPU -> STT whisper.cpp/Vosk + TTS Piper pt_BR.
1b. **Fase 1b** — Piloto empirico PT-BR: medir latencia fim-a-fim, tok/s, WER e qualidade
   do VQA/TTS em portugues no device-alvo. **Go/no-go do modelo** antes de congelar.
2. **Fase 2** — Firmware base no ESP32-S3 (ESP-IDF): camera DVP -> MJPEG por WiFi (SoftAP
   ponto-a-ponto); audio I2S; BLE GATT; WakeNet local. Conectar ao app da Fase 1.
3. **Fase 3** — Hibrido visao+IMU + power: IMU por BLE, duty-cycle event-driven, validacao
   de energia com power profiler (Nordic PPK2), EQ de agudos no TTS.
4. **Fase 4** — Hardenizacao: PCB custom (WROOM-S3 bare + PMIC), mecanica/ergonomia (<50g),
   BMS/seguranca da LiPo, certificacao de radio (Anatel/FCC/CE). Avaliar ESP32-P4 se
   1080p/H.264 virar requisito firme.

## Alternativas consideradas

- **App cross-platform (Flutter/RN/KMP)** — descartado: UVC externo nao funciona no iPhone
  (quebra o requisito de camera no iOS); cross-platform adiciona camada sem remover o gargalo
  nativo (UVC + NPU + MediaPipe). KMP so quando houver necessidade concreta.
- **Webcam UVC direto no celular tambem no PRODUTO** — so na Fase 1: no produto exigiria cabo
  USB-C (quebra "wireless").
- **Webcam UVC host no ESP32-S3** — descartado: USB Full-Speed trava em ~640x480@15fps sem
  ganho frente ao DVP nativo.
- **nRF52/nRF53 ou Teensy** — descartados para o caminho de video (nRF sem WiFi/camera;
  Teensy sem radio). nRF53 so se virasse audio-first sem camera nos oculos.
- **ESP32-P4 agora** — adiado: tem MIPI-CSI + H.264 HW (1080p real) mas nao tem radio proprio
  (precisa de co-processador C6/C5) e ecossistema mais novo. Evolucao futura.
- **Gemini Nano (ML Kit) / Apple Foundation Models** — caminhos "de sistema" opcionais por
  plataforma, nao base de produto (NPUs especificas, alpha, iOS-only, PT vs PT-BR incerto).

## Consequencias

### Positivas
- Topologia confirmada por numeros e por benchmark de mercado (Ray-Ban Meta: 154 mAh, 50.8g,
  3-4h, processamento pesado no celular).
- Fase 1 valida o maior risco (cerebro) sem gastar em hardware novo.
- Caminho de hardware enxuto e portavel (ESP32-S3 carrega prototipo -> produto sem retrabalho).

### Negativas / riscos
- Camera CSI 5MP e (no produto) a webcam UVC viram hardware de bancada — parte da BOM atual
  nao vai para os oculos.
- Qualidade do VLM/TTS em PT-BR nao comprovada -> piloto empirico obrigatorio (Fase 1b).
- Fragmentacao de hardware do celular: experiencia plena so em flagships; mid-range = modo
  degradado / fallback cloud opt-in.
- Lock-in no Google AI Edge (LiteRT-LM ja migrou uma vez) -> isolar inferencia atras de interface.
- Latencia conversacional composta e termica do wearable a validar com medicao real.

## Referencias

- [[../referencias/camera-esp32-csi-dvp-uvc]]
- [[../referencias/ble-wifi-video-audio-esp32]]
- [[../referencias/vlm-offline-celular-gemma3n-stt-tts-ptbr]]
- [[../referencias/audio-i2s-esp32-mems-max98357a-conducao-ossea]]
- [[../referencias/energia-mcu-esp32s3-cliente-fino]]
- [[../referencias/app-cerebro-android-ondevice]]
- [[../CONVENCOES]]
