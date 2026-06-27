---
title: RT-001 · Execucao da suite unitaria (pytest, mock total)
id: RT-001
type: relatorio-teste
status: aprovado
requisitos_cobertos: [RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-008]
planos_executados: [TP-001, TP-002, TP-003]
executante: pytest (automatizado)
data_execucao: 2026-06-27
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 06_Testes_Validacao
prioridade: alta
tags: [teste, relatorio, automatizado, pytest, tema/qualidade, layer/teste, prio/alta]
---

# RT-001 · Execucao da suite unitaria (pytest, mock total)

## Resumo executivo

Foi implementada uma **suite de testes unitarios automatizada** (`tests/`, pytest)
cobrindo os 6 modulos de producao. A suite usa **mock total** (stubs em
`sys.modules`), entao roda **sem** as libs pesadas de runtime
(mediapipe/opencv/pygame/gemini/edge-tts/speech_recognition) instaladas.

| Metrica | Valor |
|---|---|
| Itens de teste | **181 passed + 2 xfailed** |
| Tempo | ~1 s |
| Cobertura total | **92%** (`--cov-fail-under=85` no CI) |
| Ambiente | Python 3.11/3.12, sem libs de runtime |
| Comando | `python -m pytest` |

> **Escopo e limite:** esta camada automatizada **nao substitui** os planos manuais
> [[TP-001_Validacao_Reconhecimento_Gestos|TP-001]] / [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002]] /
> [[TP-003_Validacao_Captura_E_Upload|TP-003]]. Ela valida a **logica/orquestracao**
> do nosso codigo (geometria dos gestos, fluxo das acoes, tratamento de erro), com
> hardware (camera/microfone/audio) e rede (Gemini/Photos) **mockados**. A validacao
> ponta a ponta com hardware real continua sendo feita pelos TPs manuais.

## Cobertura por modulo

| Modulo | Cobertura | Observacao |
|---|---|---|
| `hands.py` | **100%** | Geometria dos 5 gestos — nucleo testado a fundo |
| `control.py` | **100%** | Orquestracao das acoes (mock de jarvis/manager/cv2/sr) |
| `jarvis.py` | **100%** | Cliente Gemini + TTS (mock de genai/edge_tts) |
| `manager.py` | **100%** | Upload Google Photos (mock de requests/oauth) |
| `ProjectConfig.py` | **100%** | Bootstrap idempotente (ver [[BUG-003_ProjectConfig_Mkdir_Sem_ExistOk|BUG-003]]) |
| `main.py` | **44%** | So o loop de I/O de `main()` (cap/imshow/waitKey) fica fora — deliberado |
| **TOTAL** | **92%** | — |

## O que foi testado

### Reconhecimento de gestos (`hands.py`) — relacionado a [[TP-001_Validacao_Reconhecimento_Gestos|TP-001]], RF-006/RF-008
- Cada gesto canonico dispara **exatamente** o seu `Map_*` (95 testes).
- **Exclusividade**: matriz 5x5 — nenhum gesto dispara outro `Map_*`.
- **Nao-gesto**: mao aberta / pose neutra nao dispara nada.
- **Thresholds de fronteira**: cada limite (`0.05*w`, `0.05*h`) testado logo dentro / no limite / logo fora.
- **Robustez**: rescala de resolucao (480x640 / 720x1280 / 1080x1920) e landmarks em borda (0.0/1.0).

### Fluxo de IA (`jarvis.py`) — relacionado a [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002]], RF-003/004/005
- `Text_To_Text` / `Image_To_Text` / `Video_To_Text`: chamada ao Gemini, TTS e reproducao.
- `Video_To_Text`: ramos PROCESSING->ACTIVE e FAILED->`ValueError`; `Delete_Cahche_Files`.
- `Translate`: normalizacao de caracteres especiais.

### Captura e upload (`control.py`, `manager.py`) — relacionado a [[TP-003_Validacao_Captura_E_Upload|TP-003]], RF-001/002
- `Capture_Photo` / `Capture_Video` / `Capture_Audio` (incl. tratamento de `UnknownValueError`/`RequestError`).
- Trava `ACTION` e nomes de arquivo (`midia/<timestamp>.jpg|avi`).
- `Manager`: `authorize_credentials` (3 caminhos OAuth), `getPhotoUrl`, `uploadMidia` (sucesso + erro HTTP).

### Loop e controle (`main.py`) — relacionado a RF-008
- `Check_Gesture`: match de mao/`side`, set de `gesture_cooldown`, toggle de `Control_Video`, disparo de `func_exe`.
- `init_hands` / `init_control`.

## Defeitos confirmados pela suite

A suite **confirmou automaticamente** 3 bugs ja catalogados (encapsulados em
`@pytest.mark.xfail` quando o teste tropeca no defeito, fixando o comportamento atual):

| Bug | Confirmado por | Status |
|---|---|---|
| [[BUG-001_Video_Audio_Sem_Executor\|BUG-001]] · `Video_Audio` sem `executor` | `tests/test_control.py::...::test_bug_capture_audio_sem_executor` (xfail) | aberto |
| [[BUG-002_Recycle_Midia_Sem_Self\|BUG-002]] · `Recycle_midia` sem `self` | `tests/test_control.py::...::test_bug_recycle_midia_sem_self` (xfail) | aberto |
| [[BUG-003_ProjectConfig_Mkdir_Sem_ExistOk\|BUG-003]] · `os.mkdir` sem `exist_ok` | `tests/test_project_config.py` (idempotencia) | **fechado** (corrigido) |

Defeitos adicionais observados durante a escrita dos testes (ainda nao catalogados como
BUG; candidatos a abrir): `manager.uploadMidia` nao retorna a `photo_url`; `batchCreate`
sem `raise_for_status`; `jarvis.Translate` nao colapsa 3+ espacos; `time.sleep(10)`
bloqueante em corrotina async (`Video_To_Text`); `Capture_Audio` toca `video_start_sound`.
Lista completa em [[../../../decisoes/2026-06-27_testes_unitarios|Decisao: testes unitarios]].

## Desvios / o que ficou fora (sem mascarar)

- **`main()` (loop da camera)**: I/O puro (`cv2.VideoCapture/imshow/waitKey`), nao
  testado unitariamente — exige hardware/mock fragil de baixo ROI. Coberto pelos TPs manuais.
- **Integracao real** (Gemini, Google Photos, MediaPipe, audio): mockada. Fidelidade da
  API real NAO e garantida por esta suite — e papel dos TPs manuais.

## Como reproduzir

```powershell
pip install -r requirements-dev.txt
python -m pytest                       # 181 passed, 2 xfailed, cobertura ~92%
python -m pytest --cov-fail-under=85   # como no CI (.github/workflows/tests.yml)
```

## Referencias

- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Reconhecimento de gestos]]
- [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002 · Fluxo de IA]]
- [[TP-003_Validacao_Captura_E_Upload|TP-003 · Captura e upload]]
- [[../../../decisoes/2026-06-27_testes_unitarios|Decisao (repo): testes unitarios com mock total]]
- [[../../../referencias/pytest-mock-total|Referencia: mock total com pytest]]
- Codigo: `tests/conftest.py`, `pyproject.toml`, `.github/workflows/tests.yml`
