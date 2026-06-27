---
title: Configuracao inicial da estrutura Obsidian do template
type: decisao-repo
status: aprovado
date: 2026-05-28
created: 2026-05-28
updated: 2026-05-28
tags: [decisao, obsidian, template, configuracao]
---

# Configuracao inicial da estrutura Obsidian do template

## Contexto

O repositorio ja tinha um esqueleto de 14 modulos em `docs_projeto/docs_Template_Projeto/` clonado de uma vault Sanesoluti corporativa, mas:

- `.obsidian/templates.json` apontava para `Sanesoluti/01_Projetos/_Template_Projeto/_templates` — path que so existe dentro da vault Sanesoluti, nao deste repo. Templates nao apareciam no `Ctrl+P`.
- Templates ADR/Requisito/Teste tinham `created: 2026-04-22` e `updated: 2026-04-23` hard-coded — toda nota nova inseria as datas erradas.
- `Home.md` referenciava wikilinks para `Sanesoluti/00_SGQ_Sistema_Gestao_Qualidade/...` que nao resolvem fora da vault Sanesoluti.
- `00_SGI_Aplicado/README.md` falava em "SGI da Sanesoluti", "FO-001", "PR-007" — acoplado a uma organizacao especifica.
- Nao existia documentacao de schema de properties/tags/IDs.
- Nao existia HOWTO de como clonar e usar o template.
- Faltavam templates basicos: ata de reuniao, bug, release notes.

## Decisao

Tornar o template **standalone e generico**:

1. **Remover toda referencia a Sanesoluti** dos arquivos do template (Home.md, 00_SGI/README, templates.json, graph.json). Skills de scaffolding (`.claude/skills/obsidian-tool`, `obsidian-project`) ficaram intocadas porque sao ferramentas independentes do template.
2. **Corrigir `.obsidian/templates.json`** apontando para `docs_projeto/docs_Template_Projeto/_templates` e adicionando `format: YYYY-MM-DD`.
3. **Reescrever templates** ADR/Requisito/Teste com `{{date:YYYY-MM-DD}}` em `created/updated` e padronizar frontmatter (adicionar `id`, `project`, `module`).
4. **Criar 3 templates novos**: `Ata_Template.md`, `Bug_Template.md`, `Release_Template.md`.
5. **Documentar schema** em `docs_projeto/CONVENCOES.md`: properties obrigatorias/opcionais, valores de `type`/`status`, taxonomia de tags, formato de IDs por tipo, regras de wikilinks.
6. **Criar `docs_projeto/HOWTO.md`** com fluxo de clonar → duplicar pasta → ajustar frontmatter → escolher modulos → inserir templates.
7. **Criar `docs_projeto/README.md`** como indice da pasta.
8. **Reescrever `00_SGI_Aplicado/README.md`** generico (norma + procedimento + gate) sem citar nenhuma organizacao especifica.
9. **Atualizar `.obsidian/graph.json`** trocando colorGroup Sanesoluti por colorGroups por `type:` (adr, requisito, plano-de-teste).

## Alternativas consideradas

- **Enxugar para 5-6 modulos universais** — descartado: usuario escolheu "misto/generico", quer template abrangente.
- **Scaffolding ativo (script que gera template sob demanda)** — descartado nesta iteracao: complexidade desnecessaria para tirar o template do estado quebrado. Pode ser feito depois.
- **Manter wikilinks SGQ como ponteiro opcional** — descartado: usuario foi explicito em "remover referencia de qualquer coisa da Sanesoluti".

## Consequencias

### Positivas
- Template usavel sem dependencia de vault externa.
- Templates inseriveis via `Ctrl+P` com datas corretas.
- Schema documentado — bases (`.base`) podem evoluir confiando no schema.
- Novos templates (Ata, Bug, Release) cobrem casos comuns que faltavam.

