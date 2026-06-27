---
title: RNF-001 · Execucao no Raspberry Pi 3
type: requisito
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
id: RNF-001
module: 02_Especificacoes
categoria: nao-funcional
prioridade: alta
tags: [requisito, layer/especificacao, prio/alta, tema/desempenho, tema/hardware]
---

# RNF-001 · Execucao no Raspberry Pi 3

## Descricao

O software Jarvis deve executar no **Raspberry Pi 3**, plataforma-alvo dos oculos
inteligentes. Isso impoe restricoes de CPU (ARM Cortex-A53 quad-core), memoria
(1 GB RAM) e ausencia de GPU dedicada para inferencia. O pipeline completo
(camera → MediaPipe Hands → reconhecimento de gesto → acao) precisa caber nesse
envelope de recursos.

## Justificativa

A decisao de plataforma esta registrada em [[ADR-0007_Alvo_Raspberry_Pi3|ADR-0007]].
O Pi 3 e o gargalo de desempenho do projeto: MediaPipe Hands roda em CPU e o loop
de captura ([[main.py]]) processa frame a frame. Sem caber no Pi 3, o produto nao
existe como oculos autonomo.

## Criterios de aceitacao

| # | Criterio | Como medir | Meta |
|---|----------|------------|------|
| 1 | O app inicia sem erro no Pi 3 (Raspberry Pi OS) | Rodar `python main.py` e observar a janela do OpenCV | inicia sem crash |
| 2 | Taxa de processamento de frames utilizavel | FPS efetivo do loop `while cap.isOpened()` | a definir (medir em campo; baseline desejavel >= 10 FPS) |
| 3 | Reconhecimento de gesto responde sem travar a UI | Tempo entre gesto e disparo da acao | a definir |
| 4 | Uso de memoria nao satura 1 GB | `htop`/`free -m` durante operacao | a definir |

> Os numeros de FPS, latencia de deteccao e uso de memoria **nao** estao definidos
> no codigo. Devem ser medidos no hardware-alvo e fixados como baseline.

## Riscos e dependencias

- MediaPipe pode nao ter build oficial estavel para ARM/Pi 3 em todas as versoes —
  verificar disponibilidade do wheel (ver [[Ref_MediaPipe_Hands]]).
- `max_num_hands=2` em [[hands.py]] dobra o custo de inferencia por frame; reduzir
  para `1` e uma otimizacao possivel se o FPS ficar baixo.
- Funcoes de IA dependem de rede (ver [[RNF-006_Dependencia_Conectividade]]), o que
  desloca parte da carga para a nuvem mas adiciona latencia.

## Referencias

- [[ADR-0007_Alvo_Raspberry_Pi3|ADR-0007 · Alvo Raspberry Pi 3]]
- [[ADR-0001_MediaPipe_Hands|ADR-0001 · MediaPipe Hands]]
- [[RNF-004_Latencia_Resposta|RNF-004 · Latencia de resposta]]
- [[Arquitetura_Software|Arquitetura do software]]
- [[Ref_MediaPipe_Hands]]
