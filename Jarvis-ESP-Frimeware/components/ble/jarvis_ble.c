// jarvis_ble.c — init do host NimBLE, GAP/advertising e funcoes de notify.
// Sequencia de init validada para ESP-IDF v5.5+/v6.0 (nimble_port_init substitui o
// removido esp_nimble_hci_and_controller_init; advertising so no sync_cb).
#include <string.h>

#include "esp_log.h"
#include "nvs_flash.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/util/util.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"

#include "jarvis_ble.h"
#include "jarvis_ble_priv.h"

// Funcao da lib esp-nimble sem header publico exposto — forward-declare e o padrao
// oficial (bleprph). Sem isto, -Werror=implicit-function-declaration quebra o build.
void ble_store_config_init(void);

static const char *TAG = "ble";

static uint8_t s_own_addr_type;
static uint16_t s_conn_handle = BLE_HS_CONN_HANDLE_NONE;
static jarvis_ble_cmd_cb_t s_cmd_cb;
static uint16_t s_event_seq;

static void jarvis_advertise(void);
static int jarvis_gap_event(struct ble_gap_event *event, void *arg);

// ---- acessores usados por gatt_svc.c ----
uint16_t jarvis_ble_conn_handle(void) { return s_conn_handle; }
jarvis_ble_cmd_cb_t jarvis_ble_get_cmd_cb(void) { return s_cmd_cb; }

// ---- API publica: estado/notify ----
bool jarvis_ble_is_connected(void)
{
    return s_conn_handle != BLE_HS_CONN_HANDLE_NONE;
}

static void notify_flat(uint16_t handle, const void *data, uint16_t len)
{
    if (s_conn_handle == BLE_HS_CONN_HANDLE_NONE || handle == 0) {
        return;
    }
    struct os_mbuf *om = ble_hs_mbuf_from_flat(data, len);
    if (om == NULL) {
        ESP_LOGW(TAG, "sem mbuf p/ notify (handle=%u)", handle);
        return;
    }
    ble_gatts_notify_custom(s_conn_handle, handle, om);
}

void jarvis_ble_notify_event(const jarvis_event_t *evt)
{
    if (evt == NULL) {
        return;
    }
    uint8_t type = (evt->kind == JARVIS_EVENT_WAKEWORD)
                       ? JARVIS_EVT_TYPE_WAKEWORD
                       : JARVIS_EVT_TYPE_HEAD_GESTURE;
    uint16_t seq = ++s_event_seq;
    uint8_t frame[8] = {
        type, evt->code, evt->flags, evt->arg,
        (uint8_t)(seq & 0xff), (uint8_t)(seq >> 8),
        0x00, 0x00,  // ts_delta_ms (best-effort; 0 no bring-up)
    };
    notify_flat(g_handle_events, frame, sizeof(frame));
}

void jarvis_ble_notify_battery(uint8_t pct, uint16_t mv)
{
    g_batt_level = pct;                 // Battery Level 0x2A19 (fonte unica do %)
    g_telemetry[0] = 1;                 // schema
    g_telemetry[6] = (uint8_t)(mv & 0xff);
    g_telemetry[7] = (uint8_t)(mv >> 8);
    notify_flat(g_handle_battery, &g_batt_level, 1);
    notify_flat(g_handle_telemetry, g_telemetry, sizeof(g_telemetry));
}

// ---- GAP / advertising ----
static void jarvis_advertise(void)
{
    struct ble_hs_adv_fields fields = {0};
    const char *name = ble_svc_gap_device_name();

    fields.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
    fields.tx_pwr_lvl_is_present = 1;
    fields.tx_pwr_lvl = BLE_HS_ADV_TX_PWR_LVL_AUTO;
    fields.name = (uint8_t *)name;
    fields.name_len = strlen(name);
    fields.name_is_complete = 1;
    if (ble_gap_adv_set_fields(&fields) != 0) {
        ESP_LOGE(TAG, "adv_set_fields falhou");
        return;
    }

    struct ble_gap_adv_params adv_params = {
        .conn_mode = BLE_GAP_CONN_MODE_UND,
        .disc_mode = BLE_GAP_DISC_MODE_GEN,
    };
    int rc = ble_gap_adv_start(s_own_addr_type, NULL, BLE_HS_FOREVER,
                               &adv_params, jarvis_gap_event, NULL);
    if (rc != 0) {
        ESP_LOGE(TAG, "adv_start rc=%d", rc);
    }
}

static int jarvis_gap_event(struct ble_gap_event *event, void *arg)
{
    switch (event->type) {
    case BLE_GAP_EVENT_CONNECT:
        if (event->connect.status == 0) {
            s_conn_handle = event->connect.conn_handle;
            ESP_LOGI(TAG, "connected; conn=%u", s_conn_handle);
        } else {
            ESP_LOGW(TAG, "connect falhou; re-anuncia");
            jarvis_advertise();
        }
        break;
    case BLE_GAP_EVENT_DISCONNECT:
        ESP_LOGI(TAG, "disconnect; reason=%d", event->disconnect.reason);
        s_conn_handle = BLE_HS_CONN_HANDLE_NONE;
        jarvis_advertise();  // volta ao plano de controle disponivel
        break;
    case BLE_GAP_EVENT_SUBSCRIBE:
        ESP_LOGI(TAG, "subscribe attr=%u notify=%d",
                 event->subscribe.attr_handle, event->subscribe.cur_notify);
        break;
    case BLE_GAP_EVENT_MTU:
        ESP_LOGI(TAG, "mtu=%d", event->mtu.value);
        break;
    default:
        break;
    }
    return 0;
}

// ---- host callbacks ----
static void on_stack_reset(int reason)
{
    ESP_LOGE(TAG, "stack reset; reason=%d", reason);
}

static void on_stack_sync(void)
{
    if (ble_hs_id_infer_auto(0, &s_own_addr_type) != 0) {
        ESP_LOGE(TAG, "infer_auto falhou");
        return;
    }
    ESP_LOGI(TAG, "init, advertising as %s", ble_svc_gap_device_name());
    jarvis_advertise();
}

static void jarvis_host_task(void *param)
{
    nimble_port_run();              // bloqueia ate nimble_port_stop()
    nimble_port_freertos_deinit();
}

esp_err_t jarvis_ble_start(jarvis_ble_cmd_cb_t on_cmd)
{
    s_cmd_cb = on_cmd;

    // nimble_port_init pode falhar por memoria do controller; num oculos sem porta
    // de debug NAO abortamos (correcao da verificacao) — degradamos sem BLE.
    esp_err_t ret = nimble_port_init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "nimble_port_init=%d (segue sem BLE)", ret);
        return ret;
    }

    ble_hs_cfg.reset_cb = on_stack_reset;
    ble_hs_cfg.sync_cb = on_stack_sync;
    ble_hs_cfg.store_status_cb = ble_store_util_status_rr;

    int rc = jarvis_gatt_svc_init();
    if (rc != 0) {
        ESP_LOGE(TAG, "gatt_svc_init rc=%d", rc);
        return ESP_FAIL;
    }
    ble_svc_gap_device_name_set("Jarvis-Glasses");
    ble_store_config_init();          // registra store de keys em NVS (correcao)

    nimble_port_freertos_init(jarvis_host_task);
    return ESP_OK;
}
