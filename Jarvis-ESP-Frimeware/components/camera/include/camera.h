// camera.h — driver OV2640 DVP -> JPEG por HW -> frame buffer PSRAM (SOB DEMANDA).
// STUB de bring-up: API real (camera_capture/camera_release) entra ao implementar.
// Folha: depende so de jarvis_common; nao conhece WiFi nem app_core.
#pragma once

void camera_init(void);  // bring-up: sinal de vida. Real: configura sensor + buffers PSRAM.
