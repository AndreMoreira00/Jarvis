---
title: RISCO-001 · Desempenho no Raspberry Pi 3
id: RISCO-001
type: risco
status: aberto
prioridade: alta
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 00_SGI_Aplicado
tags: [risco, module/software, prio/alta, tema/hardware]
---

# RISCO-001 · Desempenho no Raspberry Pi 3

## Descricao

O pipeline de visao computacional (**OpenCV** + **MediaPipe Hands**, rodando a cada frame da camera) e as chamadas a IA (**Gemini**, **edge-tts**, **pygame**) podem **nao rodar em tempo real** no Raspberry Pi 3, plataforma-alvo do produto. O RPi 3 tem CPU ARM modesta e pouca memoria; o MediaPipe processa 21 landmarks por mao para ate 2 maos a cada frame, e o `Video_To_Text` ainda faz upload + polling do video no Gemini com `time.sleep(10)` bloqueante (comentado no proprio codigo como "Bomba, precisa ser limpo").

## Probabilidade x Impacto

| Dimensao | Avaliacao | Justificativa |
|---|---|---|
| Probabilidade | **Alta** | RPi 3 e notoriamente limitado para visao computacional em tempo real |
| Impacto | **Alto** | Se o FPS cair demais, o reconhecimento de gestos fica intermitente e o produto inviavel |
| Severidade resultante | **Alta** | — |

## Gatilhos / sintomas

- Queda de FPS na deteccao de mao a ponto de perder gestos.
- Travamento do loop durante `Video_To_Text` (polling bloqueante).
- Estouro de memoria/aquecimento ao manter MediaPipe + playback simultaneos.

## Mitigacoes

- Isolar tarefas pesadas em `ThreadPoolExecutor` (ja feito) para nao travar o loop `asyncio` — ver [[ADR-0004_Concorrencia_Asyncio_ThreadPool|ADR-0004]].
- Reduzir resolucao da camera / `max_num_hands` se necessario.
- Substituir o polling bloqueante de `Video_To_Text` por espera assincrona.
- Medir FPS e latencia reais em RPi 3 antes de fechar metas (hoje **a definir**).

## Dono e status

- Status: **aberto** (sem medicao em hardware ainda).
- Vinculado a [[OBJ-003_Portabilidade_Raspberry_Pi|OBJ-003]] e [[RNF-001_Execucao_Raspberry_Pi3|RNF-001]].

## Referencias

- [[ADR-0007_Alvo_Raspberry_Pi3|ADR-0007 · Alvo Raspberry Pi 3]]
- [[RNF-004_Latencia_Resposta|RNF-004 · Latencia de resposta]]
- [[Roadmap_Jarvis|Roadmap]]
- [[Home|Home — Jarvis]]
