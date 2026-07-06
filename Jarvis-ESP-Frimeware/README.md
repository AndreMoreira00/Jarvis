# Jarvis — Firmware (cliente-fino ESP32-S3)

Firmware dos oculos inteligentes Jarvis (ESP-IDF, C/C++). O MCU e um **cliente-fino**: captura,
encaminha e atua — **nunca** faz percepcao nem IA (isso vive no app Android; ver o repo). Plano
completo em [docs_projeto/decisoes/2026-06-29_plano_firmware_esp32s3.md](../docs_projeto/decisoes/2026-06-29_plano_firmware_esp32s3.md)
e contrato BLE em [.../2026-06-29_contrato_ble_gatt_proposta.md](../docs_projeto/decisoes/2026-06-29_contrato_ble_gatt_proposta.md).

- **Placa alvo:** ESP32-S3 N16R8 (16MB flash / 8MB PSRAM octal).
- **SDK:** ESP-IDF (validado p/ NimBLE em v5.5+/v6.0).

## Estrutura (1 componente por subsistema)

| Caminho | Papel | Estado |
|---|---|---|
| `main/` | Entry fino → `app_core_start()` | ✅ |
| `components/jarvis_common/` | Tipos do contrato interno + versao de protocolo (folha pura) | ✅ |
| `components/app_core/` | Composition root FINO + orquestrador de eventos | ✅ |
| `components/ble/` | **GATT server NimBLE — plano de controle** (1º subsistema real) | ✅ |
| `components/camera/` | OV2640 DVP → JPEG/HW → PSRAM (sob demanda) | stub |
| `components/audio/` | I2S: mic MEMS + MAX98357A → conducao ossea | stub |
| `components/wake_word/` | WakeNet9s local (ESP-SR) | stub |
| `components/imu/` | Gestos de cabeca (MPU-6050/BNO055) → evento BLE | stub |
| `components/power/` | Sleep event-driven + bateria | stub |
| `components/wifi_stream/` | SoftAP + WebSocket MJPEG (sob demanda) | stub |

**Regra de dependencia:** acoplamento aponta para baixo. `app_core` (topo) depende de todos;
ninguem depende de `app_core`. Drivers sao folhas (so `jarvis_common`) e publicam eventos por
callback injetado (inversao de dependencia). Excecoes de **dado**: `wake_word`→`audio`, `wifi_stream`→`camera`.

## Build

Toolchains ja estao em `C:\Espressif`. Se a venv Python da IDF faltar, rode o `install` uma vez.

```powershell
$env:IDF_TOOLS_PATH = "C:\Espressif"
. C:\esp\v6.0.1\esp-idf\export.ps1
idf.py set-target esp32s3      # use 'esp32' p/ validar o plano de controle no DevKitC
idf.py build
idf.py -p <PORTA> flash monitor
```

> Tambem da p/ usar a extensao **ESP-IDF do VS Code** (ambiente proprio, build em um clique).

## Bring-up esperado (monitor serial)

```
jarvis: Jarvis firmware (cliente-fino ESP32-S3) | proto v=1
power/imu/audio/wake_word/camera/wifi_stream: stub init (...)
ble: init, advertising as Jarvis-Glasses
app_core: graph built (8 componentes); boot completo
app_core: state=BLE_IDLE hb conn=0      (a cada ~5s)
```

Com um app BLE (ex.: nRF Connect): conectar → ler **Battery Level (0x2A19)** → escrever **HELLO**
(`01 01`) na **Handshake** → receber **HELLO_ACK** (`81 01 ...`). O heartbeat tambem dispara
notificacoes de bateria/telemetria — exercita o caminho `app_core → ble notify` ponta-a-ponta.

## Proximos passos

Ver o roadmap no plano: IMU → audio+wakeword → camera+wifi_stream → power → voz por WiFi → hardenizacao.
