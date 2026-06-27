---
title: ADR-0003 · edge-tts + pygame para sintese e reproducao de voz
type: adr
status: aceito
id: ADR-0003
deciders: [Andre Moreira]
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 01_Gestao
layer: gestao
tags: [adr, module/software, layer/gestao, tema/voz, tema/audio]
---

# ADR-0003 · edge-tts + pygame para sintese e reproducao de voz

## Contexto

O Jarvis e um assistente **falado**: o usuario faz perguntas por voz e recebe a
resposta tambem por voz, sem tela de leitura. Isso exige dois servicos de audio:

- **STT** (voz → texto) para transcrever a pergunta do usuario;
- **TTS** (texto → voz) para sintetizar a resposta do Gemini na "voz do Jarvis";
- um **player** para reproduzir o audio sintetizado e os sons de confirmacao de
  acoes (foto, inicio/fim de video).

Tudo em **PT-BR** (ver [[RNF-003_Idioma_PT_BR]]) e integrado ao loop de gestos sem
travar o `asyncio` mais do que o necessario.

## Decisao

| Funcao | Tecnologia | Detalhe |
|---|---|---|
| **TTS** | `edge-tts` | Voz `pt-BR-AntonioNeural`; gera MP3 em `./response/translate.mp3` |
| **Player** | `pygame.mixer` | `mixer.Sound(...).play()` para a resposta e para os sons de `audios_check/` |
| **STT** | `SpeechRecognition` | `recognize_google(..., language="pt-BR")` |

Fluxo de saida (em [jarvis.py](../../../../jarvis.py), `Translate` →
`Text_To_Text`/`Image_To_Text`/`Video_To_Text`):

1. O texto do Gemini passa por `Translate`, que **higieniza caracteres** (tab `\t`,
   asterisco `*`, zero-width `​`/`‌`/`‍`, BOM `﻿`, espacos
   duplos) trocando-os por espaco e aplicando `strip()`.
2. `edge_tts.Communicate(text, VOICE).save(PATH_FILE)` grava o MP3 em
   `./response/translate.mp3`.
3. `pygame.mixer.Sound(PATH_FILE).play()` reproduz; aguarda
   `asyncio.sleep(SOUND.get_length())` e da `stop()`.

Fluxo de entrada (em [control.py](../../../../control.py), `Capture_Audio`):
`SpeechRecognition` com `Recognizer` (`pause_threshold=0.8`,
`dynamic_energy_threshold=False`, `energy_threshold=300`), `adjust_for_ambient_noise`
por 2s e `recognize_google(language="pt-BR")`. Excecoes mapeiam para mensagens PT-BR
("Sem Pergunta", "Erro de conexao", "Erro inesperado: ...").

A persona que origina o texto falado vem do Gemini (ver [[ADR-0002_Gemini_Multimodal]]).

## Alternativas consideradas

| Alternativa | Por que foi descartada |
|---|---|
| **TTS local** (`pyttsx3`, Piper) | Funciona offline, mas a qualidade/naturalidade da voz `pyttsx3` e baixa; Piper exige empacotar modelos e tunar para ARM. `edge-tts` entrega voz neural PT-BR de alta qualidade sem custo de modelo local. |
| **Google Cloud TTS** | Qualidade alta, porem servico pago com billing/credenciais proprias; `edge-tts` cobre a necessidade sem custo. |
| **ElevenLabs** | Vozes excelentes, mas servico pago e overkill para o escopo atual. |

## Consequencias

### Positivas

- **Voz neural PT-BR de qualidade** (`pt-BR-AntonioNeural`) sem treinar nem
  hospedar modelo, satisfazendo [[RF-007_Resposta_Falada_Persona_Jarvis]].
- **`pygame.mixer` unifica o playback**: tanto a resposta quanto os sons de
  confirmacao de acao (`audios_check/`) usam o mesmo mecanismo.
- **Higienizacao em `Translate`** evita que markdown/zero-width width chars do
  Gemini virem ruido na fala.
- STT e TTS ja em **PT-BR**, alinhados a [[RNF-003_Idioma_PT_BR]].

### Negativas / riscos

- **edge-tts exige internet**: o servico de voz da Microsoft e online; sem rede,
  nao ha fala (somam-se as dependencias do Gemini — ver
  [[RNF-006_Dependencia_Conectividade]]).
- **STT tambem online**: `recognize_google` depende de conectividade; offline cai
  em "Erro de conexao".
- **Arquivo MP3 unico** (`./response/translate.mp3`) e sobrescrito a cada resposta;
  duas falas concorrentes se atropelariam (mitigado pela trava `ACTION`, ver
  [[ADR-0004_Concorrencia_Asyncio_ThreadPool]] e [[RF-008_Debounce_Cooldown_E_Trava_Acao]]).
- **Conducao ossea no hardware futuro**: a reproducao no oculos deve usar
  conducao ossea / alto-falante proximo ao ouvido; a saida de audio fisica ainda e
  *a definir* no hardware alvo (ver [[ADR-0007_Alvo_Raspberry_Pi3]]).
- **Quirk de som**: `Capture_Audio` toca o som de **inicio de video**
  (`video_start_sound`) ao iniciar a captura de **audio** — feedback sonoro
  potencialmente confuso (registrado para revisao).

## Referencias

- [[Ref_Edge_TTS]] — referencia da biblioteca edge-tts
- [[Ref_SpeechRecognition]] — referencia do SpeechRecognition (STT)
- [[Ref_Pygame_Mixer]] — referencia do pygame.mixer (player)
- [[RNF-003_Idioma_PT_BR]] — requisito de idioma PT-BR
- [[RF-007_Resposta_Falada_Persona_Jarvis]] — resposta falada com persona
- [[ADR-0002_Gemini_Multimodal]] — origem do texto a ser falado
- [[ADR-0004_Concorrencia_Asyncio_ThreadPool]] — trava de acao e concorrencia
- [[RNF-006_Dependencia_Conectividade]] — dependencia de internet
