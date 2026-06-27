---
title: RF-008 · Debounce por cooldown e trava de acao
id: RF-008
type: requisito
categoria: funcional
status: aprovado
prioridade: alta
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
verificado_por: [TP-001_Validacao_Reconhecimento_Gestos, TP-002_Validacao_Fluxo_IA_Gemini]
tags: [requisito, funcional, module/software, layer/especificacao, prio/alta, tema/gestos, tema/concorrencia]
---

# RF-008 · Debounce por cooldown e trava de acao

## Descricao

O sistema deve evitar disparos repetidos do mesmo gesto e impedir a execucao de acoes concorrentes, por meio de dois mecanismos:

1. **Debounce por cooldown** — a variavel global `gesture_cooldown` (em frames) e setada para o valor do gesto (20 ou 30) ao disparar e decrementada em 1 a cada frame. Nenhum gesto e avaliado enquanto `gesture_cooldown > 0`.
2. **Trava de acao** — a flag `Control.ACTION` (bool) impede iniciar uma nova acao enquanto outra roda. As acoes de IA setam `ACTION = True` no inicio e `ACTION = False` no fim; o loop em `main.py` so avalia gestos quando `ACTION == False`.

A condicao de avaliacao em `main.py` e: `if control_functions.ACTION == False and gesture_cooldown == 0`.

## Criterios de aceitacao

- [ ] Ao disparar um gesto, `gesture_cooldown` e setado para o cooldown do gesto (20 para OK/dedo/L/rock; 30 para positivo).
- [ ] `gesture_cooldown` decrementa 1 por frame e bloqueia novos disparos ate chegar a 0.
- [ ] Enquanto `ACTION == True`, nenhum gesto e avaliado nem disparado.
- [ ] As acoes `Audio_to_Audio`, `Image_Audio` e `Video_Audio` setam `ACTION = True` no inicio e `False` no fim.
- [ ] A combinacao cooldown + trava evita disparos multiplos do mesmo gesto e acoes sobrepostas.

## Casos de uso associados

- [[Mapa_Gestos|Mapa de gestos]]
- [[CU-003_Perguntar_Por_Voz|CU-003]], [[CU-004_Analisar_Imagem_Com_Pergunta|CU-004]], [[CU-005_Analisar_Video_Com_Pergunta|CU-005]]

## Testes que verificam

- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Validacao de reconhecimento de gestos]]
- [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002 · Validacao do fluxo de IA (Gemini)]]

## Observacoes

- **Cobertura assimetrica:** `Capture_Photo` e `Capture_Video` **nao** setam `ACTION`; sua protecao vem apenas do `gesture_cooldown`. So as acoes de IA usam a trava `ACTION`.
- **Quirk de toggle:** `Check_Gesture` alterna `Control_Video` a cada disparo de gesto (de qualquer tipo), acoplando o estado de gravacao ao debounce de forma fragil. Ver [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002]].
- `gesture_cooldown` e global e compartilhado entre todos os gestos: um disparo bloqueia temporariamente a avaliacao de qualquer gesto, nao apenas do que disparou.
- Valores de cooldown sao em frames, nao em segundos; o tempo real depende do frame rate (sensivel no Raspberry Pi 3). Ver [[RNF-001_Execucao_Raspberry_Pi3|RNF-001]].

## Referencias

- [[ADR-0004_Concorrencia_Asyncio_ThreadPool|ADR-0004 · Concorrencia asyncio/ThreadPool]]
- [[RF-006_Reconhecimento_Cinco_Gestos|RF-006 · Reconhecimento de cinco gestos]]
- [[Arquitetura_Software|Arquitetura do software]]
