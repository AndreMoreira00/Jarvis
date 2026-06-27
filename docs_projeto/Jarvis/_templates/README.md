---
title: Templates
area: _templates
tags: [templates, convencoes]
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
type: readme
status: aprovado
---

# Templates

Notas-molde usadas pelo core plugin **Templates** do Obsidian. Inserir com `Ctrl+P` → "Insert template" (configurado em `.obsidian/templates.json` apontando para esta pasta).

## Disponiveis

| Template | ID prefixo | Modulo padrao | Uso |
|----------|------------|---------------|-----|
| [[ADR_Template]] | `ADR-XXXX` | 01_Gestao | Decisoes tecnicas com contexto, alternativas e consequencias |
| [[Requisito_Template]] | `RF-XXX` / `RNF-XXX` | 02_Especificacoes | Requisitos funcionais ou nao-funcionais com criterios verificaveis |
| [[Teste_Template]] | `TP-XXX` | 06_Testes_Validacao | Plano de teste vinculado a requisitos |
| [[Ata_Template]] | `ATA-YYYYMMDD` | 01_Gestao | Ata de reuniao com decisoes e action items |
| [[Bug_Template]] | `BUG-XXX` | 06_Testes_Validacao | Registro de defeito com passos para reproduzir |
| [[Release_Template]] | `REL-vX.Y.Z` | 04_Firmware | Release notes versionadas |

## Convencao para criar novos templates

1. Frontmatter obrigatorio: `title`, `id`, `type`, `status`, `created`, `updated`, `project`, `module`, `tags`.
2. Usar `{{date:YYYY-MM-DD}}` para datas dinamicas e `{{title}}` para o nome.
3. Manter o `id` no padrao `<PREFIXO>-<NUMERO>` (ver [[../../../CONVENCOES|Convencoes]]).
4. Adicionar a entrada na tabela acima ao criar um novo template.

> Schema de properties e taxonomia de tags estao em [[../../../CONVENCOES|docs_projeto/CONVENCOES.md]].
