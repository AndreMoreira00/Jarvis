// jarvis_ble_priv.h — interface PRIVADA entre jarvis_ble.c (host/gap) e
// gatt_svc.c (tabela de servicos + access callbacks). Nao sai do componente.
#pragma once

#include <stdint.h>
#include "host/ble_hs.h"
#include "jarvis_ble.h"

// --- UUID base da JarvisService (vendor 128-bit), proposta do firmware ---
// 6a4e<NNNN>-b5a3-f393-e0a9-e50e24dcca9e  (NNNN = id curto da char; 0x0001 = service)
// Macro monta o array little-endian que o NimBLE espera, inserindo o id curto.
#define JARVIS_UUID128(s16)                                                       \
    BLE_UUID128_INIT(0x9e, 0xca, 0xdc, 0x24, 0x0e, 0xe5, 0xa9, 0xe0,              \
                     0x93, 0xf3, 0xa3, 0xb5,                                       \
                     (uint8_t)((s16) & 0xff), (uint8_t)(((s16) >> 8) & 0xff),      \
                     0x4e, 0x6a)

// Ids curtos das characteristics da JarvisService.
#define JARVIS_SVC_ID        0x0001
#define JARVIS_CHR_HANDSHAKE 0x0002
#define JARVIS_CHR_CONTROL   0x0003
#define JARVIS_CHR_EVENTS    0x0004
#define JARVIS_CHR_TELEMETRY 0x0005
#define JARVIS_CHR_VOICE     0x0006

// Handles preenchidos no registro do GATT (val_handle de cada char), usados p/ notify.
extern uint16_t g_handle_events;
extern uint16_t g_handle_telemetry;
extern uint16_t g_handle_battery;

// Caches de "ultimo valor" lidos pelos access callbacks (READ) e atualizados pelos
// notify de jarvis_ble.c. Mantem fonte unica por characteristic.
extern uint8_t  g_batt_level;        // Battery Level 0x2A19 (0..100%)
extern uint8_t  g_telemetry[12];     // snapshot da Telemetry custom

// Registra a tabela de servicos (chamado dentro do init de jarvis_ble.c).
int jarvis_gatt_svc_init(void);

// Conexao atual (BLE_HS_CONN_HANDLE_NONE se nao conectado) — definido em jarvis_ble.c.
uint16_t jarvis_ble_conn_handle(void);

// Callback de comando do app, registrado no start — usado pelo access cb de Control.
jarvis_ble_cmd_cb_t jarvis_ble_get_cmd_cb(void);
