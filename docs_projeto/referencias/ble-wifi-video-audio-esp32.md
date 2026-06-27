---
title: BLE vs WiFi para video e audio no ESP32 (arquitetura de dois canais)
source: https://interrupt.memfault.com/blog/ble-throughput-primer + https://docs.espressif.com/projects/esp-faq/en/latest/software-framework/bt/ble.html + https://argenox.com/blog/bluetooth-le-throughput-max-performance + https://www.pschatzmann.ch/home/2022/04/28/arduino-low-latency-streaming-of-audio-data-codecs/
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
tags: [referencia, firmware, conectividade, ble, wifi, esp32, tema/comunicacao]
---

# BLE vs WiFi para video e audio no ESP32 (arquitetura de dois canais)

Resumo da pesquisa (fontes 2024-2026) para a dimensao **conectividade** do produto.

## BLE nao transmite video (verificado: confirmado)

| Link | Teto real (aplicacao) |
|---|---|
| BLE 1M PHY (BLE 4.2, varias revisoes do DevKitC) | ~0.5-0.7 Mbps |
| BLE 2M PHY + DLE + MTU max (BLE 5) | ~1.4 Mbps de pico (~0.8 medido na pratica) |
| Video utilizavel (>=480p) | 1.5-6 Mbps -> **exige WiFi** |

O limite e arquitetural do BLE (inter-frame spacing, overhead ATT/L2CAP), nao defeito do ESP32.
BLE serve para **controle, eventos de gesto, telemetria e voz comprimida** (~16-32 kbps cabe folgado).

## Video so por WiFi

- ESP32-CAM MJPEG: VGA ~14fps (HTTP simples), 640x480@30-50fps com 90-110ms de latencia em
  projetos FPV otimizados (~8-10 Mbps).
- Latencia ~100ms e aceitavel para captura+IA, marginal para feedback visual em tempo real.

## Audio tambem fica melhor em WiFi

- **A2DP/SBC (Bluetooth classico de musica): ~500ms de latencia** + rajadas -> inviavel para conversa.
- Usar **WiFi (TCP/WebSocket) com codec Opus 16kHz** para voz bidirecional.
- Opus no ESP32: decode ~30% de 1 nucleo @240MHz; encode 16kHz ~70-80% (usar fixed-point).

## Onde roda o reconhecimento de gestos

- **Migra do desktop para o celular**: MediaPipe HandLandmarker on-device (~12-17 ms/frame no
  Pixel 6), 100% offline = atende a privacidade. O oculos so envia video; o celular detecta o
  gesto; so o EVENTO (poucos bytes) dispara a acao.

## Arquitetura recomendada: DOIS CANAIS

- **BLE GATT always-on** (baixo consumo): controle, eventos de gesto, gesto de cabeca (IMU),
  voz comprimida.
- **WiFi/WebSocket sob demanda**: video MJPEG (~8-10 Mbps), ligado so na janela de captura
  para poupar bateria. WiFi ponto-a-ponto (SoftAP/Wi-Fi Direct) -> video nunca sai do par.
- Cuidado: BLE GATT + A2DP simultaneos causam artefatos de audio -> isolar perfis.

Ver [[../decisoes/2026-06-27_arquitetura_tres_pilares]] e [[energia-mcu-esp32s3-cliente-fino]].
