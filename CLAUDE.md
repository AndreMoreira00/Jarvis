# CLAUDE.md

Instrucoes para o Claude Code neste repositorio.

## Hooks ativos

`.claude/settings.json` define um hook `UserPromptSubmit` que injeta as regras
do projeto a cada prompt do usuario. O script vive em
`.claude/hooks/inject-rules.js` (Node, cross-platform).

Para inspecionar o que e injetado:
```
echo "{}" | node .claude/hooks/inject-rules.js
```

## Regras de comportamento (resumo)

1. Consultar skills em `.claude/skills/` antes de qualquer tarefa
2. Atualizar `docs_projeto/` ao final de mudancas e quando absorver referencias novas
3. Minimo de 5 perguntas via AskUserQuestion (exceto leitura factual)
4. Atuar como advogado do diabo: criticar, invalidar, oferecer caminhos alternativos
5. Atencao a complexidade, organizacao de pastas e arquitetura limpa
6. Ingerir referencias citadas pelo usuario para `docs_projeto/referencias/`

Detalhes completos em `docs_projeto/HOOKS.md`.

## Estrutura

- `.claude/settings.json` — versionado, hooks publicos
- `.claude/settings.local.json` — ignorado pelo git, config pessoal
- `.claude/skills/` — skills locais do projeto
- `docs_projeto/` — documentacao do projeto (atualizar sempre)
