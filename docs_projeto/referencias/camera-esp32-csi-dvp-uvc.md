---
title: Camera no ESP32 - CSI vs DVP vs UVC e por que a CSI 5MP e Pi-only
source: https://docs.espressif.com/projects/esp-faq/en/latest/application-solution/camera-application.html + https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_host/usb_stream.html + https://github.com/espressif/esp-usb/issues/50 + https://www.cnx-software.com/2026/05/04/esp32-p4-esp32-c5-board-features-raspberry-pi-compatible-mipi-connectors-for-official-displays-and-camera-modules/
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
tags: [referencia, hardware, camera, esp32, csi, dvp, uvc, tema/arquitetura]
---

# Camera no ESP32 - CSI vs DVP vs UVC e por que a CSI 5MP e Pi-only

Resumo da pesquisa (fontes 2024-2026) para a dimensao **camera x ESP32** do produto.
Conclusao critica: **nenhuma das duas cameras que o dono possui casa bem com o ESP32.**

## Tres interfaces de camera, incompativeis entre si

| Interface | O que e | Quem aceita |
|---|---|---|
| **MIPI CSI-2** | serial diferencial de alta velocidade (FPC ribbon) | Raspberry Pi; ESP32-P4 (so OV5647); STM32N6. **NAO** ESP32/S3 |
| **DVP** | paralela 8-bit (D0-D7 + PCLK/HSYNC/VSYNC) | ESP32 / ESP32-S3 via `esp32-camera` (OV2640/OV5640) |
| **UVC (USB)** | webcam USB padrao | host USB: PC, Linux, Android (OTG), ESP32-S2/S3/P4 |

## A camera CSI 5MP "para Raspberry Pi" e Pi-only (para este hardware)

- Usa MIPI CSI-2; o ESP32 classico nao tem peripheral CSI e o S3 so tem DVP (paralelo).
  So o **ESP32-P4** tem MIPI CSI nativo — e mesmo assim limitado ao OV5647 original.
- Nao conecta direto no celular (FPC nao encaixa, sem driver).
- Existem adaptadores **CSI->USB UVC** (Arducam B0278), mas sao **casados com o modulo HQ
  IMX477**, nao com o Mini 5MP (provavel OV5647) do dono -> sem caminho pronto.
- **Veredito:** vai para **bancada no Raspberry Pi 3**.

## O ESP32 DevKitC classico NAO captura a webcam UVC

- O ESP32 original nao tem USB-OTG (a porta USB e so UART para flash). USB host so existe
  no **ESP32-S2/S3/P4**. *(verificado: confirmado)*

## Mesmo o ESP32-S3 tem UVC host limitado

- USB **Full-Speed** (12 Mbps), MPS travado em 512 bytes -> ~0.5 MB/s isocrono.
- Tetos reais: **640x480@15fps** ou **320x240@30fps**, sempre MJPEG, PSRAM >=2MB obrigatoria.
- **1080p esta fora de alcance** do S3 (so o ESP32-P4, com USB High-Speed, faz 1080p).

## Caminho recomendado: DVP nativo

- Sensor **OV2640** (2MP) com JPEG por hardware (ate UXGA@15fps) -> frame buffer em PSRAM ->
  **streaming MJPEG por WiFi**. Preferir ao OV5640 (5MP sem JPEG em HW, fps baixo).
- Benchmark ESP32-CAM: VGA ~14fps, QVGA ~44fps (HTTP MJPEG). FPV otimizado: 640x480@30-50fps,
  latencia 90-110ms, ~8-10 Mbps.

## A webcam UVC e a peca CERTA na Fase 1

- Plugada direto no **celular Android** via OTG (lib AUSBC, sem root) valida TODO o cerebro
  sem ESP32 no caminho de camera e sem comprar nada. No produto (Fase 2) o caminho e DVP nativo.

## Para o projeto Jarvis

- CSI 5MP -> bancada (Pi 3). DevKitC -> sem camera USB. Produto -> **ESP32-S3 + OV2640 DVP**.
  Webcam UVC -> validacao no celular (Fase 1). Ver [[../decisoes/2026-06-27_arquitetura_tres_pilares]].
