// jarvis_types.h — tipos do CONTRATO INTERNO do firmware (folha pura, sem deps).
// Todos os componentes dependem deste header; ele de ninguem (quebra ciclos).
// Os codigos de fio (BLE) que precisam casar com o app vivem aqui para serem a
// fonte unica compartilhada entre o componente `ble` e os drivers que geram eventos.
#pragma once

#include <stdint.h>
#include <stdbool.h>

// Versao do protocolo oculos<->app trocada no handshake BLE (HELLO/HELLO_ACK).
// Incrementa a CADA mudanca quebradora de payload/semantica (ver plano de versionamento).
#define JARVIS_PROTOCOL_VERSION 1

// ---- Tipos de evento no canal Events (oculos -> app), 1 byte ----
// IMPORTANTE: gesto de MAO NAO esta aqui. Reconhecimento de mao roda no celular
// (MediaPipe); o MCU nunca faz percepcao. So nascem no firmware o gesto de CABECA
// (IMU, calculado local) e o WAKEWORD (ESP-SR). (Correcao da verificacao adversarial.)
typedef enum {
    JARVIS_EVT_TYPE_HEAD_GESTURE = 0x02,  // gesto de cabeca derivado do IMU
    JARVIS_EVT_TYPE_WAKEWORD     = 0x03,  // palavra-chave detectada (WakeNet)
} jarvis_evt_type_t;

// Codigos de gesto de CABECA (IMU) — nascem no firmware.
typedef enum {
    JARVIS_HEAD_NONE      = 0,
    JARVIS_HEAD_NOD       = 1,  // "sim"
    JARVIS_HEAD_SHAKE     = 2,  // "nao"
    JARVIS_HEAD_TILT_L    = 3,
    JARVIS_HEAD_TILT_R    = 4,
    JARVIS_HEAD_LOOK_UP   = 5,
    JARVIS_HEAD_LOOK_DOWN = 6,
    JARVIS_HEAD_DOUBLE_NOD = 7,
} jarvis_head_gesture_t;

// ---- Comandos do app no canal Control (app -> oculos), cmd_id ----
typedef enum {
    JARVIS_CMD_START_WIFI_STREAM = 0x10,
    JARVIS_CMD_STOP_WIFI_STREAM  = 0x11,
    JARVIS_CMD_CAPTURE_PHOTO     = 0x20,
    JARVIS_CMD_START_VOICE       = 0x30,
    JARVIS_CMD_STOP_VOICE        = 0x31,
    JARVIS_CMD_SET_LED           = 0x40,
    JARVIS_CMD_SLEEP             = 0x50,
    JARVIS_CMD_SET_NOTIFY_MASK   = 0x60,
    JARVIS_CMD_PING              = 0x70,
} jarvis_cmd_id_t;

// ---- Estados de energia (event-driven). Politica decidida no app_core; o
// componente `power` so executa as transicoes de hardware. ----
typedef enum {
    JARVIS_POWER_DEEP_SLEEP = 0,   // guardado: BLE desconectado, alvo <200uA
    JARVIS_POWER_BLE_IDLE,         // em uso: plano de controle BLE conectado (~mA)
    JARVIS_POWER_WAKE_LISTENING,   // pos-wakeword: canal de audio aberto
    JARVIS_POWER_CAPTURE_ACTIVE,   // captura sob comando: camera ligada
    JARVIS_POWER_WIFI_BURST,       // janela de stream MJPEG (maior dreno)
} jarvis_power_state_t;

// ---- Evento interno (IPC entre tasks via fila central do app_core) ----
// Forma compacta e neutra de transporte; o componente `ble` traduz para o fio.
typedef enum {
    JARVIS_EVENT_NONE = 0,
    JARVIS_EVENT_HEAD_GESTURE,  // imu -> app_core -> ble (Events 0x02)
    JARVIS_EVENT_WAKEWORD,      // wake_word -> app_core -> ble (Events 0x03)
    JARVIS_EVENT_APP_COMMAND,   // ble (Control) -> app_core
    JARVIS_EVENT_BATTERY,       // power -> app_core -> ble (Telemetry/0x2A19)
} jarvis_event_kind_t;

typedef struct {
    jarvis_event_kind_t kind;
    uint8_t  code;   // gesto (jarvis_head_gesture_t) ou cmd_id (jarvis_cmd_id_t)
    uint8_t  flags;  // bitfield dependente do kind (ex.: hold/repeat no IMU)
    uint8_t  arg;    // confidence (0..255) ou battery_pct ou arg do comando
    uint16_t value;  // vbat_mv (BATTERY) ou dado generico
} jarvis_event_t;
