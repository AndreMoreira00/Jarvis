// wake_word.h — deteccao local de palavra-chave (ESP-SR / WakeNet9s) sobre o mic.
// NAO faz STT (isso e no celular): ao detectar, emite UM evento p/ o app_core.
// STUB de bring-up. Consome PCM do `audio` (excecao de dado documentada).
#pragma once

void wake_word_init(void);  // bring-up: sinal de vida. Real: carrega WakeNet + callback.
