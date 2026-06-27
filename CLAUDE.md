# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Idioma: este repo e escrito em portugues (codigo, comentarios, docs e persona). Mantenha esse padrao.

## Visao geral

**Jarvis** e o software para um par de oculos inteligentes (alvo: Raspberry Pi 3) que
funciona por **controle por gestos**. O fluxo, por frame da camera, e:

camera (OpenCV) → deteccao de mao (MediaPipe) → reconhecimento de gesto → acao
de controle → IA (Google Gemini) e/ou upload (Google Photos) → resposta falada
(edge-tts + pygame).

Ha uma suite de **testes unitarios** (`tests/`, pytest) com **mock total** das libs
pesadas — roda sem mediapipe/opencv/pygame/gemini instalados. Lint/format/types via
**ruff + mypy** (config em `pyproject.toml`). A validacao funcional ainda e manual
(rodando o app); os testes cobrem logica/orquestracao.

## Comandos

```powershell
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Bootstrap: cria as pastas response/ e midia/ e um .env vazio (rode uma vez)
python scripts/bootstrap.py

# 3. Rodar o app — entry point canonico (pacote em src/jarvis)
python -m jarvis      # requer `pip install -e .` / `uv sync`; tecle 'q' p/ sair
python main.py        # shim de compatibilidade (roda sem instalar o pacote)

# 4. Rodar os testes (NAO precisa das libs de runtime — mock total)
pip install -r requirements-dev.txt
python -m pytest                       # suite completa + cobertura (~92%)
python -m pytest tests/test_hands.py --no-cov   # um arquivo, sem coverage
```

- `.env` precisa de `API_GEMINI=<sua_chave_gemini>` (lido em [services/jarvis.py](src/jarvis/services/jarvis.py)).
- Upload no Google Photos exige `env/client_secret.json` (OAuth desktop); o fluxo
  gera `env/token.json` no primeiro uso (ver [services/manager.py](src/jarvis/services/manager.py)).
- CI: [.github/workflows/codeql.yml](.github/workflows/codeql.yml) roda analise CodeQL e
  [.github/workflows/tests.yml](.github/workflows/tests.yml) roda a suite pytest com
  gate de cobertura (85%) em Python 3.11 e 3.12.

### Testes (`tests/`)

- **Mock total** ([tests/conftest.py](tests/conftest.py)): stuba `mediapipe`, `cv2`,
  `pygame`, `speech_recognition`, `google.generativeai`, `edge_tts` e `google-auth*` em
  `sys.modules` ANTES de importar o codigo de producao. Os testes rodam sem instalar as
  libs pesadas. `requests`/`python-dotenv` sao reais (mockados pontualmente por teste).
- Config de pytest/coverage em [pyproject.toml](pyproject.toml) (`asyncio_mode=auto`,
  `pythonpath=["src","scripts"]`, coverage escopado a `src/jarvis` + `scripts/`).
- Fixtures de gesto canonicas (`GESTURE_OK/POSITIVE/SPEAK/SQUID/ROCK/NONE`) verificadas
  por exclusividade; construtor `make_hand_landmarks()` cria os 21 landmarks do MediaPipe.
- Cobertura por modulo: gestures/hands/control/jarvis/manager/bootstrap em 100%;
  `core/loop.py` em ~45% (so o loop de I/O de `main()` fica fora, deliberadamente).
- A suite encontrou **bugs reais** no codigo (nao corrigidos — fora do escopo "testes"):
  ver [docs_projeto/decisoes/2026-06-27_testes_unitarios.md](docs_projeto/decisoes/2026-06-27_testes_unitarios.md).

## Arquitetura

O codigo e um **pacote em camadas** (`src/jarvis/`): **vision** (captura/gestos),
**core** (orquestracao + loop) e **services** (integracoes externas). O loop async vive
em [core/loop.py](src/jarvis/core/loop.py); as responsabilidades estao separadas por
classe, uma por arquivo, instanciadas em cadeia (`Control` cria `Jarvis` e `Manager`).
Entry: [`__main__.py`](src/jarvis/__main__.py) (`python -m jarvis`) ou o shim
[main.py](main.py) na raiz.

| Arquivo | Classe | Papel |
|---|---|---|
| [core/loop.py](src/jarvis/core/loop.py) | — | Loop `asyncio` da camera. Para cada mao detectada, percorre a lista `checks` e dispara a acao via `ThreadPoolExecutor`. |
| [vision/gestures.py](src/jarvis/vision/gestures.py) | — | Funcoes **puras** de classificacao (`is_ok`/`is_positive`/...) sobre os 21 landmarks normalizados. |
| [vision/hands.py](src/jarvis/vision/hands.py) | `Hands` | Wrapper do MediaPipe Hands. Cada `Map_*` delega para `gestures.*` e retorna `True`/`None` (contrato legado). |
| [core/control.py](src/jarvis/core/control.py) | `Control` | Orquestra as acoes: captura de foto/video/audio, toca sons de confirmacao (`audios_check/`) e encadeia os fluxos do Jarvis. |
| [services/jarvis.py](src/jarvis/services/jarvis.py) | `Jarvis` | Cliente do Gemini (`gemini-2.0-flash-lite`) com persona PT-BR. Converte a resposta em fala (`edge-tts`, voz `pt-BR-AntonioNeural`) e toca via pygame. |
| [services/manager.py](src/jarvis/services/manager.py) | `Manager` | Upload de midia para o Google Photos via OAuth2. |
| [scripts/bootstrap.py](scripts/bootstrap.py) | — | Script de bootstrap das pastas e `.env`. |

