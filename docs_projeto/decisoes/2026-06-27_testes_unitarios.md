---
title: Implementacao de testes unitarios com mock total
type: decisao-repo
status: aprovado
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
tags: [decisao, testes, pytest, mock, cobertura, ci]
---

# Implementacao de testes unitarios com mock total

## Contexto

O repositorio Jarvis (app Python de oculos inteligentes por gestos, alvo Raspberry
Pi 3) **nao tinha nenhum teste** nem framework configurado. A validacao era 100%
manual (rodar `python main.py` e gesticular para a camera). Problemas que tornavam
testar dificil:

- **Dependencias pesadas de runtime**: `mediapipe`, `opencv-python`, `pygame`,
  `google-generativeai`, `edge-tts`, `speech_recognition`. Pesadas de instalar,
  algumas dependem de hardware (camera, microfone, dispositivo de audio) e de rede
  (Gemini, Google Photos). Instalar tudo no CI seria lento e flaky.
- **Efeitos colaterais no import**: `control.py` chamava `mixer.init()` no topo do
  modulo; `ProjectConfig.py` rodava `os.mkdir(...)` no import (estourava
  `FileExistsError` na segunda execucao); `jarvis.Jarvis.__init__` chamava
  `genai.configure(...)`.
- **`requirements.txt` problematico**: inclui pseudo-pacotes da stdlib (`time`,
  `os`, `pathlib`) e nomes genericos (`google`) que podem quebrar `pip install`.

## Decisao

Implementar uma suite de **testes unitarios com pytest** usando a estrategia de
**mock total**, decidida com o usuario via 5 perguntas (escopo, framework,
dependencias, criterio de aceite, refactor):

1. **Escopo**: todos os 6 modulos de producao, incluindo `main.py`.
2. **Framework**: `pytest` + `pytest-cov` + `pytest-asyncio` (codigo tem corrotinas).
3. **Dependencias**: **mock total** — as libs pesadas sao stubadas em `sys.modules`
   (via `MagicMock`) em `tests/conftest.py` ANTES de qualquer import do codigo de
   producao. Os testes rodam **sem** instalar mediapipe/opencv/pygame/gemini/etc.
   `requests` e `python-dotenv` (instalados, leves) ficam reais e sao mockados
   pontualmente por teste.
4. **Aceite/CI**: testes verdes + **gate de cobertura** em GitHub Actions
   (`.github/workflows/tests.yml`), Python 3.11 e 3.12, `--cov-fail-under=85`.
5. **Refactors minimos de testabilidade** (autorizados): ver secao abaixo.

### Edge cases priorizados (gestos / `hands.py`)

- Limiares de geometria (fronteiras dos `if` — logo dentro/no limite/logo fora).
- Nao-gesto (mao aberta / pose neutra nao dispara nada).
- Exclusividade (matriz 5x5: cada gesto so dispara o proprio `Map_*`).
- Robustez de coordenadas (rescala de `h/w`, landmarks em bordas `0.0`/`1.0`).

## Alternativas consideradas

- **(A) Testes de integracao reais** (libs instaladas, sem mock): mais fieis, mas
  exigiriam mediapipe/pygame/credenciais no CI -> lento, flaky e inviavel de rodar
  no Pi. **Descartado.**
- **(B) Cobrir so `hands.py`** (maior ROI, logica pura): descartado porque o usuario
  pediu cobertura total. `hands.py` foi priorizado *dentro* do escopo total.
- **(C) Refatorar tudo para injecao de dependencia** antes de testar: arquitetura
  ideal, mas reescrita grande e arriscada. **Descartado** em favor de refactors
  minimos so onde destravavam teste.
- **Mock por modulo** (parcial): descartado por inconsistencia; mock total e uniforme.

## Refactors aplicados (minimos, de testabilidade)

So dois, ambos seguros e que tambem corrigem defeitos reais:

1. **`ProjectConfig.py`**: `os.mkdir` -> `os.makedirs(..., exist_ok=True)` (idempotente,
   nao quebra na 2a execucao), `open('.env','a')` -> `open('.env','a').close()` (nao
   vaza handle) e `Config_Project()` agora sob `if __name__ == "__main__":` (importavel
   sem efeito colateral).
2. **`control.py`**: `mixer.init()` movido do topo do modulo para dentro de
   `Control.__init__` (remove efeito colateral no import; comportamento de runtime
   identico, pois `Control` e instanciado uma vez no startup).

Nenhuma outra logica de producao foi alterada.

## Bugs reais encontrados (NAO corrigidos — fora do escopo "testes")

A escrita dos testes revelou defeitos no codigo de producao. Foram **documentados e
fixados via `@pytest.mark.xfail`** (quando o teste tropeca neles), mas **nao
corrigidos** — corrigir comportamento foge do escopo aprovado (apenas testes +
refactor de testabilidade). Candidatos a issues/correcao futura:

