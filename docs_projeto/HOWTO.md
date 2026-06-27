---
title: HOWTO · Usar este template
type: convencao
status: aprovado
created: 2026-05-28
updated: 2026-05-28
tags: [howto, template, obsidian]
---

# HOWTO · Usar este template

Como clonar este repositorio e iniciar um projeto novo com a estrutura de documentacao Obsidian.

## 1. Clonar e abrir no Obsidian

```bash
git clone <url-do-repo> meu-novo-projeto
cd meu-novo-projeto
```

No Obsidian: **Open another vault** → **Open folder as vault** → selecione `meu-novo-projeto/` (a **raiz do repo**, nao `docs_projeto/`). Isso garante que `.obsidian/` e ambos `docs_projeto/` e `_views/` (via `docs_projeto/_views/`) sejam carregados.

## 2. Duplicar a pasta-template

```
docs_projeto/
├── docs_Template_Projeto/   ← este e o template
└── _views/                   ← bases globais (cross-projetos)
```

1. Duplique `docs_Template_Projeto/` no mesmo nivel.
2. Renomeie para o slug do projeto (ex: `Produto_X`, `BalancaIndustrial_2`). Use `_` como separador.
3. Resultado:

```
docs_projeto/
├── docs_Template_Projeto/   ← deixa intacto para referencia futura
├── Produto_X/                ← seu projeto novo
└── _views/
```

## 3. Ajustar frontmatter

Em **todas** as notas dentro de `Produto_X/`, trocar:

```yaml
project: _Template_Projeto
```

por:

```yaml
project: Produto_X
```

Find & Replace global no Obsidian (`Ctrl+Shift+F`) facilita.

## 4. Decidir quais modulos manter

A estrutura tem 14 modulos. Se seu projeto e **software puro**, voce pode deletar `03_Hardware/`, `04_Firmware/`, `07_Certificacoes_Homologacoes/`, `08_Producao/`. Se e **hardware sem firmware**, deletar `04_Firmware/`.

Regra: prefira **deletar** modulos nao-aplicaveis a manter pastas vazias — pastas mortas poluem busca e graph.

## 5. Preencher o esqueleto inicial

Ordem sugerida:

1. `Home.md` — atualizar titulo, descricao curta do projeto, datas
2. `00_SGI_Aplicado/Procedimentos_Aplicaveis` — listar normas adotadas
3. `01_Gestao/Roadmap/` — primeira nota com roadmap macro
4. `01_Gestao/Cronograma/` — cronograma de alto nivel
5. `02_Especificacoes/Requisitos_Funcionais/` — primeira batelada de RFs (usar template `Ctrl+P` → "Insert template" → `Requisito_Template`)
6. `01_Gestao/Decisoes_Tecnicas/` — primeira ADR explicando escolhas iniciais

## 6. Inserir templates rapidamente

Configurado em `.obsidian/templates.json`. Atalho:

- `Ctrl+P` → "Templates: Insert template" → escolher
- Ou rebind para uma hotkey (em `Settings → Hotkeys → Templates: Insert template`)

Templates disponiveis estao em [[docs_Template_Projeto/_templates/README]].

## 7. Schema (properties + tags + IDs)

Antes de criar notas, leia [[CONVENCOES]]. Resumo:

- `created` / `updated` em **toda** nota (ISO 8601).
- `type:` controlado — ver tabela 1.3 em CONVENCOES.
- `status:` segue o fluxo `rascunho → em_revisao → aprovado → obsoleto`.
- Tags em hierarquia rasa: `module/firmware`, `layer/teste`, `prio/alta`.
- IDs imutaveis: `ADR-0001`, `RF-001`, `BUG-001`, etc.

## 8. Views (bases)

`docs_projeto/_views/` tem bases que cruzam dados de todas as notas:

- `Documentos_por_Clausula.base` — agrupado por `clause` (norma)
- `Rascunhos_Pendentes.base` — `status == rascunho`, com formula de "dias parado"
- `Documentos_Obsoletos.base` — `status == obsoleto`

Para adicionar uma base nova, criar `.base` em `_views/` e linkar no Home.

## 9. Atualizar docs_projeto/ ao alterar codigo

Convencao deste repo (CLAUDE.md): toda mudanca em codigo ou estrutura tem que reverberar em `docs_projeto/`. Em projetos derivados, manter a mesma regra ou suspender explicitamente.

## 10. O que NAO copiar do template

- Datas `created/updated` dos templates: deixar `{{date:YYYY-MM-DD}}` — o plugin Templates do Obsidian substitui na hora de inserir.
- Conteudo de exemplo das tabelas de READMEs: substituir pelos dados reais.
- Este HOWTO em si — voce pode deletar do projeto derivado quando ele nao for mais util.

## 11. Bootstrap de um projeto-exemplo

Comando manual (PowerShell):

```powershell
Copy-Item -Recurse docs_projeto/docs_Template_Projeto docs_projeto/Produto_X
```

Bash/POSIX:

```bash
cp -r docs_projeto/docs_Template_Projeto docs_projeto/Produto_X
```

Depois, abra no Obsidian e faca o Find & Replace de `project: _Template_Projeto`.

## 12. Troubleshooting

| Sintoma | Causa provavel | Acao |
|---------|----------------|------|
| Templates nao aparecem no `Ctrl+P` | Path errado em `.obsidian/templates.json` | Confirmar que aponta para `docs_projeto/docs_Template_Projeto/_templates` |
| Bases nao renderizam | Core plugin `bases` desligado | `Settings → Core plugins → Bases` |
| Wikilinks aparecem como nao-resolvidos | Vault aberto na pasta errada | Abrir o vault na **raiz do repo**, nao em `docs_projeto/` |
| Graph mostra so um arquivo | Filtro do graph esta restritivo | `.obsidian/graph.json` → revisar `colorGroups` e `search` |
