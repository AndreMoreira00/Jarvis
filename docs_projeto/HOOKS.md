# Hooks do projeto

Este repositorio versiona um hook `UserPromptSubmit` que injeta seis regras
obrigatorias em cada mensagem do usuario para o Claude Code.

## Arquivos

| Caminho | Papel |
|---|---|
| `.claude/settings.json` | Registra o hook, versionado no git |
| `.claude/hooks/inject-rules.js` | Script Node cross-platform que monta o lembrete |
| `.claude/settings.local.json` | Configuracoes pessoais, **ignoradas pelo git** |

## Regras injetadas

### 1. Consulta de skills (por prompt)
Antes de planejar ou agir, o Claude lista as skills em `.claude/skills/` e
invoca a que combinar com a tarefa via Skill tool. O proprio hook lista as
skills disponiveis no contexto injetado.

### 2. Atualizacao de documentacao
Ao final de qualquer alteracao de codigo, ou quando o usuario citar referencias,
o Claude deve atualizar `docs_projeto/` com o que mudou ou foi aprendido.

### 3. Minimo de 5 perguntas
Para qualquer pedido nao-trivial, o Claude chama `AskUserQuestion` com pelo
menos 5 perguntas cobrindo: escopo, restricoes tecnicas, preferencias,
criterios de aceite e edge cases. Excecao: leitura factual pura.

### 4. Advogado do diabo
Em todo prompt, o Claude critica a abordagem proposta, aponta riscos, invalida
premissas fracas e apresenta no minimo 2 caminhos alternativos com tradeoffs.

### 5. Qualidade arquitetural
Atencao continua a complexidade ciclomatica, organizacao de pastas, separacao
de responsabilidades, arquitetura limpa e abstracao em arquivos coesos.

### 6. Ingestao de referencias
Quando o usuario cita URL, biblioteca ou conceito que o Claude nao domina, ele
ingere via defuddle/WebFetch e salva um resumo em
`docs_projeto/referencias/<slug>.md` antes de prosseguir.

## Como testar localmente

```powershell
echo "{}" | node .claude/hooks/inject-rules.js
```

A saida e o bloco de regras que sera injetado em cada turno.

## Como desativar temporariamente

Edite `.claude/settings.json` e remova o bloco `UserPromptSubmit`, ou use
`/hooks` no Claude Code para gerenciar interativamente. Nao apague o script
`inject-rules.js` — ele pode ser util mais tarde.

## Como estender

Para adicionar uma nova regra, edite a string `rules` em
`.claude/hooks/inject-rules.js`. Mantenha o conteudo dentro do bloco
`<project-rules>...</project-rules>` para deixar claro de onde veio a injecao.
