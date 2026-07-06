// jarvis_common.c — utilitarios minimos compartilhados (folha pura).
#include "jarvis_common.h"
#include "esp_log.h"

void jarvis_log_banner(void)
{
    ESP_LOGI("jarvis", "Jarvis firmware (cliente-fino ESP32-S3) | proto v=%d",
             JARVIS_PROTOCOL_VERSION);
}
