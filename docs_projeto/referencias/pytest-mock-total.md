---
title: Mock total com pytest (stub de sys.modules)
source: https://docs.pytest.org/ + https://pytest-cov.readthedocs.io/ + https://docs.python.org/3/library/unittest.mock.html
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
tags: [referencia, testes, pytest, mock, cobertura, tema/qualidade]
---

# Mock total com pytest (stub de sys.modules)

Resumo do padrao e das ferramentas usadas para testar o Jarvis sem instalar as
libs pesadas de runtime. Aplicado em [[../decisoes/2026-06-27_testes_unitarios]].

## Conceito: "mock total" via `sys.modules`

Para testar codigo que importa libs pesadas/indisponiveis (mediapipe, opencv,
pygame, gemini...), injeta-se um **stub** em `sys.modules` ANTES do primeiro import
do modulo de producao. Quando o codigo faz `import cv2`, o Python encontra o stub
no cache de `sys.modules` e **nao** procura a lib real.

```python
import sys
from unittest.mock import MagicMock
sys.modules["cv2"] = MagicMock(name="cv2")   # antes de 'import control'
```

- **Onde colocar**: em `tests/conftest.py`, no nivel do modulo. O pytest importa o
  `conftest.py` da pasta de testes ANTES dos `test_*.py`, entao os stubs ja estao
  no `sys.modules` quando os testes importam o codigo de producao.
- **`MagicMock` como modulo**: qualquer atributo acessado (`cv2.imwrite`,
  `mp.solutions.hands.Hands`) vira um mock-filho automatico. Bom para imports que
  so precisam "nao explodir".
- **Pacotes com submodulo** (`from mediapipe.tasks import python`,
  `from google.oauth2.credentials import Credentials`): registrar TODOS os nomes
  pontilhados intermediarios em `sys.modules` (`mediapipe`, `mediapipe.tasks`, ...),
  senao o import do submodulo tenta usar o `__path__` do pacote (que o MagicMock nao
  tem) e falha.

### Armadilhas (vividas neste projeto)

- **`except sr.UnknownValueError`**: o alvo de um `except` precisa ser uma classe de
  excecao **real**. Um `MagicMock` quebra o `except`. Solucao: stub do
  `speech_recognition` com classes de excecao de verdade (`class UnknownValueError(Exception)`).
- **`asyncio.sleep(mock.get_length())`**: `get_length()` num MagicMock devolve outro
  mock, e `asyncio.sleep(mock)` da `TypeError`. Configure o retorno: `...get_length.return_value = 0.0`.
- **Mocks compartilhados vazam estado**: stubs em `sys.modules` sao globais entre
  arquivos de teste. Para asserts de "chamado 1x", faca `mock.reset_mock()` numa
  fixture antes de cada teste.
- **`str + MagicMock`**: `"" + recognize_google(...)` da `TypeError` se o retorno for
  mock; configure `recognize_google.return_value = "texto"`.

## Stack de teste

| Pacote | Papel |
|--------|-------|
| `pytest` | runner, fixtures, `parametrize` |
| `pytest-asyncio` | testa corrotinas; `asyncio_mode = "auto"` dispensa decorator em `async def test_*` |
| `pytest-cov` | cobertura (`--cov`, `--cov-report`, `--cov-fail-under=N`) |
| `unittest.mock` (stdlib) | `MagicMock`, `AsyncMock`, `patch`, `mock_open` |

### Config (em `pyproject.toml`)

```toml
[tool.pytest.ini_options]
pythonpath = ["."]          # raiz do repo importavel pelos testes
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-q --cov --cov-report=term-missing --cov-report=xml"

[tool.coverage.run]
source = ["."]              # ancora no repo (exclui site-packages)
omit = ["tests/*", ".claude/*", "docs_projeto/*", "*/site-packages/*"]
```

> **Por que `source=["."]` e nao `include=["main.py",...]`**: padroes de `include`
> com nome simples (`main.py`) casam por sufixo e pegam `_pytest/main.py`,
> `dotenv/main.py` em site-packages. `source=["."]` + `omit` ancora no projeto.

### Comandos uteis

```powershell
python -m pytest                                 # tudo + cobertura
python -m pytest tests/test_x.py --no-cov        # 1 arquivo (sem coverage, evita concorrencia)
python -m pytest -k "threshold" -v               # filtra por nome
python -m pytest --cov-fail-under=85             # falha se cobertura < 85%
```

## Fontes

- pytest — https://docs.pytest.org/
- pytest-cov — https://pytest-cov.readthedocs.io/
- pytest-asyncio — https://pytest-asyncio.readthedocs.io/
- unittest.mock — https://docs.python.org/3/library/unittest.mock.html
- coverage.py (config) — https://coverage.readthedocs.io/en/latest/config.html
