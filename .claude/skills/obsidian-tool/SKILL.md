---
name: obsidian-tool
description: Scaffold uma nova ferramenta em Sanesoluti/04_Ferramentas/ — cria a nota .md a partir do Ferramenta_Template.md e, quando type=script|integracao, também cria o pacote uv correspondente em S.O.L-tools/<categoria>/<sub>/<slug>/ + registra no workspace. Use quando o usuário pedir para criar uma ferramenta, novo script, registrar uma integração ou scaffold de runbook.
created: 2026-05-07
created_by: andremoreira102030@gmail.com
updated: 2026-05-07
updated_by: andremoreira102030@gmail.com
---

# Obsidian Tool Scaffold — Sanesoluti

Cria uma nova entrada em `Sanesoluti/04_Ferramentas/<categoria>/[<sub>/]<type>-<slug>.md` a partir do template canônico e, para `type=script|integracao`, automatiza os 9 passos de scaffolding em [`S.O.L-tools/docs/ESTRUTURA.md`](https://github.com/AndreMoreira00/S.O.L-tools/blob/main/docs/ESTRUTURA.md).

## Quando invocar

- "Criar ferramenta" / "nova ferramenta" / "novo script" / "nova integração" / "novo runbook"
- "Registrar X no 04_Ferramentas"
- "Scaffold de ferramenta para \<slug\>"
- Qualquer menção a iniciar uma entrada sob `04_Ferramentas/` (doc + pacote `uv`)

## Fontes canônicas

- [`Sanesoluti/04_Ferramentas/PADRAO_INGESTAO.md`](../../../Sanesoluti/04_Ferramentas/PADRAO_INGESTAO.md) — frontmatter, types, categorias, regra "doc aqui / código no S.O.L-tools".
- [`Sanesoluti/04_Ferramentas/_templates/Ferramenta_Template.md`](../../../Sanesoluti/04_Ferramentas/_templates/Ferramenta_Template.md) — template da nota.
- `S.O.L-tools/_templates/ferramenta-template/` — template do pacote `uv` (no repo irmão).
- [`S.O.L-tools/docs/ESTRUTURA.md`](https://github.com/AndreMoreira00/S.O.L-tools/blob/main/docs/ESTRUTURA.md) — convenção monorepo.

## Workflow

### 1. Coletar inputs

Pergunte ao usuário (ou infira do contexto) e valide:

| Input | Valores aceitos | Exemplo |
|---|---|---|
| `<slug>` | kebab-case ASCII, regex `^[a-z][a-z0-9-]*$` | `ppk2-capture` |
| `<type>` | `ferramenta` \| `script` \| `integracao` \| `runbook` | `script` |
| `<categoria>` | `documentacao` \| `automacao` \| `comunicacao` \| `produtividade` \| `desenvolvimento` \| `engenharia` \| `laboratorio` \| `qualidade` \| `integracoes` | `automacao` |
| `<sub>` (opcional) | subpasta livre dentro da categoria (`manutencao`, `pipelines`, `ltspice`, ...) | `manutencao` |
| `--repo` (opcional) | `S.O.L-tools` (default), `LTSPICE-Simulations`, `Obsidian_Scope` | `S.O.L-tools` |

Se o usuário não informou um deles, **pergunte antes de prosseguir** — não invente.

### 2. Rodar o scaffolder

```bash
python .claude/scripts/new_tool.py <slug> <type> <categoria> [--sub <sub>] [--repo S.O.L-tools]
```

O script:

1. Cria `Sanesoluti/04_Ferramentas/<categoria>/[<sub>/]<type>-<slug>.md` a partir de `Ferramenta_Template.md`, com `title`, `ferramenta`, `type`, `categoria`, `repo`, `repo_path`, `repo_url` preenchidos.
2. Se `type` ∈ {`script`, `integracao`} e `--repo S.O.L-tools`:
   - Copia `S.O.L-tools/_templates/ferramenta-template/` → `S.O.L-tools/<categoria>/[<sub>/]<slug>/`.
   - Renomeia `src/ferramenta_template/` → `src/<pkg>/` (pkg = slug com `_`).
   - Edita `pyproject.toml` da ferramenta (`name`, `[project.scripts]`, `[tool.hatch.build.targets.wheel].packages`).
   - Edita o `README.md` da ferramenta substituindo `{{slug}}`/`{{categoria}}`/`{{pkg}}`.
   - Adiciona o caminho ao `[tool.uv.workspace].members` em `S.O.L-tools/pyproject.toml`.
3. Imprime resumo e os passos manuais restantes.

O script é idempotente — aborta se a nota ou a pasta destino já existirem.

### 3. Preencher a nota

Abra a nota recém-criada e preencha:

- `responsavel:` — pessoa/equipe dona
- Seção **Identidade** (versão, link oficial)
- Seção **Propósito** (o que resolve, em quais módulos é usada)
- Seção **Uso básico** (comandos, fluxos)
- Seção **Limitações** e **Alternativas conhecidas**

Para `type=ferramenta`/`runbook`, **remova** a seção "📦 Código fonte" da nota (ou deixe-a vazia se for um runbook que vai virar script).

### 4. Implementar o código (só `type=script|integracao`)

Abra o pacote `uv` recém-criado em S.O.L-tools e implemente:

- `src/<pkg>/cli.py` — entrypoint apontado por `[project.scripts]` no `pyproject.toml`.
- `tests/` — pelo menos um smoke test.
- `docs/ARCHITECTURE.md` — opcional, só se a ferramenta exigir.
- Atualize o `README.md` da ferramenta com o link da nota Obsidian.

Depois rode na raiz de S.O.L-tools:

```powershell
uv sync
uv run --package <slug> <slug> --help
```

### 5. Registrar no catálogo

Adicione uma linha em [`Sanesoluti/04_Ferramentas/README.md`](../../../Sanesoluti/04_Ferramentas/README.md) na seção da categoria correta:

```markdown
- [[<type>-<slug>|Nome legível]]
```

## Validações automáticas

- O hook [`update-frontmatter.py`](../../hooks/update-frontmatter.py) atualiza `created`/`updated`/`created_by`/`updated_by` no save da nota e emite advisory em stderr se `type=script|integracao` e `repo`/`repo_path` estão ausentes.
- A skill [`/validate-ingestion`](../obsidian-skills/skills/) audita conformidade do módulo (`/validate-ingestion 04_Ferramentas`).

## Erros comuns

- **Slug com underscore ou maiúscula**: o validador rejeita. Use kebab-case (`meu-script`, não `Meu_Script`).
- **Categoria errada**: cada uma tem subpastas próprias — confira a tabela em [`PADRAO_INGESTAO.md`](../../../Sanesoluti/04_Ferramentas/PADRAO_INGESTAO.md) e a árvore em [`README.md`](../../../Sanesoluti/04_Ferramentas/README.md).
- **`--sub` ausente quando deveria ter**: ex. `automacao` tem subpastas `manutencao/` e `pipelines/`. Sem `--sub`, a nota cai direto em `automacao/`. Veja a árvore antes.
- **S.O.L-tools não encontrado**: o script espera o repo irmão em `<parent>/S.O.L-tools/`. Se faltar, ele só cria a nota e avisa.
- **Workspace member duplicado**: o script é idempotente; se já estiver no `pyproject.toml` raiz, ele apenas pula.

## Ver também

- [`PADRAO_INGESTAO.md`](../../../Sanesoluti/04_Ferramentas/PADRAO_INGESTAO.md) — campos obrigatórios e regras de localização do código.
- [`PADRAO_INGESTAO.schema.json`](../../../Sanesoluti/04_Ferramentas/PADRAO_INGESTAO.schema.json) — schema de validação.
- [`obsidian-project`](../obsidian-project/SKILL.md) — skill análoga para projetos de produto.
- [`Sanesoluti/CLAUDE.md`](../../../Sanesoluti/CLAUDE.md) — regras globais da vault.
