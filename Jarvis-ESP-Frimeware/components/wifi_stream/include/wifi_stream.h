// wifi_stream.h — plano de DADOS sob demanda: SoftAP ponto-a-ponto + WebSocket/HTTP
// servindo MJPEG. Liga o radio WiFi SO na janela de captura (wifi_burst) e desliga.
// Consome frames JPEG do `camera` (excecao de dado documentada). STUB de bring-up.
#pragma once

void wifi_stream_init(void);  // bring-up: sinal de vida. Real: prepara SoftAP+WS (desligado).
