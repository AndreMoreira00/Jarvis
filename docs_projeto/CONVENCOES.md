---
title: Convencoes da Documentacao
type: convencao
status: aprovado
created: 2026-05-28
updated: 2026-05-28
tags: [convencao, schema, properties, naming, tags]
---

# Convencoes da Documentacao

Schema unico para frontmatter, nomes de arquivo e tags. Tudo que estiver em `docs_projeto/docs_Template_Projeto/` (e em projetos derivados) deve seguir o que esta aqui.

Se voce vai inventar uma property nova, **primeiro adicione nesta pagina** — bases (`.base`) e graph dependem do schema estavel.

## 1. Properties (frontmatter)

### 1.1 Obrigatorias em toda nota

| Property | Tipo | Exemplo | Observacao |
|----------|------|---------|------------|
| `title` | string | `RF-001 · Login com biometria` | Sem `#` no inicio, sem aspas |
| `type` | enum | `requisito` | Ver tabela 1.3 |
| `status` | enum | `rascunho` | Ver tabela 1.4 |
| `created` | date | `2026-05-28` | ISO 8601, imutavel |
| `updated` | date | `2026-05-28` | Atualizar a cada edicao |
| `project` | string | `Produto_X` | Nome do projeto (slug com `_`) |
| `tags` | list | `[requisito, funcional]` | Ver secao 3 |

### 1.2 Recomendadas (quando aplicavel)

| Property | Tipo | Aplica a |
|----------|------|----------|
| `id` | string | Notas com identificador externo (ADR-XXXX, RF-XXX, BUG-XXX) |
| `module` | enum | Modulo dono (`01_Gestao`, `02_Especificacoes`, ...) |
| `layer` | enum | `gestao` \| `especificacao` \| `hardware` \| `firmware` \| `software` \| `teste` \| `producao` \| `comercial` |
| `date` | date | Data factual do evento (data da reuniao, da decisao, do teste) — diferente de `created` |
| `prioridade` | enum | `baixa` \| `media` \| `alta` \| `critica` |
| `severidade` | enum | Bugs: `cosmetica` \| `media` \| `alta` \| `bloqueante` |
| `versao` | string | Releases: `vX.Y.Z` |
| `componente` | string | Subsistema afetado |
| `clause` | string | Clausula de norma (`ISO 9001:9.1.3`) — usado pela base `Documentos_por_Clausula` |
| `standard` | enum | `ISO 9001` \| `ISO 17025` \| `ISO 14971` \| outras |
| `deciders` | list | ADRs: pessoas que decidiram |
| `participantes` | list | Atas: presentes |
| `verificado_por` | list | Requisitos: testes que verificam |
| `requisitos_cobertos` | list | Testes: requisitos cobertos |

### 1.3 Valores de `type`

| Valor | Significado |
|-------|-------------|
| `home` | Dashboard / Home |
| `readme` | README de pasta |
| `adr` | Architecture Decision Record |
| `requisito` | Requisito (funcional ou nao-funcional) |
| `caso-de-uso` | Caso de uso / user story |
| `plano-de-teste` | Plano de teste |
| `relatorio-teste` | Relatorio de execucao de teste |
| `ata` | Ata de reuniao |
| `bug` | Defeito |
| `release` | Release notes |
| `objetivo` | Objetivo do projeto |
| `risco` | Risco |
| `nc` | Nao conformidade |
| `gate` | Aprovacao de gate |
| `procedimento` | Procedimento aplicavel |
| `convencao` | Pagina de convencao/schema |
| `referencia` | Referencia externa (norma, paper, datasheet) |

### 1.4 Valores de `status`

```
rascunho → em_revisao → aprovado → obsoleto
```

| Status | Quando usar |
|--------|-------------|
| `rascunho` | Em construcao, nao revisado |
| `em_revisao` | Pronto para revisao por par/lider |
| `aprovado` | Revisado e em vigor |
| `obsoleto` | Substituido — manter para historico, mover para `99_Arquivo_Historico/` se grande |
| `registrado` | Para atas e logs (nao tem aprovacao) |
| `aberto` / `fechado` | Bugs e NCs |
| `proposto` / `aceito` / `rejeitado` / `superseded` | ADRs |

