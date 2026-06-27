---
title: Referencias externas
type: readme
status: aprovado
created: 2026-05-28
updated: 2026-05-28
tags: [readme, referencias]
---

# Referencias externas

Resumos de URLs, bibliotecas, normas ou conceitos citados durante o desenvolvimento que **nao** sao especificos a um projeto (esses ficam em `docs_Template_Projeto/10_Referencias/`).

> Regra 6 do projeto: se o usuario cita um link/biblioteca/conceito que o Claude nao domina, o Claude ingere via defuddle/WebFetch e salva um resumo aqui antes de prosseguir.

## Convencao

- Um arquivo por referencia: `<slug-da-referencia>.md`
- Frontmatter minimo: `title`, `source` (URL ou citacao), `type: referencia`, `tags`, `created`, `updated`
- Conteudo: resumo executivo + trechos relevantes citaveis + link/fonte

## Indice

- [[pytest-mock-total]] — padrao de mock total via `sys.modules` + stack pytest/pytest-cov/pytest-asyncio
