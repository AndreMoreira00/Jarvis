---
title: MediaPipe Hands
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 10_Referencias
categoria: visao-computacional
tags: [referencia, biblioteca, module/software, tema/gestos]
---

# MediaPipe Hands

## O que e

Solucao de rastreamento de maos do **MediaPipe** (Google). Detecta ate N maos em
imagem/video e devolve, por mao, **21 landmarks** (pontos) normalizados em `x`, `y`
(faixa 0..1, relativos a largura/altura do frame) e `z` (profundidade relativa),
mais a classificacao de lateralidade (`Right`/`Left`). E a base do controle por
gestos do Jarvis: nenhum gesto e reconhecido sem esses landmarks.

## Como o Jarvis usa

Encapsulada em [[Ref_OpenCV|cv2]]-friendly na classe `Hands` ([hands.py](hands.py)).

| Item | Detalhe no codigo |
|---|---|
| Instanciacao | `mp.solutions.hands.Hands(...)` no `__init__` |
| `static_image_mode` | `False` (modo video, com tracking entre frames) |
| `max_num_hands` | `2` |
| `min_detection_confidence` | `0.5` |
| `min_tracking_confidence` | `0.5` |
| Desenho | `mp.solutions.drawing_utils` -> `draw_landmarks(..., HAND_CONNECTIONS)` em [main.py](main.py) |
| Processamento | `hands_system.hands.process(rgb_frame)` em [main.py](main.py) |

O resultado expoe `results.multi_hand_landmarks` (geometria) e
`results.multi_handedness` (lateralidade via `classification[0].label`). Cada metodo
`Map_*` da classe `Hands` recebe `(h, w, hand_landmarks, frame)`, converte os
landmarks para **pixels** (`int(landmark.x * w)`, `int(landmark.y * h)`) e compara
coordenadas para decidir a pose. Thresholds usados sao relativos (`0.05 * w` ou
`0.05 * h`). Detalhes dos cinco gestos em [[Mapa_Gestos|Mapa de Gestos]] e
[[RF-006_Reconhecimento_Cinco_Gestos|RF-006]].

> Convencao de eixos: `y` cresce para **baixo**, entao "y menor" significa ponto
> mais **alto** na imagem. Isso explica comparacoes como `indicador_8_y < indicador_5_y - 0.05*h`.

## Pontos de atencao

- **Custo no Raspberry Pi 3**: MediaPipe Hands e relativamente pesado para a CPU do
  Pi 3 (alvo do projeto, ver [[ADR-0007_Alvo_Raspberry_Pi3|ADR-0007]]). A taxa de
  frames real e o que limita a fluidez do controle por gestos.
- **Confidences em 0.5**: valores baixos favorecem deteccao em condicoes ruins, mas
  aumentam falsos positivos. Combinar com o debounce de [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008]].
- **Lateralidade espelhada**: o rotulo `Right`/`Left` segue a convencao do MediaPipe
  e pode parecer invertido dependendo de espelhamento da camera; o mapeamento
  gesto -> mao exigida depende disso.
- **Versao**: a API `mp.solutions.hands` e estavel mas o pacote `mediapipe` muda;
  versao exata **verificar** em `requirements.txt`.

## Link oficial

- https://developers.google.com/mediapipe

## Referencias

- [[hands.py|Codigo: hands.py (classe Hands)]]
- [[ADR-0001_MediaPipe_Hands|ADR-0001 — Escolha do MediaPipe Hands]]
- [[RF-006_Reconhecimento_Cinco_Gestos|RF-006 — Reconhecimento de cinco gestos]]
- [[Mapa_Gestos|Mapa de Gestos]]
- [[Ref_OpenCV|Referencia: OpenCV]]
- [[Arquitetura_Software|Arquitetura do Software]]
