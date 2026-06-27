---
title: Audio I2S no ESP32 - mic MEMS, MAX98357A e conducao ossea
source: https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf + https://www.daytonaudio.com/images/resources/240-614--dayton-audio-bce-1-bone-conducting-exciter-spec.pdf + https://easyelecmodule.com/a-complete-guide-to-the-inmp441-i2s-microphone/ + https://github.com/espressif/esp-sr/blob/master/README.md
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
tags: [referencia, firmware, hardware, audio, i2s, conducao-ossea, esp32, tema/audio]
---

# Audio I2S no ESP32 - mic MEMS, MAX98357A e conducao ossea

Resumo da pesquisa (fontes 2024-2026) para a dimensao **audio** do produto. Toda a cadeia
gira em torno do barramento **I2S** em ambas as pontas.

## Captura: microfone MEMS digital I2S

- **INMP441** (ou, melhor, **ICS-43434** por menor ruido): MEMS + ADC + filtro integrados,
  saida I2S 24-bit direto no ESP32, **sem ADC externo**. Funciona ate no ESP32 classico (I2S
  e do SoC base). **Alimentar em 3.3V** (5V danifica). INMP441: 60Hz-15kHz, SNR 61 dB(A).

## Reproducao: o amp "digital/analogico" do dono e provavelmente um MAX98357A

- **MAX98357A**: amplificador class-D com **entrada I2S** e **saida filterless** — ja faz a
  conversao D/A internamente, **dispensa DAC externo**. Casa com a descricao "digital/analogico".
  - 2.7-5.5V, ate **3.2W em 4 ohm** @5V; sample rate 8-96kHz; ganho 3-15dB (resistor no pino).
- **AVISO**: confirmar a sigla impressa no modulo. Se for **PCM5102** (DAC puro, saida linha)
  ou **PAM8403** (amp analogico), a topologia muda (exigiria DAC). *(risco registrado)*

## Conducao ossea: compativel direto, sem amp dedicado

- Exciter tipico (ex. **Dayton BCE-1**): **4 ohm, 1W RMS / 2W max**, Re=3.99 ohm. Liga **direto**
  em OUTP/OUTN do MAX98357A, sem driver especial.
- **Limitar ganho/volume**: o amp entrega ate 3.2W e o exciter aguenta ~1W -> risco de distorcao/dano.
- Inteligibilidade de voz suficiente (a fala vive em ~100-500Hz); agudos atenuam pelo osso ->
  aplicar **EQ de realce de agudos no TTS** do celular.
- MAX98357A e **MONO**: estereo exigiria dois. Para assistente de voz, mono basta.

## Fluxo no cliente-fino

- O **celular** faz STT + LLM + TTS e envia o audio **ja sintetizado** ao ESP32, que so
  decodifica e toca (passthrough I2S). PCM 16kHz/16-bit mono ~32 KB/s; preferir **Opus 16k**.
- Transporte por **WiFi** (A2DP/SBC tem ~500ms de latencia — ver [[ble-wifi-video-audio-esp32]]).

## Wake word local

- **ESP-SR / WakeNet** roda no proprio ESP32 (WakeNet9s ate sem PSRAM; folga no S3, deteccao
  ~80ms) — abre o stream so apos a palavra-chave (poupa banda/energia, reforca privacidade).
  O **STT completo fica no celular**. Para rua, avaliar 2 mics + AEC (ESP-SR AFE) -> reforca o S3.

Ver [[../decisoes/2026-06-27_arquitetura_tres_pilares]].
