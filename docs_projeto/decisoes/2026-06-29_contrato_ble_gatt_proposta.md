---
title: Contrato BLE GATT oculos<->app — PROPOSTA do firmware (v1)
type: decisao-repo
status: proposto
date: 2026-06-29
created: 2026-06-29
updated: 2026-06-29
project: Jarvis
tags: [decisao, firmware, contrato, ble, gatt, nimble, proposta, tema/comunicacao]
---

# Contrato BLE GATT oculos<->app — PROPOSTA do firmware (v1)

> **Status: PROPOSTA.** A **fonte da verdade** do contrato oculos<->app e o repo **Jarvis-APP**
> (`docs_projeto/Jarvis_App/05_Software_Auxiliar/App_Mobile/Contrato_Comunicacao_Oculos.md`), por
> decisao de [[2026-06-28_separacao_repos_firmware_app]]. Como esse repo ainda nao publicou o contrato,
> o firmware propoe esta v1 para destravar o **plano de controle BLE** e a sincroniza quando o app
> publicar. O ponto de sincronizacao disciplinada e o campo **`protocolVersion`**.

Implementado em [components/ble/](../../Jarvis-ESP-Frimeware/components/ble/). Plano geral em
[[2026-06-29_plano_firmware_esp32s3]].

## Mapa de transporte (dois canais)

| Canal | Leva | Por que |
|---|---|---|
| **BLE GATT** (always-on, baixo consumo) | Controle: handshake, comandos, eventos (gesto de cabeca + wakeword), telemetria/bateria. Voz Opus 16k so em **fallback** voice-only. | Sempre ligado, poucos bytes. **Nunca** leva video (teto ~1.4 Mbps). |
| **WiFi/WebSocket** (SoftAP ponto-a-ponto, **sob demanda**) | Video MJPEG (~8-10 Mbps) e **voz Opus 16k primaria**. So na janela de captura. | Video so e viavel em WiFi; voz reusa a sessao ja de pe. Midia nunca sai do par (privacidade). |
| **Local no firmware** (nao sai por radio) | Deteccao de wakeword (WakeNet9s) e classificacao de gesto de cabeca (fusao IMU). | So o **evento** resultante sai por BLE — economia de radio + privacidade. |

## JarvisService (vendor 128-bit)

Base UUID **proposta**: `6a4e<NNNN>-b5a3-f393-e0a9-e50e24dcca9e` (`NNNN` = id curto; `0x0001` = service).
Anunciada no advertising junto do nome `Jarvis-Glasses` e do **Battery Service `0x180F`** padrao.

| Characteristic | UUID curto | Props | Direcao | Payload |
|---|---|---|---|---|
| **Handshake** | `0x0002` | write, read, notify | app↔oculos | WRITE 8B (HELLO); NOTIFY 12B (HELLO_ACK/REJECT) |
| **Control** | `0x0003` | write, write-no-rsp | app→oculos | TLV: `[0]=cmd_id [1]=arg_len [2..]=args` |
| **Events** | `0x0004` | notify | oculos→app | 8B fixo (gesto de cabeca / wakeword) |
| **Telemetry** | `0x0005` | read, notify | oculos→app | 12B (estado rico) |
| **Voice** | `0x0006` | notify, write-no-rsp | bidirecional | Frame Opus 16k — **impl deferida** |

Mais **Battery Level `0x2A19`** (read, notify) no `0x180F`: a **%** de bateria (fonte unica).

### Handshake (HELLO / HELLO_ACK)

- **WRITE (app→oculos), 8B:** `[0]=0x01 HELLO`, `[1]=app_proto_version`, `[2..3]=app_caps (uint16 LE)`,
  `[4..7]=reservado`.
- **NOTIFY (oculos→app), 12B:** `[0]=0x81 ACK | 0x8F REJECT`, `[1]=fw_proto_version`,
  `[2..3]=fw_caps`, `[4]=motivo` (0=ok, 1=versao incompativel), `[6..9]=session_id (uint32 LE)`,
  **`[10..11]=ATT_MTU efetivo em bytes (uint16 LE)`**.
- **Fluxo:** conexao → troca de MTU (alvo 247, util 244B) → app escreve HELLO → firmware compara
  `protocolVersion` (**fail-closed**: mismatch → REJECT + Control desabilitado) → app inscreve CCCD
  (Events/Telemetry/Battery) → Control liberado. **Sem HELLO valido em 5s → desconecta** (anti-zumbi).

