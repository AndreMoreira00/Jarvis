---
title: OBJ-001 · Controle hands-free por gestos
id: OBJ-001
type: objetivo
status: aprovado
prioridade: alta
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 00_SGI_Aplicado
tags: [objetivo, module/software, prio/alta, tema/gestos]
---

# OBJ-001 · Controle hands-free por gestos

## Descricao

Permitir que o usuario opere o Jarvis **inteiramente com as maos no ar**, sem teclado, mouse, toque ou comando de voz para acionar funcoes. A camera frontal observa as maos, o **MediaPipe Hands** extrai os 21 landmarks por mao e a classe `Hands` reconhece, por geometria, cinco poses pre-definidas. Cada pose, combinada com a mao correta (esquerda/direita), dispara uma acao da classe `Control`.

Este e o objetivo central do produto: oculos inteligentes pressupoem interacao sem usar as maos para segurar um dispositivo — o gesto e a interface.

## Escopo

- Cinco gestos reconhecidos: **OK** (`Map_Ok`), **joinha/positivo** (`Map_Positive`), **dedo levantado** (`Map_Speak`), **"L"** (`Map_Squid`) e **rock** (`Map_Rock`).
- Cada gesto exige uma mao especifica (`hand_label == side`), evitando disparos ambiguos.
- Mecanismos de robustez: trava global `Control.ACTION` (impede acoes concorrentes) e `gesture_cooldown` (debounce em frames). Ver [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008]].

## Criterio mensuravel

| Metrica | Meta |
|---|---|
| Gestos reconhecidos | 5/5 disparam a acao correta com a mao certa |
| Falsos disparos consecutivos | 0, gracas ao `cooldown` + trava `ACTION` |
| Acionamento sem contato | 100% das acoes iniciadas por gesto (zero entrada por teclado/mouse, exceto `q` para sair) |

Validacao manual via [[TP-001_Validacao_Reconhecimento_Gestos|TP-001]].

## Referencias

- [[Mapa_Gestos|Mapa de Gestos]]
- [[RF-006_Reconhecimento_Cinco_Gestos|RF-006 · Reconhecimento de cinco gestos]]
- [[RNF-002_Operacao_Hands_Free|RNF-002 · Operacao hands-free]]
- [[ADR-0001_MediaPipe_Hands|ADR-0001 · MediaPipe Hands]]
- [[Home|Home — Jarvis]]
