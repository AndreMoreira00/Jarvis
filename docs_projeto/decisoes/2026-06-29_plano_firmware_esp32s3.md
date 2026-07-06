---
title: Plano de implementacao do firmware ESP32-S3 (cliente-fino)
type: decisao-repo
status: aprovado
date: 2026-06-29
created: 2026-06-29
updated: 2026-06-29
project: Jarvis
tags: [decisao, firmware, esp32-s3, esp-idf, ble, nimble, arquitetura, tema/arquitetura]
---

# Plano de implementacao do firmware ESP32-S3 (cliente-fino)

Plano de construcao do firmware dos oculos em [Jarvis-ESP-Frimeware/](../../Jarvis-ESP-Frimeware/),
derivado dos requisitos dos tres pilares ([[2026-06-27_arquitetura_tres_pilares]]) e da
separacao de repos ([[2026-06-28_separacao_repos_firmware_app]]). Define **o que vira C/C++ no
firmware**, **o que pertence ao app (cerebro)**, a **arquitetura de componentes** e o **roadmap**.

Produzido com pesquisa multi-agente + **verificacao adversarial** (6 agentes): a verificacao
refutou pontos do desenho cru (sdkconfig PSRAM, init do NimBLE, gesto de mao no canal errado,
encoding de MTU, contradicao energia) — todos corrigidos e anotados abaixo.

## Decisoes desta sessao (travadas com o dono)

| Dimensao | Escolha |
|---|---|
| Entrega | Plano + esqueleto + **1º subsistema real: BLE GATT (plano de controle)** |
| Placa alvo | **ESP32-S3 N16R8** desde o inicio (16MB flash / 8MB PSRAM octal) |
| "Pronto" = | `idf.py build` OK + fronteiras de componente documentadas + bring-up (sinal de vida por subsistema) |
| Contrato oculos<->app | **Proposta do lado firmware** aqui (a fonte da verdade futura e o repo Jarvis-APP) |
| Estrutura | **1 componente ESP-IDF por subsistema** |

## Principio reitor (nao violar)

O **MCU nunca faz percepcao nem IA**. O firmware so **captura, encaminha e atua**. Toda
visao computacional (gestos de mao), STT, VLM/LLM e TTS vivem **no celular** (privacidade/offline
e a restricao nº1). O firmware origina apenas dois sinais "inteligentes", ambos baratos e locais:
**gesto de cabeca (IMU)** e **wake word (ESP-SR)**.

## O que vira C/C++ no firmware vs o que vai pro app

Mapa derivado item a item do MVP Python `src/jarvis` (que permanece como **spec executavel**).

### Fica no FIRMWARE (C/C++, ESP-IDF)

| Origem (spec Python) | Papel no firmware | Componente |
|---|---|---|
| `capture.py::capture_photo` (captura crua) | Dispara 1 frame JPEG (OV2640 DVP→HW JPEG→PSRAM) sob comando | `camera` |
| `capture.py::capture_video` (captura crua) | Serve frames MJPEG por WiFi enquanto a janela esta aberta | `camera`+`wifi_stream` |
| `capture.py::capture_audio` (**so o PCM**, nao o STT) | Captura PCM 16k do mic MEMS I2S; Opus p/ transporte | `audio` |
| `capture.py::play_confirmation_sound` | Tons locais de confirmacao via MAX98357A→conducao ossea | `audio` |
| `state.py::RuntimeState` | Mutex de recurso (camera/radio) + flag de janela de stream | `app_core` |
| `loop.py::gesture_cooldown` | Debounce do **evento de gesto de cabeca** (IMU) antes do BLE | `imu`+`app_core` |

### Vai para o APP (cerebro), NAO firmware

`gestures.py` (classificacao de 21 landmarks), `hands.py` (MediaPipe Hands), `loop.py::checks`
+ `check_gesture` (mapa gesto→acao / despacho), `flows.py` (state machine de assistente),
`capture.py::recognize_google` (STT → whisper.cpp/Vosk offline), `jarvis.py` (Gemini → Gemma 3n
on-device; edge-tts → Piper pt-BR), gestao de cache do modelo.

### DESCARTADO (privacidade/offline) ou andaime de runtime

`manager.py` inteiro (upload Google Photos/OAuth), `config.py` (chave/modelo Gemini, segredos
OAuth, voz/arquivo edge-tts), `loop.py` (cv2.VideoCapture/imshow/janela desktop),
`async_bridge.py`/`app.py::build`/pygame (wiring especifico do runtime Python — cada lado tem o seu).

### SPEC COMUM / contrato (vocabulario compartilhado entre os dois repos)

- **Enum dos 5 gestos de mao** {OK, POSITIVO, SPEAK, L, ROCK} + handedness — o **app** reconhece
  e emite; serve de vocabulario. (Gesto de **cabeca** via IMU e um enum separado, esse nasce no firmware.)
