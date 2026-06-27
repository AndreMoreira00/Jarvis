---
title: Riscos do Projeto — Jarvis
area: SGI_Aplicado
tags: [readme, module::sgi, riscos, projeto, template]
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

# Riscos do Projeto

Riscos específicos deste projeto — mapeados a partir da **Matriz Integrada SGI** (cap. 6.1 ISO 9001 + cap. 8.5 ISO 17025). Cada risco aqui deve declarar no frontmatter `parent: [[sgi-mtz-rNN-...]]` para aparecer na [[Matriz_Integrada.base|Matriz Integrada]].

## Tipos de risco a considerar

- **Herdados** — derivados de `sgi-mtz-r01..r29` da Matriz Integrada (declarar `parent:`)
- **Específicos** — próprios do projeto, sem pai (criar na Matriz Integrada também, se materiais)

## Frontmatter sugerido para cada risco

```yaml
---
title: Risco — <descrição>
tipo: risco
layer: sgi
class: mtz
project: <NomeDoProjeto>
parent: "[[sgi-mtz-r01-...]]"   # opcional: risco SGI parent
probabilidade: 1..5
impacto: 1..5
controles_existentes: <texto>
plano_mitigacao: <texto>
responsavel: <nome>
status: aberto | mitigado | aceito | encerrado
created: YYYY-MM-DD
---
```

> `probabilidade × impacto` é calculado automaticamente em [[Matriz_Integrada.base|Matriz_Integrada.base]] via fórmula `nivel`.
