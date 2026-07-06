// jarvis_ble.h — plano de CONTROLE always-on (GATT server NimBLE).
// API publica do componente `ble`. Implementa a PROPOSTA do contrato oculos<->app
// (ver docs_projeto/decisoes/2026-06-29_contrato_ble_gatt_proposta.md).
//
// O componente nao conhece app_core: recebe um callback de comando no start
// (inversao de dependencia) e expoe funcoes de notify chamadas pelo orquestrador.
#pragma once

#include "esp_err.h"
#include "jarvis_types.h"

// Callback de comando do app (canal Control). Chamado NO CONTEXTO DO HOST BLE —
// nao bloqueie: apenas repasse para a fila do app_core.
typedef void (*jarvis_ble_cmd_cb_t)(uint8_t cmd_id, const uint8_t *args, uint8_t len);

// Sobe controller + host NimBLE, registra o GATT server e inicia o advertising.
// Nao bloqueia (o host roda numa task propria criada pela stack). on_cmd pode ser NULL.
esp_err_t jarvis_ble_start(jarvis_ble_cmd_cb_t on_cmd);

// True enquanto ha um app conectado.
bool jarvis_ble_is_connected(void);

// Notifica um evento de gesto de cabeca (IMU) ou wakeword -> characteristic Events.
// No-op se nao houver conexao/inscricao. evt->kind deve ser HEAD_GESTURE ou WAKEWORD.
void jarvis_ble_notify_event(const jarvis_event_t *evt);

// Atualiza e notifica bateria: % no Battery Level padrao (0x2A19) + tensao na
// Telemetry custom. No-op se nao conectado.
void jarvis_ble_notify_battery(uint8_t pct, uint16_t mv);
