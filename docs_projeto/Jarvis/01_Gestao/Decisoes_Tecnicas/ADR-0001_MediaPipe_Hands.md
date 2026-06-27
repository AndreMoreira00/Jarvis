---
title: ADR-0001 · MediaPipe Hands para reconhecimento de gestos
type: adr
status: aceito
id: ADR-0001
deciders: [Andre Moreira]
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 01_Gestao
layer: gestao
tags: [adr, module/software, layer/gestao, tema/gestos, tema/visao-computacional]
---

# ADR-0001 · MediaPipe Hands para reconhecimento de gestos

## Contexto

O Jarvis e operado **hands-free**, sem teclado nem toque: o unico canal de
entrada de comandos sao gestos de mao captados pela camera do oculos (alvo
Raspberry Pi 3). Precisamos de um detector de mao em tempo real que:

- rode no loop de video (`cv2.VideoCapture(0)` em [[Arquitetura_Software|main.py]]),
  frame a frame, sem travar o `asyncio`;
- forneca pontos articulares estaveis o suficiente para distinguir **5 gestos**
  distintos (OK, joinha, dedo levantado, "L" e rock);
- nao exija coleta de dataset nem treino, dado que o projeto e de um desenvolvedor
  so e a iteracao precisa ser rapida.

A geometria dos dedos e suficiente para separar os gestos alvo, entao bastava uma
fonte confiavel de **landmarks** (coordenadas dos pontos da mao).

## Decisao

Adotar **MediaPipe Hands** (`mp.solutions.hands.Hands`) como detector e
implementar o **reconhecimento dos gestos em geometria propria** sobre os 21
landmarks, sem classificador treinado.

Configuracao usada em [hands.py](../../../../hands.py) (`class Hands`):

| Parametro | Valor | Motivo |
|---|---|---|
| `static_image_mode` | `False` | Modo video: usa tracking entre frames, mais leve |
| `max_num_hands` | `2` | Detecta as duas maos; o gesto so dispara se `hand_label` casar com o lado exigido |
| `min_detection_confidence` | `0.5` | Limiar de deteccao |
| `min_tracking_confidence` | `0.5` | Limiar de rastreamento |

Cada metodo `Map_*(h, w, hand_landmarks, frame)` converte os landmarks
normalizados para pixels (`x*w`, `y*h`) e compara coordenadas. O **eixo Y cresce
para baixo**, entao "Y menor" significa ponto mais alto. Os thresholds sao
**relativos** ao tamanho do frame (`0.05*w` ou `0.05*h`), nunca pixels absolutos.

Mapa de gestos reconhecidos (geometria resumida):

| Metodo | Gesto | Regra (resumo) |
|---|---|---|
| `Map_Ok` | OK / pinca | polegar(4) proximo do indicador(8), distancia `< 0.05*w`, demais dedos baixos |
| `Map_Positive` | joinha | polegar(4) levantado (`< polegar(1)_y - 0.05*h`), demais dobrados |
| `Map_Speak` | dedo levantado | so o indicador levantado, polegar lateral, demais dobrados |
| `Map_Squid` | "L" | indicador levantado e polegar aberto (`polegar(4)_x < polegar(2)_x`) |
| `Map_Rock` | rock | indicador e mindinho levantados, medio e anelar dobrados |

Cada `Map_*` retorna `True` apenas quando a pose e detectada, e e usado como
predicado na lista `checks` de [[Arquitetura_Software|main.py]]. O detalhamento
do mapa gesto → acao esta em [[Mapa_Gestos]].

## Alternativas consideradas

| Alternativa | Por que foi descartada |
|---|---|
| **Modelo customizado treinado** (CNN/MLP sobre imagens ou landmarks) | Exige coletar e rotular dataset, treinar e versionar pesos; custo alto para 1 dev e 5 gestos. Pode voltar a ser considerado se a geometria se mostrar fragil demais. |
| **OpenCV puro** (Haar cascade / contornos / convex hull) | Reconhecimento de mao por contorno e muito sensivel a fundo, pele e iluminacao; nao entrega pontos articulares estaveis. Mais codigo e menos robusto que MediaPipe. |
| **Luvas / sensores (IMU, flex sensors)** | Quebra o requisito hands-free "natural" e adiciona hardware vestivel extra ao oculos. Inviavel para o form factor alvo. |

## Consequencias

### Positivas

- **Zero treino**: gestos novos sao adicionados escrevendo um novo `Map_*`,
  ciclo de iteracao muito curto.
- **Tempo real e robusto a fundo**: MediaPipe entrega landmarks estaveis mesmo
  com fundos variados, melhor que abordagens de contorno.
- **Thresholds relativos ao frame** tornam a deteccao parcialmente independente
  da resolucao da camera.
- **`max_num_hands=2` + filtro por lado** permite mapear gestos diferentes para a
  mao direita e a esquerda sem ambiguidade (ver [[Mapa_Gestos]]).

### Negativas / riscos

- **Fragilidade dos thresholds**: as regras geometricas sao sensiveis a
  **iluminacao**, **distancia** e **angulo** da mao. Variacoes podem gerar
  falsos negativos (gesto nao reconhecido) ou falsos positivos.
- **Sem tolerancia configuravel**: os limiares `0.05*w`/`0.05*h` sao fixos no
  codigo; nao ha calibracao por usuario.
- **Custo de inferencia no RPi3**: MediaPipe Hands em CPU ARM pode reduzir o FPS
  e impactar a fluidez do loop — risco a validar no hardware alvo (ver [[ADR-0007_Alvo_Raspberry_Pi3]]).
- **Estimativa de distancia desativada**: `calculusNormalDistance` (landmarks 5 e
  17) esta **comentada** em main.py; nao ha filtro de "mao perto/longe" para
  evitar disparos acidentais.
- A validacao do reconhecimento e **manual** (sem suite de testes) — coberta pelo
  plano [[TP-001_Validacao_Reconhecimento_Gestos]].

## Referencias

- [[Ref_MediaPipe_Hands]] — referencia da biblioteca MediaPipe Hands
- [[RF-006_Reconhecimento_Cinco_Gestos]] — requisito funcional dos 5 gestos
- [[Mapa_Gestos]] — mapa completo gesto → mao → acao
- [[Arquitetura_Software]] — visao geral do loop e da lista `checks`
- [[TP-001_Validacao_Reconhecimento_Gestos]] — plano de teste do reconhecimento
- [[ADR-0007_Alvo_Raspberry_Pi3]] — alvo de hardware e seus limites
- [[RNF-002_Operacao_Hands_Free]] — requisito de operacao sem maos
