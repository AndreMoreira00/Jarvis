---
title: Requisitos_Funcionais — Jarvis
area: Especificacoes/Requisitos_Funcionais
tags: [readme, template, projeto, pendente::ingestao]
project: Jarvis
created: 2026-06-27
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Requisitos Funcionais

Requisitos funcionais (RF-NNN) do **Jarvis** — o que o software dos oculos inteligentes deve fazer. Cada requisito mapeia um gesto, fluxo de IA ou mecanismo de controle para um comportamento verificavel, com criterios de aceitacao e testes associados.

## Indice

| ID | Titulo | Prioridade | Status |
|----|--------|-----------|--------|
| RF-001 | [[RF-001_Captura_Foto_Gesto_Ok\|Captura de foto por gesto OK]] | alta | aprovado |
| RF-002 | [[RF-002_Gravacao_Video_Gesto_Positivo\|Gravacao de video por gesto positivo]] | alta | aprovado |
| RF-003 | [[RF-003_Pergunta_Voz_Resposta_Falada\|Pergunta por voz com resposta falada]] | alta | aprovado |
| RF-004 | [[RF-004_Foto_Mais_Pergunta_Analise\|Foto + pergunta com analise de imagem]] | alta | aprovado |
| RF-005 | [[RF-005_Video_Mais_Pergunta_Analise\|Video + pergunta com analise de video]] | media | aprovado |
| RF-006 | [[RF-006_Reconhecimento_Cinco_Gestos\|Reconhecimento de cinco gestos via MediaPipe]] | critica | aprovado |
| RF-007 | [[RF-007_Resposta_Falada_Persona_Jarvis\|Resposta falada com persona Jarvis]] | alta | aprovado |
| RF-008 | [[RF-008_Debounce_Cooldown_E_Trava_Acao\|Debounce por cooldown e trava de acao]] | alta | aprovado |
| RF-009 | [[RF-009_Upload_Automatico_Google_Photos\|Upload automatico para o Google Photos]] | media | aprovado |

## Notas relacionadas

- Casos de uso: [[Mapa_Gestos|Mapa de gestos]], [[CU-001_Tirar_Foto|CU-001]], [[CU-002_Gravar_Video|CU-002]], [[CU-003_Perguntar_Por_Voz|CU-003]], [[CU-004_Analisar_Imagem_Com_Pergunta|CU-004]], [[CU-005_Analisar_Video_Com_Pergunta|CU-005]]
- Testes: [[TP-001_Validacao_Reconhecimento_Gestos|TP-001]], [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002]], [[TP-003_Validacao_Captura_E_Upload|TP-003]]
- Arquitetura: [[Arquitetura_Software|Arquitetura do software]], [[Referencia_Modulos|Referencia de modulos]]
