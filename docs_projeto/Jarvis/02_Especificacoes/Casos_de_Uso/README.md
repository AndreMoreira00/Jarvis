---
title: Casos_de_Uso — Jarvis
area: Especificacoes/Casos_de_Uso
tags: [readme, module/software, layer/especificacao, tema/gestos]
project: Jarvis
created: 2026-06-27
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Casos de Uso

Casos de uso do **Jarvis** (óculos inteligentes, controle por gestos). Cada caso de
uso descreve ator, pré-condições, gesto disparador (com mão e cooldown), fluxo
principal fiel ao código, fluxos alternativos/erros, pós-condições e requisitos
relacionados.

O ciclo por frame é: câmera (OpenCV) → MediaPipe Hands (21 landmarks) →
reconhecimento de gesto por geometria → ação (`Control`) → IA (Gemini) e/ou upload
(Google Photos) → resposta falada (edge-tts + pygame).

## Casos de uso

| ID | Caso de uso | Gesto (mão · cooldown) | Ação `Control` | Requisito |
|---|---|---|---|---|
| [[CU-001_Tirar_Foto\|CU-001]] | Tirar foto | OK · Direita · 20 | `Capture_Photo` | [[RF-001_Captura_Foto_Gesto_Ok\|RF-001]] |
| [[CU-002_Gravar_Video\|CU-002]] | Gravar vídeo | Positivo · Esquerda · 30 | `Capture_Video` | [[RF-002_Gravacao_Video_Gesto_Positivo\|RF-002]] |
| [[CU-003_Perguntar_Por_Voz\|CU-003]] | Perguntar por voz | Dedo levantado · Direita · 20 | `Audio_to_Audio` | [[RF-003_Pergunta_Voz_Resposta_Falada\|RF-003]] |
| [[CU-004_Analisar_Imagem_Com_Pergunta\|CU-004]] | Analisar imagem com pergunta | "L" · Esquerda · 20 | `Image_Audio` | [[RF-004_Foto_Mais_Pergunta_Analise\|RF-004]] |
| [[CU-005_Analisar_Video_Com_Pergunta\|CU-005]] | Analisar vídeo com pergunta | Rock · Direita · 20 | `Video_Audio` | [[RF-005_Video_Mais_Pergunta_Analise\|RF-005]] |

## Visão consolidada

- [[Mapa_Gestos|Mapa de gestos → ações]] — tabela mestra (gesto, método, mão,
  cooldown, ação, caso de uso, requisito), diagrama Mermaid, geometria de cada
  gesto e quirks conhecidos.

## Referências

- [[RF-006_Reconhecimento_Cinco_Gestos|RF-006 · Reconhecimento dos cinco gestos]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008 · Debounce, cooldown e trava de ação]]
- [[Arquitetura_Software|Arquitetura do software]]