> **Correcao da verificacao:** o MTU vai em **bytes (uint16)**, nao `/4` — `247/4` nao fecha sem perda.

### Events (so o que NASCE no firmware)

8B fixo: `[0]=event_type`, `[1]=event_code`, `[2]=flags`, `[3]=confidence(0..255)`,
`[4..5]=seq (uint16 LE, detecta perda)`, `[6..7]=ts_delta_ms (best-effort, satura)`.

- `event_type = 0x02` **GESTO_CABECA_IMU**: `1=NOD 2=SHAKE 3=TILT_L 4=TILT_R 5=LOOK_UP 6=LOOK_DOWN 7=DOUBLE_NOD`.
- `event_type = 0x03` **WAKEWORD**.

> **Correcao da verificacao:** **removido** o `0x01 GESTO_MAO`. Reconhecimento de gesto de mao roda
> **no celular** (MediaPipe) — coloca-lo num canal *oculos→app* feriria "o MCU nunca faz percepcao".
> O enum dos 5 gestos de mao permanece como **vocabulario compartilhado**; quando o app traduz um gesto
> reconhecido em acao, isso desce como **`cmd_id` em Control**, nao como evento de uplink.

### Control (comandos do app)

`cmd_id`: `0x10 START_WIFI_STREAM`, `0x11 STOP_WIFI_STREAM`, `0x20 CAPTURE_PHOTO`,
`0x30 START_VOICE`, `0x31 STOP_VOICE`, `0x40 SET_LED`, `0x50 SLEEP`, `0x60 SET_NOTIFY_MASK`, `0x70 PING`.

### Telemetry (estado rico) + Battery padrao

A **%** de bateria vai **sempre** no `0x2A19` padrao (hosts genericos leem de graca). O estado nao
padronizado vai na **Telemetry custom 12B**: `[0]=schema`, `[1]=state`, `[2]=charge_flags`,
`[3]=active_channel`, `[4]=temp_c (int8)`, `[5]=rssi_ble`, `[6..7]=vbat_mv (uint16 LE)`,
`[8]=fault_flags`, `[9..10]=uptime_min`, `[11]=fw_build`.

### Voice (impl deferida)

Frame Opus 16k por notificacao. **Caminho primario de voz e WiFi** (reusa a sessao de video); o
canal BLE Voice existe como contrato/fallback voice-only (sem WiFi). Ao implementar: **fixar quadro
de 20ms/40ms** (cabem em MTU<247); 60ms (244B) so com MTU≥247 negociado — senao fragmenta e quebra.

## Versionamento

`protocolVersion` = inteiro unico (uint8), trocado no HELLO. Mudanca **quebradora** (mover bytes,
mudar semantica de `cmd_id`/`event_code`, trocar UUID) **incrementa** a versao (fail-closed em
mismatch). Evolucao **nao-quebradora** na mesma versao: novos `cmd_id`/`event_code` (desconhecidos
sao **ignorados**), bytes reservados, `caps` bitfield no HELLO e `schema` byte nas characteristics.

## Questoes em aberto (a alinhar com o app)

1. UUID base `6a4e...` — confirmar/substituir pela base canonica do repo Jarvis-APP.
2. MTU efetivo no celular alvo (Android concede 247? 517? menos?) — medir na Fase 1b.
3. Seguranca do salto BLE→SoftAP: credencial do WiFi **derivada** da sessao BLE autenticada
   (LESC + HKDF + `session_id`), WPA2/WPA3, SSID/PSK efemeros por burst. **Bloqueador antes de
   habilitar streaming real** (nao bloqueia o bring-up de controle).
4. Codec/bitrate Opus exato (CBR/VBR, 16/24 kbps, quadro 20/40/60ms) — fixar medindo CPU no S3.
5. QoS BLE quando Voice fallback ativo: controle (Events/Telemetry) tem prioridade sobre voz (voz
   tolera perda) — fila separada com drop-oldest p/ voz.

## Referencias

- [[2026-06-29_plano_firmware_esp32s3]] · [[2026-06-28_separacao_repos_firmware_app]]
- [[../referencias/ble-wifi-video-audio-esp32]]
