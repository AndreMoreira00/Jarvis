---
title: Referencias externas
type: readme
status: aprovado
created: 2026-05-28
updated: 2026-05-28
tags: [readme, referencias]
---

# Referencias externas

Resumos de URLs, bibliotecas, normas ou conceitos citados durante o desenvolvimento que **nao** sao especificos a um projeto (esses ficam em `docs_Template_Projeto/10_Referencias/`).

> Regra 6 do projeto: se o usuario cita um link/biblioteca/conceito que o Claude nao domina, o Claude ingere via defuddle/WebFetch e salva um resumo aqui antes de prosseguir.

## Convencao

- Um arquivo por referencia: `<slug-da-referencia>.md`
- Frontmatter minimo: `title`, `source` (URL ou citacao), `type: referencia`, `tags`, `created`, `updated`
- Conteudo: resumo executivo + trechos relevantes citaveis + link/fonte

## Indice

- [[pytest-mock-total]] — padrao de mock total via `sys.modules` + stack pytest/pytest-cov/pytest-asyncio
- [[app-cerebro-android-ondevice]] — app cerebro: framework, camera UVC, LLM on-device, mapeamento do MVP Python
- [[camera-esp32-csi-dvp-uvc]] — camera no ESP32: CSI vs DVP vs UVC e por que a CSI 5MP e Pi-only
- [[ble-wifi-video-audio-esp32]] — BLE nao transmite video; WiFi obrigatorio; arquitetura de dois canais
- [[vlm-offline-celular-gemma3n-stt-tts-ptbr]] — VLM offline (Gemma 3n) + STT/TTS PT-BR on-device
- [[audio-i2s-esp32-mems-max98357a-conducao-ossea]] — cadeia de audio I2S: mic MEMS, MAX98357A, conducao ossea
- [[energia-mcu-esp32s3-cliente-fino]] — energia/MCU: ESP32-S3 vs Teensy/nRF, standby do DevKitC, bateria de wearable
