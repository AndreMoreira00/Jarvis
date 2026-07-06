// app_core.h — composition root (FINO) do firmware Jarvis.
// Monta o grafo de componentes, sobe a fila central de eventos e o orquestrador.
// Nao implementa logica de dominio nem driver: so injeta e roteia.
#pragma once

#include "jarvis_types.h"

// Sobe o sistema: NVS, fila central, BLE (plano de controle) e os subsistemas
// (stubs por enquanto), e cria o orchestrator_task. Chamado de app_main().
void app_core_start(void);

// Publica um evento na fila central (usado pelos drivers via callback injetado).
// Seguro chamar de outras tasks; retorna false se a fila estiver cheia.
bool app_core_post_event(const jarvis_event_t *evt);
