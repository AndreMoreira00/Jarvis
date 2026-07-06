// app_core.c — composition root + orquestrador de eventos.
// Fluxo canonico: driver -> g_event_queue -> orchestrator_task -> ble notify -> app.
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "nvs_flash.h"

#include "app_core.h"
#include "jarvis_common.h"
#include "jarvis_ble.h"

// Subsistemas (stubs de bring-up: cada init loga um sinal de vida).
#include "camera.h"
#include "audio.h"
#include "wake_word.h"
#include "imu.h"
#include "power.h"
#include "wifi_stream.h"

static const char *TAG = "app_core";

#define EVENT_QUEUE_DEPTH 16
#define HEARTBEAT_MS      5000

static QueueHandle_t s_event_queue;

bool app_core_post_event(const jarvis_event_t *evt)
{
    if (s_event_queue == NULL || evt == NULL) {
        return false;
    }
    return xQueueSend(s_event_queue, evt, 0) == pdTRUE;
}

// Callback do componente ble: roda no contexto do host BLE -> so enfileira (nao bloqueia).
static void on_app_command(uint8_t cmd_id, const uint8_t *args, uint8_t len)
{
    (void)args;
    jarvis_event_t evt = { .kind = JARVIS_EVENT_APP_COMMAND, .code = cmd_id, .arg = len };
    app_core_post_event(&evt);
}

static void route_event(const jarvis_event_t *evt)
{
    switch (evt->kind) {
    case JARVIS_EVENT_HEAD_GESTURE:
    case JARVIS_EVENT_WAKEWORD:
        jarvis_ble_notify_event(evt);                       // -> Events (oculos->app)
        break;
    case JARVIS_EVENT_BATTERY:
        jarvis_ble_notify_battery(evt->arg, evt->value);    // -> 0x2A19 + Telemetry
        break;
    case JARVIS_EVENT_APP_COMMAND:
        ESP_LOGI(TAG, "cmd do app: 0x%02x (len=%u)", evt->code, evt->arg);
        break;
    default:
        break;
    }
}

// Coracao do app_core: drena a fila central e roteia. No timeout, emite heartbeat
// e (bring-up) uma telemetria de bateria placeholder p/ exercitar o caminho de notify.
static void orchestrator_task(void *param)
{
    ESP_LOGI(TAG, "orchestrator no ar; aguardando eventos");
    jarvis_event_t evt;
    while (true) {
        if (xQueueReceive(s_event_queue, &evt, pdMS_TO_TICKS(HEARTBEAT_MS)) == pdTRUE) {
            route_event(&evt);
            continue;
        }
        ESP_LOGI(TAG, "state=BLE_IDLE hb conn=%d", jarvis_ble_is_connected());
        jarvis_event_t batt = {
            .kind = JARVIS_EVENT_BATTERY, .arg = 87, .value = 3900,  // placeholder
        };
        route_event(&batt);
    }
}

static void init_subsystems_stub(void)
{
    // Drivers reais entram aqui ao sair do stub; por ora cada init e um sinal de vida.
    power_init();
    imu_init();
    audio_init();
    wake_word_init();
    camera_init();
    wifi_stream_init();
}

void app_core_start(void)
{
    jarvis_log_banner();

    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    s_event_queue = xQueueCreate(EVENT_QUEUE_DEPTH, sizeof(jarvis_event_t));
    if (s_event_queue == NULL) {
        ESP_LOGE(TAG, "sem memoria p/ a fila de eventos");
        return;
    }

    init_subsystems_stub();

    if (jarvis_ble_start(on_app_command) != ESP_OK) {
        ESP_LOGE(TAG, "BLE nao subiu; seguindo degradado");
    }

    // Orquestrador no core0 (plano de protocolo/radio), prioridade media.
    xTaskCreatePinnedToCore(orchestrator_task, "orchestrator", 4096, NULL, 5, NULL, 0);
    ESP_LOGI(TAG, "graph built (8 componentes); boot completo");
}
