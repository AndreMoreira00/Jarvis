---
title: Objetivos do Projeto — Jarvis
area: SGI_Aplicado
tags: [readme, module::sgi, objetivos, projeto, template]
project: Jarvis
layer: sgi
class: mtz
standard: ISO9001
parent: "[[sgi-mtz-6-1-01-matriz-integrada-riscos-oportunidades-desempenho]]"
created: 2026-06-27
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Objetivos do Projeto

Objetivos específicos deste projeto, derivados dos **4 objetivos integrados SGI** (cap. 6.2 ISO 9001). Cada objetivo aqui deve declarar no frontmatter `parent: [[sgi-mtz-oNN-...]]` para aparecer na [[Matriz_Integrada.base|Matriz Integrada]].

## Objetivos SGI de referência

- `sgi-mtz-o01-*` — objetivo 01 (ver Matriz Integrada)
- `sgi-mtz-o02-*` — objetivo 02
- `sgi-mtz-o03-*` — objetivo 03
- `sgi-mtz-o04-*` — objetivo 04

## Frontmatter sugerido para cada objetivo do projeto

```yaml
---
title: Objetivo — <descrição>
tipo: objetivo
layer: sgi
class: mtz
project: <NomeDoProjeto>
parent: "[[sgi-mtz-o01-...]]"   # qual objetivo SGI este deriva
meta: "<valor numérico alvo>"
prazo: YYYY-MM-DD
responsavel: <nome>
status: ativo
created: YYYY-MM-DD
---
```