## 2. Nomes de arquivo

- **Pastas**: `NN_Nome_Da_Pasta` (prefixo numerico, underscore como separador).
- **Notas comuns**: `Titulo_Em_PascalCase_Underscore.md` ou `Snake_Case.md`. Evitar espacos.
- **Notas com ID**: prefixar com ID quando facilita busca: `RF-001_Login_Biometria.md`, `ADR-0007_Escolha_MCU.md`.
- **Bases**: `Pergunta_Que_Responde.base` (em `_views/`).
- **Templates**: `Nome_Template.md` em `_templates/`.

Evitar acentos e caracteres especiais em nomes de arquivo (Windows-safe).

## 3. Tags

Tags com `/` formam hierarquia no Obsidian. Usar **plurais coerentes** e nivel raso (max 3 niveis).

### Raiz da taxonomia

| Raiz | Uso |
|------|-----|
| `tipo/<valor>` | Espelha `type:` — opcional, util quando a property nao esta exposta |
| `module/<valor>` | Espelha `module:` — `module/firmware`, `module/hardware` |
| `layer/<valor>` | `layer/gestao`, `layer/teste` |
| `prio/<valor>` | `prio/alta` |
| `status/<valor>` | `status/rascunho` (opcional) |
| `produto/<nome>` | Quando o template gera varias notas para varios produtos |
| `tema/<assunto>` | Tema livre: `tema/seguranca`, `tema/comunicacao` |

Tags **proibidas** (nao informativas): `#documento`, `#nota`, `#trabalho`. O fato de algo ser uma nota nao precisa ser anotado.

## 4. Wikilinks

- Sempre `[[caminho/Nome|Texto de exibicao]]` quando o nome do arquivo nao serve como label legivel.
- Usar caminho relativo quando estiver dentro de `docs_Template_Projeto/`.
- Evitar links absolutos para fora do repo — se precisar, registre em [[referencias/README|referencias/]].

## 5. IDs

| Prefixo | Tipo | Formato |
|---------|------|---------|
| `ADR-` | Decisao | `ADR-0001` (zero-padded 4 digitos) |
| `RF-` | Requisito funcional | `RF-001` (3 digitos) |
| `RNF-` | Requisito nao-funcional | `RNF-001` |
| `CU-` | Caso de uso | `CU-001` (3 digitos) |
| `TP-` | Plano de teste | `TP-001` |
| `RT-` | Relatorio de teste | `RT-001` |
| `BUG-` | Bug | `BUG-001` |
| `ATA-` | Ata | `ATA-YYYYMMDD` |
| `REL-` | Release | `REL-vMAJOR.MINOR.PATCH` |
| `NC-` | Nao conformidade | `NC-YYYY-NNN` |
| `RISCO-` | Risco | `RISCO-001` |
| `OBJ-` | Objetivo | `OBJ-001` |

IDs sao **imutaveis**. Se uma nota for descontinuada, manter o ID e marcar `status: obsoleto`.

## 6. Datas

- Sempre ISO 8601 (`YYYY-MM-DD`).
- `created` nunca muda apos criacao.
- `updated` atualiza a cada edicao significativa (nao a cada salvar).
- `date` (quando existe) e a data do evento factual (reuniao, teste, decisao).

## 7. Como evoluir este schema

1. Editar este arquivo com a mudanca.
2. Documentar em [[#9-changelog|changelog]] abaixo (data + o que mudou + motivo).
3. Atualizar templates afetados em [[docs_Template_Projeto/_templates/README]].
4. Atualizar bases afetadas em [[_views/]].

## 8. Referencias

- [[HOWTO|HOWTO.md]] — como clonar e usar este template
- [[docs_Template_Projeto/Home|Home do template]]
- [[docs_Template_Projeto/_templates/README|Templates disponiveis]]

## 9. Changelog

| Data | Mudanca | Motivo |
|------|---------|--------|
| 2026-05-28 | Versao inicial do schema | Configuracao inicial do template Obsidian |
| 2026-06-27 | Adicionado prefixo de ID `CU-` (caso de uso) | Documentacao do app Jarvis usa casos de uso com identificador rastreavel |
