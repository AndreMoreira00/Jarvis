---
title: OBJ-003 · Portabilidade para Raspberry Pi 3
id: OBJ-003
type: objetivo
status: aprovado
prioridade: media
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 00_SGI_Aplicado
tags: [objetivo, module/software, prio/media, tema/hardware]
---

# OBJ-003 · Portabilidade para Raspberry Pi 3

## Descricao

Garantir que o software rode no **Raspberry Pi 3**, a plataforma-alvo dos oculos inteligentes. Hoje o app e desenvolvido e validado em desktop, mas todo o pipeline (OpenCV, MediaPipe, Gemini via rede, edge-tts, pygame) precisa caber no orcamento de CPU, memoria e energia de um RPi 3, com a camera e o microfone embarcados.

Este objetivo e de **media prioridade** nesta fase: o foco imediato e provar o software no desktop. A portabilidade entra como criterio de viabilidade do produto final e esta diretamente ligada ao [[RISCO-001_Desempenho_Raspberry_Pi|RISCO-001]] (desempenho em tempo real no RPi 3).

## Escopo

- Codigo agnostico de plataforma: paths relativos a partir da raiz do repo, dependencias instalaveis via `pip` (com a ressalva das entradas problematicas em `requirements.txt`).
- Operacao **hands-free** e dependente de **conectividade** (Gemini/Photos/STT na nuvem) — ver [[RNF-006_Dependencia_Conectividade|RNF-006]].
- Tarefas pesadas isoladas em `ThreadPoolExecutor` para nao travar o loop `asyncio` da camera.

## Criterio mensuravel

| Metrica | Meta |
|---|---|
| Execucao no RPi 3 | App inicia e reconhece gestos rodando `python main.py` em Raspberry Pi 3 |
| Taxa de quadros (deteccao de mao) | a definir (alvo: fluido o bastante para reconhecer gestos sem perda perceptivel) |
| Latencia ate resposta falada | a definir — ver [[RNF-004_Latencia_Resposta|RNF-004]] |

> As metas de FPS e latencia ficam **a definir** ate haver medicao real em hardware RPi 3; nao ha numeros aferidos no codigo atual.

## Referencias

- [[RNF-001_Execucao_Raspberry_Pi3|RNF-001 · Execucao no Raspberry Pi 3]]
- [[ADR-0007_Alvo_Raspberry_Pi3|ADR-0007 · Alvo Raspberry Pi 3]]
- [[ADR-0004_Concorrencia_Asyncio_ThreadPool|ADR-0004 · Concorrencia asyncio + ThreadPool]]
- [[RISCO-001_Desempenho_Raspberry_Pi|RISCO-001 · Desempenho no Raspberry Pi 3]]
- [[Home|Home — Jarvis]]
