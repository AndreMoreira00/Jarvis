// power.h — executa a energia event-driven (sleep, fontes de wake, leitura de
// bateria via ADC/PMIC). NAO decide politica (isso e do app_core); so executa HW.
// Dois regimes: EM USO (BLE conectado, ~mA) vs GUARDADO (deep sleep, BLE off, <200uA).
// STUB de bring-up. Folha.
#pragma once

void power_init(void);  // bring-up: sinal de vida. Real: configura wake sources + ADC bateria.
