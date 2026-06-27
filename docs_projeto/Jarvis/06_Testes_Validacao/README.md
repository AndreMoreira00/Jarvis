---
title: Testes & Validação — Jarvis
area: Testes_Validacao
tags: [readme, template, projeto]
project: Jarvis
created: 2026-06-27
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Testes & Validação

Modulo de testes e validacao do **Jarvis**. Como o app nao tem suite automatizada nem linter, toda verificacao e **manual**, rodando `python main.py`. Aqui ficam os planos de teste (TP), os relatorios de execucao (em `Relatorios/`) e o registro de bugs conhecidos (BUG).

## Planos de teste (manuais)

| ID | Plano | Requisitos cobertos | Status |
|----|-------|---------------------|--------|
| TP-001 | [[TP-001_Validacao_Reconhecimento_Gestos\|Validacao do reconhecimento de gestos]] | RF-006, RF-008 | rascunho |
| TP-002 | [[TP-002_Validacao_Fluxo_IA_Gemini\|Validacao do fluxo de IA (Gemini)]] | RF-003, RF-004, RF-005, RF-007 | rascunho |
| TP-003 | [[TP-003_Validacao_Captura_E_Upload\|Validacao de captura e upload]] | RF-001, RF-002, RF-009 | rascunho |

Detalhes e indice completo em [[Planos_de_Teste/README\|Planos de Teste]].

## Bugs conhecidos

| ID | Bug | Severidade | Status |
|----|-----|------------|--------|
| BUG-001 | [[BUG-001_Video_Audio_Sem_Executor\|Video_Audio chama Capture_Audio sem o argumento executor]] | alta | aberto |
| BUG-002 | [[BUG-002_Recycle_Midia_Sem_Self\|Recycle_midia definido sem self]] | media | aberto |
| BUG-003 | [[BUG-003_ProjectConfig_Mkdir_Sem_ExistOk\|ProjectConfig usava os.mkdir sem exist_ok]] | media | fechado (corrigido) |

## Rastreabilidade

A base [[Matriz_Rastreabilidade]] agora cruza **requisitos x testes**: usa a property `verificado_por` nos requisitos e `requisitos_cobertos` nos planos de teste para listar requisitos orfaos (sem TP que verifica), planos sem requisito vinculado e a cobertura geral.

## Subpastas

| Pasta | Conteudo |
|-------|----------|
| `Planos_de_Teste/` | Planos TP-NNN (manuais) |
| `Relatorios/` | Relatorios de execucao (RT-NNN) |
| `Testes_Ambientais/`, `Testes_Campo/`, `Testes_EMC_EMI/`, `Testes_Seguranca/` | Reservadas (herdadas do template; nao aplicaveis ao software puro hoje) |