### Negativas / riscos
- Quem usava este repo dentro da vault Sanesoluti perde os wikilinks bidirecionais para o SGQ. Solucao: trazer apenas as notas SGQ essenciais para o repo se necessario, ou aceitar como standalone.
- 14 modulos ainda e muito para projetos simples — proximos passos podem oferecer perfis (`hw_embarcado`, `sw_puro`, etc).
- Templates skills (`.claude/skills/obsidian-tool`, `obsidian-project`) continuam apontando para a vault Sanesoluti; se esse repo for usado para gerar projetos via skill, essas skills precisam ser revisadas.

## Arquivos alterados/criados

Alterados:
- `.obsidian/templates.json`
- `.obsidian/graph.json`
- `docs_projeto/docs_Template_Projeto/Home.md`
- `docs_projeto/docs_Template_Projeto/00_SGI_Aplicado/README.md`
- `docs_projeto/docs_Template_Projeto/_templates/README.md`
- `docs_projeto/docs_Template_Projeto/_templates/ADR_Template.md`
- `docs_projeto/docs_Template_Projeto/_templates/Requisito_Template.md`
- `docs_projeto/docs_Template_Projeto/_templates/Teste_Template.md`

Criados:
- `docs_projeto/README.md`
- `docs_projeto/CONVENCOES.md`
- `docs_projeto/HOWTO.md`
- `docs_projeto/decisoes/README.md`
- `docs_projeto/decisoes/2026-05-28_configuracao_obsidian_template.md` (este arquivo)
- `docs_projeto/referencias/README.md`
- `docs_projeto/docs_Template_Projeto/_templates/Ata_Template.md`
- `docs_projeto/docs_Template_Projeto/_templates/Bug_Template.md`
- `docs_projeto/docs_Template_Projeto/_templates/Release_Template.md`

## Complemento — limpeza de e-mail nos frontmatters (2026-05-28)

O item 1 da decisao falava em "remover toda referencia a Sanesoluti", mas a passada original tocou apenas `Home.md`, `00_SGI_Aplicado/README.md`, `templates.json`, `graph.json` e os templates `_templates/`. Os 96 `README.md` estruturais das subpastas (`03_Hardware/README.md`, `01_Gestao/Roadmap/README.md`, etc) continuavam com:

```yaml
created_by: andrefmoreira@sanesoluti.com.br
updated_by: andrefmoreira@sanesoluti.com.br
```

Sao 192 ocorrencias em 96 arquivos — todas no frontmatter, nenhuma em corpo de texto.

**Acao:** esvaziar o valor (manter chave, remover e-mail). Resultado:

```yaml
created_by:
updated_by:
```

**Por que esvaziar e nao remover a chave:** preserva o contrato do schema documentado em `CONVENCOES.md` — se uma `.base` ou query filtra por `created_by`, a chave continua existindo. O preenchimento real fica a cargo de quem clonar/usar o template.

**Por que nao usar placeholder (`{{author_email}}`):** nao ha scaffolding ativo que faca substituicao automatica (alternativa "Scaffolding ativo" foi descartada nesta decisao). Placeholder ficaria literal no YAML e poderia quebrar parsers.

**Validacao:** `grep -ri sanesoluti docs_projeto/docs_Template_Projeto/` retorna zero ocorrencias.

## Validacao pendente

Esta sessao nao abriu o Obsidian — a validacao visual depende do usuario. Checklist sugerido:

- [ ] `Ctrl+P` → "Templates: Insert template" lista os 6 templates
- [ ] Inserir um template gera datas corretas em `created/updated/date`
- [ ] Wikilinks no `Home.md` resolvem (sem links vermelhos)
- [ ] `_views/*.base` renderiza nas 3 bases existentes
- [ ] Graph view colore notas por `type:` (cores diferentes para adr / requisito / plano-de-teste)

## Referencias

- [[../CONVENCOES]]
- [[../HOWTO]]
- [[../docs_Template_Projeto/Home]]
