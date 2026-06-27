---
title: RF-003 · Pergunta por voz com resposta falada
id: RF-003
type: requisito
categoria: funcional
status: aprovado
prioridade: alta
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
verificado_por: [TP-001_Validacao_Reconhecimento_Gestos, TP-002_Validacao_Fluxo_IA_Gemini]
tags: [requisito, funcional, module/software, layer/especificacao, prio/alta, tema/gestos, tema/ia, tema/voz]
---

# RF-003 · Pergunta por voz com resposta falada

## Descricao

O sistema deve, ao reconhecer o gesto **dedo levantado** (`Hands.Map_Speak`) executado com a **mao direita**, capturar a fala do usuario, transcrever para texto (STT em pt-BR via `recognize_google`), enviar o texto ao Gemini como prompt e reproduzir a resposta do modelo em audio (TTS).

A acao e disparada em `main.py` pela entrada `Map_Speak → Audio_to_Audio(executor)` (mao `Right`, cooldown de 20 frames) e implementada em `Control.Audio_to_Audio`, que chama `Capture_Audio` e depois `asyncio.run(jarvis_system.Text_To_Text(prompt))`.

## Criterios de aceitacao

- [ ] Com a mao direita com apenas o indicador levantado (`indicador_8_y < indicador_5_y - 0.05 * h`, demais dobrados), o fluxo de pergunta por voz inicia.
- [ ] `Capture_Audio` ajusta ruido ambiente por 2s, toca som de confirmacao e escuta com `timeout=5` e `phrase_time_limit=5`.
- [ ] A fala e transcrita por `recognize_google(language="pt-BR")`.
- [ ] O texto transcrito e enviado ao Gemini (`gemini-2.0-flash-lite`) via `Text_To_Text`.
- [ ] A resposta textual do Gemini e convertida em fala e reproduzida (ver [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007]]).
- [ ] A trava `ACTION` fica `True` durante o fluxo e volta a `False` ao final, impedindo acoes concorrentes (ver [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008]]).
- [ ] Falhas de STT retornam mensagens tratadas: `"Sem Pergunta"` (`UnknownValueError`), `"Erro de conexao"` (`RequestError`), `"Erro inesperado: ..."` (demais).

## Casos de uso associados

- [[CU-003_Perguntar_Por_Voz|CU-003 · Perguntar por voz]]
- [[Mapa_Gestos|Mapa de gestos]]

## Testes que verificam

- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Validacao de reconhecimento de gestos]]
- [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002 · Validacao do fluxo de IA (Gemini)]]

## Observacoes

- **Quirk de som:** `Capture_Audio` toca o som de inicio de **video** (`video_starter.wav`) como confirmacao de captura de audio, em vez de `audio_starter.wav`. O som dedicado de audio existe mas nao e usado neste caminho.
- Em caso de falha de STT, a string de erro (ex.: `"Sem Pergunta"`) e enviada ao Gemini como prompt — a IA respondera a esse texto. Comportamento a refinar.
- O fluxo depende de conectividade: `recognize_google` e a API Gemini sao online. Ver [[RNF-006_Dependencia_Conectividade|RNF-006]].

## Referencias

- [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini multimodal]]
- [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003 · TTS edge-tts + pygame]]
- [[Ref_SpeechRecognition|Referencia SpeechRecognition]]
- [[Ref_Google_Gemini_API|Referencia Google Gemini API]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007 · Resposta falada persona Jarvis]]
