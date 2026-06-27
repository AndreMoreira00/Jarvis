---
title: RNF-003 · Idioma portugues do Brasil (pt-BR)
type: requisito
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
id: RNF-003
module: 02_Especificacoes
categoria: nao-funcional
prioridade: alta
tags: [requisito, layer/especificacao, prio/alta, tema/idioma, tema/voz]
---

# RNF-003 · Idioma portugues do Brasil (pt-BR)

## Descricao

Toda a interacao falada — entrada (STT), processamento da persona (LLM) e saida
(TTS) — deve ocorrer em **portugues do Brasil (pt-BR)**. O assistente fala e entende
pt-BR de ponta a ponta.

## Justificativa

O usuario-alvo e brasileiro; consistencia de idioma e requisito de usabilidade
([[RNF-002_Operacao_Hands_Free|RNF-002]]). O idioma esta fixado em codigo nas tres
camadas de voz/linguagem.

## Pontos de fixacao no codigo

| Camada | Onde | Configuracao pt-BR |
|--------|------|--------------------|
| STT (voz → texto) | [[control.py]] `Capture_Audio` | `recognize_google(audio, language="pt-BR")` |
| Persona / LLM | [[jarvis.py]] `__init__` | `template` (system instruction) escrito em pt-BR, trata o usuario como "Mestre" |
| TTS (texto → voz) | [[jarvis.py]] `__init__` / `Translate` | `VOICE = "pt-BR-AntonioNeural"` (edge-tts) |

## Criterios de aceitacao

| # | Criterio | Como verificar |
|---|----------|----------------|
| 1 | Perguntas faladas em pt-BR sao transcritas corretamente | Falar uma frase e checar o prompt capturado |
| 2 | A resposta do Gemini sai em pt-BR | Validar texto retornado por `generate_content` |
| 3 | A voz sintetizada e pt-BR (Antonio) | Ouvir o `response/translate.mp3` |
| 4 | Nenhuma string de interacao em outro idioma | Revisao do `template` e dos retornos de erro |

> Mensagens de erro internas de `Capture_Audio` ("Sem Pergunta", "Erro de conexao",
> "Erro inesperado: ...") ja estao em pt-BR e sao enviadas como prompt ao Gemini.

## Riscos

- `recognize_google` depende de internet (ver [[RNF-006_Dependencia_Conectividade]]);
  sem rede nao ha STT em qualquer idioma.
- A voz `pt-BR-AntonioNeural` e um recurso da Microsoft Edge TTS — alterar a voz exige
  trocar a constante `VOICE` (ver [[Ref_Edge_TTS]]).

## Referencias

- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007 · Resposta falada com persona]]
- [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003 · TTS Edge-TTS + Pygame]]
- [[Ref_SpeechRecognition]]
- [[Ref_Edge_TTS]]
- [[Ref_Google_Gemini_API]]
