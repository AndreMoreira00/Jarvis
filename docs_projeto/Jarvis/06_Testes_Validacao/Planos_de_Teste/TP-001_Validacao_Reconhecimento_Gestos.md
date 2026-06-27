---
title: TP-001 · Validacao do Reconhecimento de Gestos
id: TP-001
type: plano-de-teste
status: rascunho
requisitos_cobertos: [RF-006, RF-008]
executante:
data_execucao:
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 06_Testes_Validacao
prioridade: alta
tags: [teste, plano, tema/gestos, layer/teste, prio/alta]
---

# TP-001 · Validacao do Reconhecimento de Gestos

## Objetivo

Verificar que cada um dos **cinco gestos** suportados e reconhecido pela geometria dos 21 landmarks do MediaPipe (`hands.py`) **somente com a mao correta** (Right/Left), e que cada deteccao dispara a acao correspondente **uma unica vez**, respeitando o `gesture_cooldown` (debounce em frames) e a trava global `Control.ACTION`.

Este e um teste **manual** — nao ha suite automatizada. A validacao e feita rodando `python main.py` e observando a janela do OpenCV mais o comportamento de audio/midia.

## Requisitos verificados

- [[RF-006_Reconhecimento_Cinco_Gestos|RF-006 · Reconhecimento de cinco gestos]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008 · Debounce, cooldown e trava de acao]]

Relacionado: [[Mapa_Gestos|Mapa Gestos]], [[ADR-0001_MediaPipe_Hands|ADR-0001 · MediaPipe Hands]].

## Equipamento e setup

| Item | Requisito | Observacao |
|------|-----------|------------|
| Webcam | Conectada e reconhecida como dispositivo `0` | `cv2.VideoCapture(0)` |
| Microfone | Conectado | Necessario para os gestos que capturam audio (`Map_Speak`, `Map_Squid`, `Map_Rock`) |
| `.env` | `API_GEMINI=<chave>` | Lido em `jarvis.py`; sem ele o construtor de `Control`/`Jarvis` ainda inicia, mas a acao falha ao chamar o Gemini |
| `env/client_secret.json` | OAuth desktop | Necessario para o upload disparado por `Map_Ok`/`Map_Positive` |
| Pastas `response/` e `midia/` | Existentes | Criar com `python ProjectConfig.py` |
| Iluminacao | Boa, fundo limpo | Thresholds sao relativos a `0.05*w` / `0.05*h`; baixa luz degrada a deteccao |

Setup: rodar `python main.py` a partir da raiz do repo. Aguardar a janela `MediaPipe Hands` abrir.

## Mapa gesto -> acao sob teste

| Gesto (`Hands.Map_*`) | Mao exigida (`side`) | Cooldown (frames) | Acao (`Control`) |
|---|---|---|---|
| OK / pinca (`Map_Ok`) | Right | 20 | `Capture_Photo` |
| Joinha / positivo (`Map_Positive`) | Left | 30 | `Capture_Video` |
| Dedo levantado (`Map_Speak`) | Right | 20 | `Audio_to_Audio` |
| "L" (`Map_Squid`) | Left | 20 | `Image_Audio` |
| Rock (`Map_Rock`) | Right | 20 | `Video_Audio` |

## Procedimento

Repetir o bloco abaixo para **cada um dos cinco gestos**.

1. Posicionar a mao **correta** (conforme `side` na tabela) diante da camera, com a pose do gesto bem formada, dentro do enquadramento.
2. Observar os landmarks desenhados sobre a mao na janela (confirma que o MediaPipe detectou a mao).
3. Confirmar que a acao dispara **uma vez**: som de confirmacao (`audios_check/`) e/ou criacao de arquivo em `midia/` e/ou resposta falada.
4. **Manter** o gesto por ~1 segundo. Confirmar que a acao **NAO** dispara repetidamente (o `gesture_cooldown` foi setado para o valor da tabela e e decrementado 1 por frame).
5. Desfazer o gesto, aguardar o cooldown expirar e repetir para validar que dispara de novo.

Testes negativos (anti-falso-positivo):

6. Fazer o **mesmo gesto com a mao errada** (ex.: OK com a mao Left). Confirmar que a acao **NAO** dispara (`hand_label == side` falha em `Check_Gesture`).
7. Durante uma acao longa em andamento (ex.: gravacao de video ou resposta falada do Gemini), tentar outro gesto. Confirmar que nada dispara enquanto `Control.ACTION == True`.

> Quirk conhecido (documentar no resultado, nao e bug do teste): todo gesto disparado **alterna** `Control.Control_Video` em `Check_Gesture`, entao a flag de gravacao liga/desliga a cada acao, nao apenas no gesto de video. Ver [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002]].

## Criterios de aprovacao

- [ ] Os 5 gestos sao reconhecidos com a mao correta e disparam a acao esperada.
- [ ] Cada deteccao dispara a acao **exatamente uma vez** por gesto (sem repeticao durante o cooldown).
- [ ] O cooldown observado e coerente com a tabela (20 frames para a maioria, 30 para `Map_Positive`).
- [ ] Nenhum gesto dispara com a **mao errada**.
- [ ] Nenhum gesto dispara enquanto `Control.ACTION == True` (outra acao em andamento).
- [ ] Taxa de falsos positivos baixa em fundo limpo e boa iluminacao (criterio qualitativo — registrar % aproximada).

## Resultados

Registrar a execucao em um relatorio de teste (`RT-XXX`) na pasta `Relatorios/` (quando criado).

| Gesto | Detectado? | Disparo unico? | Mao errada bloqueada? | Observacoes |
|-------|-----------|----------------|-----------------------|-------------|
| `Map_Ok` | | | | |
| `Map_Positive` | | | | |
| `Map_Speak` | | | | |
| `Map_Squid` | | | | |
| `Map_Rock` | | | | |

Ver relatorio: [[]]

## Referencias

- [[RF-006_Reconhecimento_Cinco_Gestos|RF-006 · Reconhecimento de cinco gestos]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008 · Debounce, cooldown e trava de acao]]
- [[Mapa_Gestos|Mapa Gestos]]
- [[ADR-0001_MediaPipe_Hands|ADR-0001 · MediaPipe Hands]]
- [[Ref_MediaPipe_Hands|Referencia · MediaPipe Hands]]
- [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002 · Validacao do fluxo de IA]]
- [[TP-003_Validacao_Captura_E_Upload|TP-003 · Validacao de captura e upload]]
