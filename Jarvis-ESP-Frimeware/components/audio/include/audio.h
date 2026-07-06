// audio.h — I2S bidirecional: mic MEMS (ICS-43434/INMP441) + MAX98357A (class-D mono)
// drivando exciter de conducao ossea com ganho limitado.
// STUB de bring-up: API real (audio_capture/audio_play) entra ao implementar. Folha.
#pragma once

void audio_init(void);  // bring-up: sinal de vida. Real: sobe I2S RX(mic)+TX(amp) @16k.