| # | Local | Bug | Severidade |
|---|-------|-----|-----------|
| 1 | `control.py:108` `Video_Audio` | Chama `self.Capture_Audio` **sem** o arg obrigatorio `executor` -> `TypeError` em runtime real | alta (quebra o gesto Rock) |
| 2 | `control.py:30` `Recycle_midia` | Metodo declarado **sem `self`** -> `TypeError` se chamado pela instancia | media |
| 3 | `control.py:70` `Capture_Audio` | Toca `video_start_sound` ao iniciar captura de **audio** (provavel copy-paste; esperado `audio_start_sound`) | cosmetica |
| 4 | `control.py:65` `Capture_Audio` | `microfone.maxAlternatives = 1` nao tem efeito na API do `speech_recognition` | cosmetica |
| 5 | `manager.py:42-82` `uploadMidia` | Calcula `photo_url` mas **nunca retorna** (cai no fim -> `None`); a URL e descartada | media |
| 6 | `manager.py:74-77` `uploadMidia` | `batchCreate` sem `raise_for_status()`; em falha vira `KeyError` em vez de erro HTTP claro | media |
| 7 | `manager.py:39-40` `getPhotoUrl` | Acessa `response.json()['baseUrl']` sem checar status/chave -> `KeyError` em erro da API | baixa |
| 8 | `jarvis.py` `Translate` | `replace('  ',' ')` em passada unica nao colapsa 3+ espacos (`'a   b'` -> `'a  b'`) | baixa |
| 9 | `jarvis.py` `Video_To_Text` | `time.sleep(10)` bloqueante dentro de corrotina `async` trava o event loop (o proprio comentario chama de "Bomba") | media (concorrencia) |
| 10 | `main.py:90-94` `Check_Gesture` | `gesture_cooldown` e armado **antes** da checagem de `state`; e `Control_Video` e alternado para **todo** gesto Async, nao so o de video | media (efeito colateral) |

Tambem ha **codigo morto** em `hands.py` (varias coordenadas calculadas e nunca usadas;
`palma_0/palma_y` em `Map_Speak`) e contrato de retorno inconsistente nos `Map_*`
(retornam `None` implicito em vez de `False` no caminho negativo — funcional, pois o
caller trata como falso; os testes fixam `is None`).

## Consequencias

### Positivas
- **183 itens de teste** (181 passed + 2 xfailed) rodando em ~1s, sem libs pesadas.
- Cobertura: hands/control/jarvis/manager/ProjectConfig em **100%**; total **~92%**.
- CI roda a suite sem instalar o `requirements.txt` quebrado (so `requirements-dev.txt`).
- Refactors deixaram `ProjectConfig` e `control` mais limpos (sem efeito no import).
- 10 bugs reais + codigo morto mapeados para correcao futura.

### Negativas / riscos
- **Mock total e fragil por natureza**: se a API real de uma lib mudar, o stub nao
  acusa — os testes validam o *nosso* codigo, nao a integracao real com as libs.
  Mitigacao: testes focam em orquestracao/geometria/fluxo, nao na lib stubada.
- **`main.py` ~44%**: o loop da camera (`main()`, linhas 14-75) ficou fora de proposito
  (I/O puro, baixo ROI). Decisao honesta — nao foi mascarado com cobertura falsa.
- **Gate de 85% da falsa seguranca** se interpretado como prova de correcao: e protecao
  contra regressao, nao prova de que o comportamento esta certo (vide os 10 bugs que
  passam nos testes porque os testes fixam o comportamento ATUAL).

## Arquivos criados/alterados

Criados:
- `tests/conftest.py` — stubs de `sys.modules` (mock total) + `make_hand_landmarks` +
  fixtures e constantes de gesto canonicas (verificadas por exclusividade).
- `tests/test_smoke.py`, `tests/test_hands.py`, `tests/test_control.py`,
  `tests/test_jarvis.py`, `tests/test_manager.py`, `tests/test_main.py`,
  `tests/test_project_config.py`.
- `pyproject.toml` — config pytest + coverage.
- `requirements-dev.txt` — pytest/pytest-asyncio/pytest-cov.
- `.github/workflows/tests.yml` — CI da suite com gate de cobertura.
- `docs_projeto/referencias/pytest-mock-total.md` — referencia do padrao/stack.

Alterados:
- `ProjectConfig.py`, `control.py` (refactors de testabilidade — acima).
- `CLAUDE.md` (visao geral, comandos, secao de testes).
- `.gitignore` (artefatos de pytest/coverage).

## Como rodar

```powershell
pip install -r requirements-dev.txt
python -m pytest                                 # suite + cobertura
python -m pytest tests/test_hands.py --no-cov    # 1 arquivo, rapido
python -m pytest --cov-fail-under=85             # como o CI (falha < 85%)
```

## Referencias

- [[../referencias/pytest-mock-total]]
- [[../CONVENCOES]]
- Codigo: [tests/conftest.py](../../tests/conftest.py), [pyproject.toml](../../pyproject.toml)