- **Mapa gesto→acao** (OK→foto; positivo→video; speak→voz; L→foto+voz; rock→video+voz) — semantica
  de produto do app; a **acao** resultante (capturar/abrir stream/abrir audio) e um comando do contrato.
- **PERSONA_PROMPT** — vira o system prompt do modelo on-device (Gemma 3n) no app.
- **Protocolo de inferencia** (texto / imagem+texto / video+texto) — informa que midia o firmware entrega.

## Arquitetura de componentes (ESP-IDF)

10 componentes (8 subsistemas + `app_core` + `jarvis_common`); `main/` so tem o entry.

```
main/                  entry fino -> app_core_start()
components/
  jarvis_common/       tipos do contrato interno + versao de protocolo (folha pura)
  app_core/            composition root FINO + orquestrador de eventos (state machine)
  ble/                 GATT server NimBLE (plano de controle)        <-- 1º REAL
  camera/   audio/   wake_word/   imu/   power/   wifi_stream/        <-- stubs
```

**Regra de dependencia** (acoplamento aponta para baixo, DAG sem ciclos — verificado):

- `app_core` (topo) pode depender de todos; **ninguem depende de `app_core`**.
- `jarvis_common` (base) nao depende de ninguem; todos dependem dele.
- Drivers (`camera/audio/imu/power/ble`) sao **folhas**: dependem so de `jarvis_common`,
  nunca de `app_core` nem de outro driver. Publicam eventos por **callback injetado no init**
  (inversao de dependencia) — em compile-time nao incluem `app_core.h`.
- Duas excecoes documentadas, por consumo de **dado** (nao controle): `wake_word`→`audio`
  (consome PCM) e `wifi_stream`→`camera` (consome JPEG).

### Modelo de tasks (FreeRTOS)

| Task | Core | Prio | Papel |
|---|---|---|---|
| `ble_host_task` | 0 | 6 | Host NimBLE (radio/protocolo) — criada pela stack |
| `orchestrator_task` | 0 | 5 | Coracao do `app_core`: drena a fila central e roteia |
| `audio_capture_task` | 1 | 5 | PCM do mic 16k → wake_word / consumidor (futuro) |
| `imu_task` | 1 | 4 | Poll I2C + classificador de gesto de cabeca (futuro) |
| `capture_task` | 1 | 4 | Captura sob demanda → wifi_stream (futuro) |
| `power_mon_task` | 0 | 2 | Bateria + gate de deep sleep (futuro) |

Core0 = radio/protocolo; Core1 = sensores/captura (reserva 1 nucleo p/ o codec Opus, ~70-80% de 1 core).
IPC: **fila central unica** (`g_event_queue`) para o orquestrador; `ble_tx_queue` p/ nao bloquear
no contexto do host; **event group** para o gate de deep sleep (nao dormir no meio de uma captura).

### State machine de energia (event-driven)

`deep_sleep` → `ble_idle` → {`wake_listening`, `capture_active` → `wifi_burst`} → `ble_idle`.
Captura **sob gesto/comando + deep sleep entre eventos**; **nunca video 24/7**.

> **Correcao da verificacao (energia):** "BLE always-on" e "<200uA" sao **dois regimes**, nao
> simultaneos. **EM USO** = BLE conectado, consumo na casa de **mA** (`ble_idle`). **GUARDADO** =
> `deep_sleep` com **BLE desconectado** + advertising lento / wake-on-GPIO, ai sim **<200uA**. O
> `<200uA` e o standby de produto guardado, nao o `ble_idle`. Falta definir: timeout
> `ble_idle`→`deep_sleep`, comportamento da conexao ao dormir, e custo de reconexao. Wake por gesto
> exige **INT pin do IMU → GPIO wake** (o ULP nao faz poll I2C trivial).

## Primeiro subsistema real: BLE GATT (plano de controle)

Implementado de verdade no componente `ble` (NimBLE, ESP-IDF v6.0/v5.5). Detalhe do contrato em
[[2026-06-29_contrato_ble_gatt_proposta]]. Resumo: **JarvisService** (128-bit) com characteristics
**Handshake** (protocolVersion), **Control** (comandos do app), **Events** (gesto de cabeca + wakeword),
**Telemetry** (estado rico) + **Voice** (Opus 16k, impl deferida); mais o **Battery Service 0x180F**
padrao para a % de bateria. Handshake **fail-closed** (sem HELLO valido em 5s → desconecta).

### Correcoes aplicadas (apontadas pela verificacao adversarial)

1. **IDF/NimBLE**: `nimble_port_init()` (a antiga `esp_nimble_hci_and_controller_init` foi removida
   no IDF 5.0); `ble_store_config_init()` agora e chamado **e** tem forward-declare (sem header
   publico → senao quebra o build); `nimble_port_init` checado **sem `ESP_ERROR_CHECK`** (oculos
   sem porta de debug nao pode `abort()`).
