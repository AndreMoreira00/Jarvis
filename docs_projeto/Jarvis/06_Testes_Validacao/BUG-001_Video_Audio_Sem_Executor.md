---
title: BUG-001 · Video_Audio chama Capture_Audio sem o argumento executor
id: BUG-001
type: bug
severidade: alta
prioridade: alta
status: aberto
componente: control.py · Control.Video_Audio
versao_afetada:
versao_corrigida:
reportado_por:
atribuido_a:
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 06_Testes_Validacao
tags: [bug, defeito, tema/ia, layer/teste, prio/alta, severidade/alta]
---

# BUG-001 · Video_Audio chama Capture_Audio sem o argumento executor

## Descricao

Em `control.py`, o metodo `Control.Video_Audio` submete a captura de audio assim:

```python
future_audio = executor.submit(self.Capture_Audio)  # falta passar executor
```

Mas a assinatura exige o argumento `executor`:

```python
def Capture_Audio(self, executor):
    ...
    executor.submit(microfone.adjust_for_ambient_noise, source, duration=2)
```

Como `Capture_Audio` e chamado **sem** `executor`, a chamada falha com `TypeError: Capture_Audio() missing 1 required positional argument: 'executor'`. O erro ocorre dentro da thread do `ThreadPoolExecutor`, ficando latente no `future_audio` ate `future_audio.result()` re-levantar a excecao em `Video_Audio`.

Efeito: o fluxo **video + pergunta** (gesto Rock / `Map_Rock`) nunca completa.

## Passos para reproduzir

1. Rodar `python main.py`.
2. Fazer o gesto **Rock** (`Map_Rock`) com a mao **Right**.
3. O `Video_Audio` e disparado e submete `self.Capture_Audio` sem `executor`.
4. Ao chamar `future_audio.result()`, o `TypeError` e re-levantado.

## Comportamento esperado vs atual

| | |
|---|---|
| **Esperado** | `Video_Audio` captura video + audio, monta o prompt e chama `Jarvis.Video_To_Text`, retornando resposta falada. |
| **Atual** | `TypeError` (argumento `executor` ausente) ao resolver o future do audio; o fluxo Rock nunca chega ao Gemini. |

## Impacto

- **Severidade: alta.** O requisito [[RF-005_Video_Mais_Pergunta_Analise|RF-005]] (video + pergunta) fica **inoperante** pelo caminho normal (gesto).
- Bloqueia a Parte C de [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002]] via gesto — so e possivel validar `Video_To_Text` de forma isolada.

## Sugestao de correcao

> Documental — nao alterar codigo nesta tarefa.

Passar `executor` na submissao, alinhando com os demais fluxos (`Audio_to_Audio`, `Image_Audio`):

```python
future_audio = executor.submit(self.Capture_Audio, executor)
```

Apos a correcao, executar a Parte C de [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002]] como teste de regressao.

## Confirmacao automatizada

Defeito **confirmado** pela suite unitaria (ver [[Relatorios/RT-001_Suite_Unitaria_Pytest|RT-001]]):
`tests/test_control.py` exercita `Capture_Audio` sem `executor` e captura o `TypeError`
com `@pytest.mark.xfail(strict=False)`. Quando o codigo for corrigido, o teste passara a
**xpass** — sinal para promover o caso a teste de regressao normal e fechar este bug.

## Referencias

- [[RF-005_Video_Mais_Pergunta_Analise|RF-005 · Video + pergunta (analise)]]
- [[CU-005_Analisar_Video_Com_Pergunta|CU-005 · Analisar video com pergunta]]
- [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002 · Validacao do fluxo de IA]]
- [[BUG-002_Recycle_Midia_Sem_Self|BUG-002 · Recycle_midia sem self]]
- [[Referencia_Modulos|Referencia de Modulos]]
