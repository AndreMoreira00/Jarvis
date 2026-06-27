---
title: Energia e MCU do cliente-fino - ESP32-S3, standby do DevKitC e bateria de wearable
source: https://hubble.com/community/guides/esp32-deep-sleep-current-what-the-datasheet-says-vs-what-you-ll-actually-measure/ + https://lastminuteengineers.com/getting-started-with-esp32-cam/ + https://www.pjrc.com/store/teensy41.html + https://www.everythingusb.com/ray-ban-meta-smart-glasses.html + https://www.espressif.com/en/products/socs/esp32-s3
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
tags: [referencia, hardware, energia, mcu, esp32-s3, teensy, bateria, tema/portabilidade]
---

# Energia e MCU do cliente-fino - ESP32-S3, standby do DevKitC e bateria de wearable

Resumo da pesquisa (fontes 2024-2026) para as dimensoes **energia/portabilidade** e
**escolha de MCU** do produto.

## MCU: ESP32-S3 ganha (Teensy e nRF descartados)

| MCU | WiFi | BLE | Camera nativa | Veredito |
|---|---|---|---|---|
| **ESP32-S3** | sim 2.4GHz | sim BLE5 | DVP (OV2640/OV5640) + USB-OTG | **Escolhido** (unico que junta tudo + I2S + PSRAM) |
| Teensy 4.x | nao | nao | so UVC experimental | Descartado (zero radio -> "Teensy+ESP32" redundante) |
| nRF52/nRF53 | nao | sim (otimo) | nao | So se audio-first sem camera |
| ESP32-P4 | nao (precisa co-radio) | nao | MIPI-CSI + H.264 HW | Evolucao futura (1080p real) |

- Placa alvo: **ESP32-S3 N16R8** (16MB flash / 8MB PSRAM). PSRAM e obrigatoria para bufferizar
  frames de camera. SDK: **ESP-IDF C/C++** (controle de PSRAM/DMA/dual-core/power).
- *(verificado: confirmado que Teensy nao tem radio nativo e que o S3 e o MCU adequado.)*

## O DevKitC classico do dono e inadequado como cliente-fino

- **Standby real 5-15 mA** (LDO AMS1117 ~5mA + USB-UART CP2102 2-5mA + LED 2-3mA) vs **7 µA**
  do chip nu — uma bateria de 150 mAh morre em 10-30h **so parada**.
- Sem USB-OTG (nao captura UVC), PSRAM/SRAM apertada. -> **bancada**, nao produto.
- Produto exige **modulo WROOM-S3 bare / PCB custom + PMIC** de baixo Iq (alvo standby <200 µA).

## O maior dreno: WiFi/video continuo

- Streaming MJPEG por WiFi: **130-260 mA continuos**, picos de TX 180-310 mA, ESP32-CAM chega
  a ~71C em streaming continuo.
- Bateria leve de oculos (150-300 mAh, 4-12g) **nao sustenta video continuo >~1h**.
- **Solucao: arquitetura event-driven** — captura sob gesto/wake + deep sleep entre eventos,
  **nunca video 24/7**. Capacitor de bulk para os picos de TX (evita brownout).

## Bateria e ergonomia

- Conforto: oculos em **35-50g** (>80g cansa). LiPo 150 mAh ~4-10g.
- PMIC com carga LiPo CC/CV + protecao (OV/UV/OC/curto/temp) integrada — celulas pequenas
  geralmente sem termistor. DCDC boost 3.7->5V de alta eficiencia e baixo Iq.
- **Validar** os tres estados (deep sleep / BLE idle / WiFi burst) com power profiler (Nordic PPK2).

## Por que o Raspberry Pi nao vai na cabeca

- Pi 3: **1.4-2W idle, 3.7-4.7W sob carga, ~68C, fonte 2.5A**. Igualar 3-4h sob carga pediria
  ~4300 mAh (dezenas-centenas de g) + calor encostado na pele. -> **bancada**.

## Benchmark de mercado valida a tese tethered

- **Ray-Ban Meta**: 154 mAh, 50.8g, 3-4h; mesmo com silicio custom, o processamento pesado
  fica no celular. Confirma "oculos = cliente fino + celular = cerebro".

Ver [[../decisoes/2026-06-27_arquitetura_tres_pilares]] e [[ble-wifi-video-audio-esp32]].
