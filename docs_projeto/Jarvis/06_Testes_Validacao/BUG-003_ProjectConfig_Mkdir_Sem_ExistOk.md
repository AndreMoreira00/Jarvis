---
title: BUG-003 · ProjectConfig usava os.mkdir sem exist_ok e rodava no import
id: BUG-003
type: bug
severidade: media
prioridade: media
status: fechado
componente: ProjectConfig.py · Config_Project
versao_afetada:
versao_corrigida:
reportado_por:
atribuido_a:
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 06_Testes_Validacao
tags: [bug, defeito, tema/bootstrap, layer/teste, prio/media, severidade/media]
---

# BUG-003 · ProjectConfig usava os.mkdir sem exist_ok e rodava no import

> **Status: fechado.** Verificado contra `ProjectConfig.py` na revisao atual: o defeito **ja foi corrigido** no codigo. Esta nota documenta o problema historico e a correcao aplicada, para rastreabilidade.

## Descricao (defeito historico)

A versao anterior de `ProjectConfig.py` criava as pastas com `os.mkdir('response')` / `os.mkdir('midia')` **sem `exist_ok`**, e chamava `Config_Project()` **no nivel do modulo** (executado ja no `import`, sem guard `__main__`). Consequencias:

1. **`FileExistsError` na segunda execucao** — `os.mkdir` levanta erro se a pasta ja existe. O bootstrap so rodava limpo **uma vez**; rodar `python ProjectConfig.py` de novo quebrava.
2. **Efeito colateral no import** — importar o modulo (ex.: em um teste) ja criava pastas/arquivo e podia estourar o erro.
3. **Handle de `.env` vazado** — `open('.env', 'a')` sem `.close()`.

## Passos para reproduzir (no codigo antigo)

1. Rodar `python ProjectConfig.py` uma vez (cria `response/` e `midia/`).
2. Rodar `python ProjectConfig.py` de novo.
3. `FileExistsError: [WinError 183] ... 'response'`.

## Comportamento esperado vs atual

| | |
|---|---|
| **Esperado** | Bootstrap **idempotente**: rodar varias vezes sem erro; importar o modulo sem efeitos colaterais. |
| **Atual (corrigido)** | `os.makedirs(..., exist_ok=True)`, `.env` aberto e fechado, e `Config_Project()` so roda sob `if __name__ == "__main__":`. |

Codigo atual (corrigido):

```python
def Config_Project():
  os.makedirs('response', exist_ok=True)
  os.makedirs('midia', exist_ok=True)
  open('.env', 'a').close()

if __name__ == "__main__":
  Config_Project()
```

## Impacto

- **Severidade: media.** No estado antigo, atrapalhava o setup repetido e o uso do modulo em testes. **Resolvido** — sem impacto na revisao atual.

## Sugestao de correcao

> Ja aplicada no codigo. Acoes de verificacao recomendadas:

- Teste de regressao: rodar `python ProjectConfig.py` **duas vezes** seguidas; nas duas deve terminar sem erro e manter `response/`, `midia/` e `.env`.
- Confirmar que `import ProjectConfig` nao cria pastas/arquivo (sem efeito colateral).

## Referencias

- [[Guia_Rapido_Execucao|Guia Rapido de Execucao]]
- [[Instalacao_Dependencias|Instalacao de Dependencias]]
- [[BUG-001_Video_Audio_Sem_Executor|BUG-001 · Video_Audio sem executor]]
- [[BUG-002_Recycle_Midia_Sem_Self|BUG-002 · Recycle_midia sem self]]
