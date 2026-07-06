// gatt_svc.c — tabela de servicos GATT (JarvisService + Battery padrao) e access
// callbacks. Implementa a PROPOSTA do contrato (handshake/control/events/telemetry/voice).
#include <string.h>

#include "esp_log.h"
#include "host/ble_hs.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"

#include "jarvis_ble_priv.h"
#include "jarvis_types.h"

static const char *TAG = "ble.gatt";

// --- handles (val_handle) preenchidos no registro ---
uint16_t g_handle_events;
uint16_t g_handle_telemetry;
uint16_t g_handle_battery;
static uint16_t s_handle_handshake;
static uint16_t s_handle_control;
static uint16_t s_handle_voice;

// --- caches de ultimo valor (fonte unica por characteristic) ---
uint8_t g_batt_level = 100;
uint8_t g_telemetry[12] = { 1 };          // byte[0]=schema=1
static uint8_t s_last_ack[12];            // ultimo HELLO_ACK (READ da Handshake)
static uint32_t s_session_id;             // incrementa por handshake (sem RNG)

// --- UUIDs (objetos com storage estatico p/ a tabela apontar) ---
static const ble_uuid128_t uuid_svc       = JARVIS_UUID128(JARVIS_SVC_ID);
static const ble_uuid128_t uuid_handshake = JARVIS_UUID128(JARVIS_CHR_HANDSHAKE);
static const ble_uuid128_t uuid_control   = JARVIS_UUID128(JARVIS_CHR_CONTROL);
static const ble_uuid128_t uuid_events    = JARVIS_UUID128(JARVIS_CHR_EVENTS);
static const ble_uuid128_t uuid_telemetry = JARVIS_UUID128(JARVIS_CHR_TELEMETRY);
static const ble_uuid128_t uuid_voice     = JARVIS_UUID128(JARVIS_CHR_VOICE);

// ---- Handshake: app escreve HELLO; firmware responde HELLO_ACK/REJECT por notify ----
static void send_hello_ack(uint16_t conn, uint8_t app_proto)
{
    bool ok = (app_proto == JARVIS_PROTOCOL_VERSION);
    uint16_t mtu = (conn != BLE_HS_CONN_HANDLE_NONE) ? ble_att_mtu(conn) : 23;
    uint32_t sid = ++s_session_id;

    memset(s_last_ack, 0, sizeof(s_last_ack));
    s_last_ack[0] = ok ? 0x81 : 0x8F;              // HELLO_ACK / HELLO_REJECT
    s_last_ack[1] = JARVIS_PROTOCOL_VERSION;
    // [2..3]=fw_caps=0 (so plano de controle no bring-up; streaming/voz deferidos)
    s_last_ack[4] = ok ? 0 : 1;                    // motivo (1=versao incompativel)
    s_last_ack[6] = (uint8_t)(sid & 0xff);
    s_last_ack[7] = (uint8_t)((sid >> 8) & 0xff);
    s_last_ack[8] = (uint8_t)((sid >> 16) & 0xff);
    s_last_ack[9] = (uint8_t)((sid >> 24) & 0xff);
    s_last_ack[10] = (uint8_t)(mtu & 0xff);        // MTU efetivo em BYTES (uint16, corrigido)
    s_last_ack[11] = (uint8_t)(mtu >> 8);

    struct os_mbuf *om = ble_hs_mbuf_from_flat(s_last_ack, sizeof(s_last_ack));
    if (om != NULL) {
        ble_gatts_notify_custom(conn, s_handle_handshake, om);
    }
    ESP_LOGI(TAG, "HELLO app_proto=%u -> %s mtu=%u sid=%lu",
             app_proto, ok ? "ACK" : "REJECT", mtu, (unsigned long)sid);
}

static int handshake_access(uint16_t conn, uint16_t attr,
                            struct ble_gatt_access_ctxt *ctxt, void *arg)
{
    if (ctxt->op == BLE_GATT_ACCESS_OP_READ_CHR) {
        return os_mbuf_append(ctxt->om, s_last_ack, sizeof(s_last_ack)) == 0
                   ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
    }
    if (ctxt->op == BLE_GATT_ACCESS_OP_WRITE_CHR) {
        uint8_t buf[8] = {0};
        uint16_t len = 0;
        ble_hs_mbuf_to_flat(ctxt->om, buf, sizeof(buf), &len);
        if (len < 2 || buf[0] != 0x01) {           // espera opcode HELLO
            return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
        }
        send_hello_ack(conn, buf[1]);
        return 0;
    }
    return BLE_ATT_ERR_UNLIKELY;
}

