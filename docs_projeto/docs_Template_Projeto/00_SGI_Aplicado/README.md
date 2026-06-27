---
title: 00 · SGI Aplicado — _Template_Projeto
area: SGI_Aplicado
tags: [readme, module/sgi, projeto, template]
project: _Template_Projeto
layer: sgi
created: 2026-05-28
updated: 2026-05-28
module: 00_SGI_Aplicado
type: readme
status: aprovado
---

# 00 · SGI Aplicado

Pasta onde se documenta como normas, procedimentos e gates de qualidade se aplicam **a este projeto**. Mantenha aqui apenas o que e relevante ao escopo — o restante fica no SGI corporativo (que pode ser referenciado externamente).

> **Template.** Ao duplicar para um novo projeto, substitua `project: _Template_Projeto` no frontmatter e popule as subpastas conforme necessario.

## Indice

- [[Objetivos_do_Projeto/README|Objetivos do Projeto]] — metas mensuraveis (qualidade, prazo, custo, regulatorio)
- [[Riscos_do_Projeto/README|Riscos do Projeto]] — matriz de riscos especificos
- [[Procedimentos_Aplicaveis|Procedimentos Aplicaveis]] — normas e procedimentos adotados (ISO 9001, ISO 17025, ISO 14971, etc., conforme aplicavel)
- [[Auditorias_do_Projeto/README|Auditorias do Projeto]]
- [[NCs_do_Projeto/README|Nao Conformidades]]
- [[Gates_Aprovacoes/README|Gates / Aprovacoes]]
- [[Registros_do_Projeto/README|Registros do Projeto]]

## Como usar

1. Defina os objetivos do projeto em `Objetivos_do_Projeto/` (cada objetivo e uma nota com criterio mensuravel).
2. Mapeie riscos em `Riscos_do_Projeto/` (probabilidade × impacto, dono, mitigacao).
3. Liste em `Procedimentos_Aplicaveis` quais normas/procedimentos foram adotados, com revisao/versao.
4. Registros preenchidos (formularios, evidencias) entram em `Registros_do_Projeto/`.
5. NCs abertas neste projeto entram em `NCs_do_Projeto/` (uma nota por NC).
6. Cada gate aprovado gera uma nota em `Gates_Aprovacoes/` com assinatura/evidencia.

> Se sua organizacao tem um SGI/SGQ corporativo, esta pasta e a ponte: ela aplica o SGI ao projeto, mas nao substitui o repositorio canonico.
