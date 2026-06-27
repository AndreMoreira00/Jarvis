---
title: docs_projeto
type: readme
status: aprovado
created: 2026-05-28
updated: 2026-05-28
tags: [readme, indice]
---

# docs_projeto

Documentacao do **repositorio template** e do **template de projeto** que ele entrega.

## Indice

### Sobre o repo template

- [[HOWTO]] — como clonar este repo e iniciar um projeto novo
- [[CONVENCOES]] — schema de properties, naming, tags, IDs
- [[HOOKS]] — regras do projeto injetadas via hook do Claude Code
- [[decisoes/README|decisoes/]] — registros de mudancas estruturais neste repo
- [[referencias/README|referencias/]] — resumos de links/normas/bibliotecas citadas

### Software do produto Jarvis

- [[arquitetura/README|arquitetura/]] — avaliacao e plano de refatoracao do codigo Python (visao + IA + TTS)

### Template de projeto (entregue para novos projetos)

- [[docs_Template_Projeto/Home|docs_Template_Projeto]] — esqueleto a ser duplicado
- [[docs_Template_Projeto/_templates/README|Templates Obsidian]] — moldes de notas

### Views (bases cross-projeto)

- [[_views/Documentos_por_Clausula.base|Documentos por clausula]]
- [[_views/Rascunhos_Pendentes.base|Rascunhos pendentes]]
- [[_views/Documentos_Obsoletos.base|Documentos obsoletos]]

## Para que existe esta pasta

Duas funcoes:

1. **Documentar o proprio repo template** (HOWTO, CONVENCOES, HOOKS, decisoes/, referencias/) — vive aqui apenas.
2. **Carregar o template de projeto** (`docs_Template_Projeto/`) que sera duplicado para cada projeto novo.

Quando clonar para um projeto real, a parte 1 e opcional (pode deletar) e a parte 2 e o que voce de fato usa.