// ---- Control: comandos do app -> callback do app_core ----
static int control_access(uint16_t conn, uint16_t attr,
                          struct ble_gatt_access_ctxt *ctxt, void *arg)
{
    if (ctxt->op != BLE_GATT_ACCESS_OP_WRITE_CHR) {
        return BLE_ATT_ERR_UNLIKELY;
    }
    uint8_t buf[20] = {0};
    uint16_t len = 0;
    ble_hs_mbuf_to_flat(ctxt->om, buf, sizeof(buf), &len);
    if (len < 2) {
        return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
    }
    uint8_t arg_len = (buf[1] <= (len - 2)) ? buf[1] : (uint8_t)(len - 2);
    jarvis_ble_cmd_cb_t cb = jarvis_ble_get_cmd_cb();
    if (cb != NULL) {
        cb(buf[0], &buf[2], arg_len);              // cmd_id, args, arg_len
    }
    return 0;
}

// ---- Telemetry custom (READ do snapshot; notify vem de jarvis_ble.c) ----
static int telemetry_access(uint16_t conn, uint16_t attr,
                            struct ble_gatt_access_ctxt *ctxt, void *arg)
{
    if (ctxt->op != BLE_GATT_ACCESS_OP_READ_CHR) {
        return BLE_ATT_ERR_UNLIKELY;
    }
    return os_mbuf_append(ctxt->om, g_telemetry, sizeof(g_telemetry)) == 0
               ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
}

// ---- Voice (IMPL DEFERIDA): aceita write mas ignora; existe so como contrato ----
static int voice_access(uint16_t conn, uint16_t attr,
                        struct ble_gatt_access_ctxt *ctxt, void *arg)
{
    return 0;  // fallback de voz Opus 16k nao implementado no bring-up
}

// ---- Battery Level 0x2A19 padrao ----
static int battery_access(uint16_t conn, uint16_t attr,
                          struct ble_gatt_access_ctxt *ctxt, void *arg)
{
    if (ctxt->op != BLE_GATT_ACCESS_OP_READ_CHR) {
        return BLE_ATT_ERR_UNLIKELY;
    }
    return os_mbuf_append(ctxt->om, &g_batt_level, 1) == 0
               ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
}

// ---- tabela de servicos ----
static const struct ble_gatt_svc_def gatt_svcs[] = {
    {
        .type = BLE_GATT_SVC_TYPE_PRIMARY,
        .uuid = &uuid_svc.u,
        .characteristics = (struct ble_gatt_chr_def[]){
            { .uuid = &uuid_handshake.u, .access_cb = handshake_access,
              .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_WRITE | BLE_GATT_CHR_F_NOTIFY,
              .val_handle = &s_handle_handshake },
            { .uuid = &uuid_control.u, .access_cb = control_access,
              .flags = BLE_GATT_CHR_F_WRITE | BLE_GATT_CHR_F_WRITE_NO_RSP,
              .val_handle = &s_handle_control },
            { .uuid = &uuid_events.u, .access_cb = NULL,
              .flags = BLE_GATT_CHR_F_NOTIFY,
              .val_handle = &g_handle_events },
            { .uuid = &uuid_telemetry.u, .access_cb = telemetry_access,
              .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_NOTIFY,
              .val_handle = &g_handle_telemetry },
            { .uuid = &uuid_voice.u, .access_cb = voice_access,
              .flags = BLE_GATT_CHR_F_NOTIFY | BLE_GATT_CHR_F_WRITE_NO_RSP,
              .val_handle = &s_handle_voice },
            { 0 },
        },
    },
    {
        .type = BLE_GATT_SVC_TYPE_PRIMARY,
        .uuid = BLE_UUID16_DECLARE(0x180F),       // Battery Service
        .characteristics = (struct ble_gatt_chr_def[]){
            { .uuid = BLE_UUID16_DECLARE(0x2A19),  // Battery Level
              .access_cb = battery_access,
              .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_NOTIFY,
              .val_handle = &g_handle_battery },
            { 0 },
        },
    },
    { 0 },
};

int jarvis_gatt_svc_init(void)
{
    int rc;
    ble_svc_gap_init();
    ble_svc_gatt_init();
    if ((rc = ble_gatts_count_cfg(gatt_svcs)) != 0) {
        return rc;
    }
    return ble_gatts_add_svcs(gatt_svcs);
}