2. **sdkconfig PSRAM/flash**: removido o `QIO@80M` fixo + `TYPE_AUTO` (combinacao invalida no N16R8;
   conflito de clock flash-quad × PSRAM-octal). Mantido `SPIRAM_MODE_OCT` (obrigatorio no R8);
   modo/freq de flash no default seguro do IDF. **Confirmar em hardware via menuconfig.**
3. **Particoes**: tabela com folga real (storage 4MB; fim em 0xF20000 < 16MB).
4. **Contrato — gesto de mao**: **removido** do canal Events (uplink). Gesto de mao nasce no celular
   (MediaPipe); Events carrega so o que nasce no firmware (IMU + wakeword). Se o app precisar
   reinjetar, isso e um `cmd_id` em Control, nao um event_type de uplink.
5. **Contrato — MTU**: HELLO_ACK carrega o ATT_MTU efetivo em **bytes (uint16)**, nao `/4` (que nao
   representa 247 sem perda).

## Roadmap (ordem de subsistemas)

0. **(feito)** Esqueleto compila + componentes + bring-up + **BLE plano de controle real**.
1. **IMU** (`imu`): I2C + classificador de gesto de cabeca → evento BLE (prova `imu→app_core→ble`
   ponta-a-ponta com hardware barato; banda ~zero).
2. **Audio + wake word** (`audio`, `wake_word`): I2S mic + MAX98357A; WakeNet9s local abre a janela de voz.
3. **Camera + WiFi stream** (`camera`, `wifi_stream`): OV2640 DVP → MJPEG por SoftAP sob demanda.
4. **Power**: deep sleep event-driven, wake-on-GPIO (INT do IMU), validacao com power profiler (PPK2).
5. **Voz primario por WiFi** (reusa a sessao de video) + EQ de agudos no TTS do app.
6. **Hardenizacao**: seguranca do SoftAP derivada da sessao BLE (LESC+HKDF), OTA, PCB custom.

## Advogado do diabo (riscos e alternativas)

- **Targetizar S3 sem ter a placa.** Voce so tem o DevKitC classico; o BLE so roda de verdade ao
  comprar o S3. *Mitigacao:* o componente `ble` e **target-agnostico** — da p/ validar o plano de
  controle HOJE no DevKitC com `idf.py set-target esp32`. *Alternativa rejeitada:* comecar tudo no
  DevKitC trava camera/USB e gera retrabalho de sdkconfig/particoes.
- **Contrato pode divergir do app.** A proposta aqui pode conflitar com o `Contrato_Comunicacao_Oculos.md`
  do repo do app. *Mitigacao:* `protocolVersion` + marcado **PROPOSTA** + disciplina de sync.
  *Alternativa rejeitada:* esperar o app (trava o 1º subsistema sem ganho real).
- **IDF v6.0.1 vs v5.5.** A verificacao recomenda v5.5 ("evite v6.0 em producao"); voce tem a v6.0.1
  instalada. A sequencia NimBLE e identica desde a v5.0, entao o codigo serve aos dois. *Risco
  residual:* mudancas pontuais de v6.0 — mitigado validando o build. Se preferir estabilidade, instalar
  a v5.5 em paralelo e so trocar o `idf.currentSetup`.
- **Voz por BLE vs WiFi.** Decidido **WiFi primario / BLE fallback** — o gargalo e CPU (Opus encode),
  nao banda (Opus 32kbps cabe ~40× no teto BLE). L2CAP CoC rejeitado (ecossistema Android irregular).

## Setup e build

Pre-requisito (uma vez): a venv Python da ESP-IDF v6.0.1. Os toolchains ja estao em `C:\Espressif`.

```powershell
# Opcao A: extensao ESP-IDF do VS Code (ambiente proprio) — recomendada p/ o dia a dia.
# Opcao B: linha de comando
$env:IDF_TOOLS_PATH = "C:\Espressif"
. C:\esp\v6.0.1\esp-idf\export.ps1          # (rode install.ps1 / install-python-env antes, se a venv faltar)
cd Jarvis-ESP-Frimeware
idf.py set-target esp32s3
idf.py build
idf.py -p <PORTA> flash monitor             # exige a placa S3 fisica
```

Bring-up esperado no monitor serial: banner `proto v=1`, `power/imu/audio/wake_word/camera/wifi_stream:
stub init`, `ble: init, advertising as Jarvis-Glasses`, e o heartbeat `app_core: state=BLE_IDLE hb`.
Com um app BLE (nRF Connect): conectar → ler Battery Level (0x2A19) → escrever HELLO na Handshake →
receber HELLO_ACK.

## Referencias

- [[2026-06-27_arquitetura_tres_pilares]] · [[2026-06-28_separacao_repos_firmware_app]]
- [[2026-06-29_contrato_ble_gatt_proposta]]
- [[../referencias/ble-wifi-video-audio-esp32]] · [[../referencias/audio-i2s-esp32-mems-max98357a-conducao-ossea]]
- [[../referencias/camera-esp32-csi-dvp-uvc]] · [[../referencias/energia-mcu-esp32s3-cliente-fino]]
