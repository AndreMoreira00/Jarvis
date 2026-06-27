---
title: RF-006 · Reconhecimento de cinco gestos via MediaPipe
id: RF-006
type: requisito
categoria: funcional
status: aprovado
prioridade: critica
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
verificado_por: [TP-001_Validacao_Reconhecimento_Gestos]
tags: [requisito, funcional, module/software, layer/especificacao, prio/critica, tema/gestos, tema/visao]
---

# RF-006 · Reconhecimento de cinco gestos via MediaPipe

## Descricao

O sistema deve reconhecer **cinco gestos de mao** a partir dos 21 landmarks do MediaPipe Hands, associando cada gesto a uma mao especifica (direita ou esquerda) e a uma acao, respeitando o cooldown configurado por gesto. O reconhecimento ocorre por geometria dos landmarks (coordenadas convertidas para pixels `x*w`, `y*h`; eixo Y cresce para baixo), com thresholds relativos a `0.05*w` ou `0.05*h`.

| Gesto | Metodo | Mao exigida | Cooldown | Acao |
|---|---|---|---|---|
| OK / pinca | `Map_Ok` | Right | 20 | `Capture_Photo` |
| Positivo / joinha | `Map_Positive` | Left | 30 | `Capture_Video` |
| Dedo levantado | `Map_Speak` | Right | 20 | `Audio_to_Audio` |
| "L" | `Map_Squid` | Left | 20 | `Image_Audio` |
| Rock | `Map_Rock` | Right | 20 | `Video_Audio` |

O MediaPipe e configurado com `max_num_hands=2`, `min_detection_confidence=0.5`, `min_tracking_confidence=0.5`. A associacao gesto→mao→acao vive na lista `checks` em `main.py`; o casamento mao correta acontece em `Check_Gesture` (`hand_label == side`).

## Criterios de aceitacao

- [ ] Cada um dos 5 gestos (`Map_Ok`, `Map_Positive`, `Map_Speak`, `Map_Squid`, `Map_Rock`) retorna `True` quando a pose correspondente e detectada.
- [ ] Um gesto so dispara sua acao quando feito com a mao exigida (`hand_label == side`): OK/dedo/rock com a direita; positivo/L com a esquerda.
- [ ] Gestos feitos com a mao errada nao disparam acao.
- [ ] Apos um disparo, o gesto respeita o cooldown configurado (20 ou 30 frames) antes de poder disparar novamente (ver [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008]]).
- [ ] Nenhum gesto e avaliado enquanto `ACTION == True` (uma acao de IA em andamento bloqueia novos disparos).
- [ ] Os landmarks sao desenhados na janela `MediaPipe Hands` para feedback visual.

## Casos de uso associados

- [[Mapa_Gestos|Mapa de gestos]]
- [[CU-001_Tirar_Foto|CU-001]], [[CU-002_Gravar_Video|CU-002]], [[CU-003_Perguntar_Por_Voz|CU-003]], [[CU-004_Analisar_Imagem_Com_Pergunta|CU-004]], [[CU-005_Analisar_Video_Com_Pergunta|CU-005]]

## Testes que verificam

- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Validacao de reconhecimento de gestos]]

## Observacoes

- A deteccao usa thresholds fixos relativos ao tamanho do frame; iluminacao, distancia da mao e angulo afetam a robustez. A funcao de estimativa de distancia (`calculusNormalDistance`) esta **comentada/desativada** em `main.py`.
- Gestos podem ter falsos positivos/negativos por similaridade geometrica (ex.: "L" vs. dedo levantado). Validacao e manual — ver [[TP-001_Validacao_Reconhecimento_Gestos|TP-001]].
- O alvo de execucao e o Raspberry Pi 3, onde o custo do MediaPipe impacta o frame rate. Ver [[RNF-001_Execucao_Raspberry_Pi3|RNF-001]] e [[ADR-0007_Alvo_Raspberry_Pi3|ADR-0007]].

## Referencias

- [[ADR-0001_MediaPipe_Hands|ADR-0001 · MediaPipe Hands]]
- [[Ref_MediaPipe_Hands|Referencia MediaPipe Hands]]
- [[Referencia_Modulos|Referencia de modulos]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008 · Debounce, cooldown e trava]]
