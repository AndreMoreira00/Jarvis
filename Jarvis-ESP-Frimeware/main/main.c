// Entry point do firmware Jarvis (cliente-fino ESP32-S3).
// Responsabilidade unica: delegar para o composition root (app_core).
// Nenhuma logica de dominio nem acesso a hardware vive aqui.
#include "app_core.h"

void app_main(void)
{
    app_core_start();
}