### Mapa gesto → acao (definido na lista `checks` em core/loop.py)

| Gesto (`Hands.Map_*`) | Mao exigida | Acao (`Control`) |
|---|---|---|
| OK (`Map_Ok`) | Direita | `Capture_Photo` — tira foto e sobe pro Photos |
| Positivo/joinha (`Map_Positive`) | Esquerda | `Capture_Video` — grava enquanto `Control_Video` estiver ligado |
| Dedo levantado (`Map_Speak`) | Direita | `Audio_to_Audio` — pergunta por voz → Gemini → resposta falada |
| "L" (`Map_Squid`) | Esquerda | `Image_Audio` — foto + pergunta por voz → Gemini |
| Rock (`Map_Rock`) | Direita | `Video_Audio` — video + pergunta por voz → Gemini |

### Controle de concorrencia (cuidado ao mexer)

- `Control.ACTION` (bool): trava global que impede disparar uma nova acao enquanto
  outra roda. Acoes setam `ACTION = True` no inicio e `False` no fim.
- `gesture_cooldown` (global em core/loop.py): debounce em frames, decrementado a cada
  frame, evita disparos repetidos do mesmo gesto.
- `Control._recording` (`threading.Event`): estado de gravacao thread-safe;
  `toggle_recording()`/`is_recording()` ligam/desligam (substituiu o antigo `Control_Video`).
- Acoes sincronas pesadas rodam em `ThreadPoolExecutor`; dentro delas, o codigo async e
  rodado via `Control._run(...)` (event loop reutilizavel por thread; substituiu `asyncio.run`).

## Armadilhas conhecidas

- **Entry point**: `python -m jarvis` (canonico) ou o shim `python main.py` na raiz.
  O `jarvis.py` agora e `src/jarvis/services/jarvis.py` (so define a classe `Jarvis`).
- **Paths relativos**: rode sempre a partir da raiz do repo. As pastas `response/` e
  `midia/` precisam existir (crie com `python scripts/bootstrap.py`); `env/` guarda os
  segredos OAuth.
- **`requirements.txt` tem entradas problematicas**: inclui pseudo-pacotes da stdlib
  (`time`, `os`, `pathlib`) e nomes genericos (`google`) que podem quebrar o
  `pip install`. Se falhar, instale o que faltar manualmente em vez de confiar no arquivo.

## Regras de comportamento (hook obrigatorio)

[.claude/settings.json](.claude/settings.json) registra um hook `UserPromptSubmit` que
roda [.claude/hooks/inject-rules.js](.claude/hooks/inject-rules.js) (Node, cross-platform)
e injeta 6 regras a **cada** prompt. Resumo:

1. **Skills primeiro** — revise `.claude/skills/` e invoque a skill que combinar com a tarefa antes de planejar/codar.
2. **Documentar** — toda alteracao de codigo ou referencia citada deve reverberar em `docs_projeto/` antes de encerrar.
3. **Minimo 5 perguntas** via `AskUserQuestion` (escopo, restricoes, estilo, criterios de aceite, edge cases) — exceto leitura factual pura.
4. **Advogado do diabo** — criticar a abordagem, apontar riscos e oferecer ≥2 caminhos alternativos com tradeoffs.
5. **Qualidade arquitetural** — atencao a complexidade, organizacao de pastas e separacao de responsabilidades; recusar funcoes monoliticas.
6. **Ingestao de referencias** — URLs/bibliotecas/conceitos citados viram resumo em `docs_projeto/referencias/<slug>.md`.

Inspecionar o que e injetado: `echo "{}" | node .claude/hooks/inject-rules.js`.
Detalhes em [docs_projeto/HOOKS.md](docs_projeto/HOOKS.md).

## Camada de documentacao (docs_projeto/)

O repo tem **duas identidades**: (1) o app Python acima e (2) um template de
documentacao Obsidian. `docs_projeto/` documenta o proprio repo (`HOWTO`,
`CONVENCOES`, `HOOKS`, `decisoes/`, `referencias/`) e carrega
`docs_Template_Projeto/` — um esqueleto de 14 modulos duplicado para projetos novos.

- Ao criar/editar notas, siga o schema de frontmatter, naming, tags e IDs de
  [docs_projeto/CONVENCOES.md](docs_projeto/CONVENCOES.md) (properties obrigatorias:
  `title`, `type`, `status`, `created`, `updated`, `project`, `tags`; datas em ISO 8601;
  IDs imutaveis como `ADR-0001`, `RF-001`).
- Para usar o template num projeto novo, ver [docs_projeto/HOWTO.md](docs_projeto/HOWTO.md).

## Config do Claude Code

- `.claude/settings.json` — versionado (hook publico).
- `.claude/settings.local.json` — ignorado pelo git (config pessoal).
- `.claude/skills/` — skills locais do projeto.
