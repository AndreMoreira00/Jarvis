---
title: Planos_de_Teste — Jarvis
area: Testes_Validacao/Planos_de_Teste
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

# Planos de Teste

Planos de teste **manuais** (TP-NNN) do Jarvis. Nao ha suite automatizada nem linter — a validacao e feita rodando `python main.py` e observando a janela do OpenCV, os sons de confirmacao, os arquivos em `midia/` e a resposta falada. Use o template `Teste_Template` ao criar novos planos.

## Indice de planos

| ID | Plano | Requisitos cobertos | Status |
|----|-------|---------------------|--------|
| TP-001 | [[TP-001_Validacao_Reconhecimento_Gestos\|Validacao do reconhecimento de gestos]] | [[RF-006_Reconhecimento_Cinco_Gestos\|RF-006]], [[RF-008_Debounce_Cooldown_E_Trava_Acao\|RF-008]] | rascunho |
| TP-002 | [[TP-002_Validacao_Fluxo_IA_Gemini\|Validacao do fluxo de IA (Gemini)]] | [[RF-003_Pergunta_Voz_Resposta_Falada\|RF-003]], [[RF-004_Foto_Mais_Pergunta_Analise\|RF-004]], [[RF-005_Video_Mais_Pergunta_Analise\|RF-005]], [[RF-007_Resposta_Falada_Persona_Jarvis\|RF-007]] | rascunho |
| TP-003 | [[TP-003_Validacao_Captura_E_Upload\|Validacao de captura e upload]] | [[RF-001_Captura_Foto_Gesto_Ok\|RF-001]], [[RF-002_Gravacao_Video_Gesto_Positivo\|RF-002]], [[RF-009_Upload_Automatico_Google_Photos\|RF-009]] | rascunho |

A property `requisitos_cobertos` no frontmatter de cada plano alimenta a base [[Matriz_Rastreabilidade]], que cruza requisitos x testes e sinaliza requisitos orfaos e planos sem requisito vinculado.
