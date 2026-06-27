---
title: BUG-002 · Recycle_midia definido sem self
id: BUG-002
type: bug
severidade: media
prioridade: media
status: aberto
componente: control.py · Control.Recycle_midia
versao_afetada:
versao_corrigida:
reportado_por:
atribuido_a:
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 06_Testes_Validacao
tags: [bug, defeito, tema/midia, layer/teste, prio/media, severidade/media]
---

# BUG-002 · Recycle_midia definido sem self

## Descricao

Em `control.py`, o metodo de instancia `Recycle_midia` foi declarado **sem o parametro `self`**:

```python
def Recycle_midia(midia_path):
    os.remove(midia_path)
```

Por estar dentro da classe `Control`, ao ser chamado como `self.Recycle_midia(caminho)` o Python passa a instancia como primeiro argumento posicional. Esse argumento cai em `midia_path`, e qualquer argumento adicional gera `TypeError: Recycle_midia() takes 1 positional argument but 2 were given`. Mesmo no melhor caso, `midia_path` recebe o objeto `Control` em vez do caminho do arquivo, fazendo `os.remove` falhar.

Observacao: hoje `Recycle_midia` **nao e chamado** em nenhum lugar do fluxo, entao o defeito esta latente — mas qualquer uso futuro como metodo de instancia quebra.

## Passos para reproduzir

1. A partir de uma instancia: `c = Control()`.
2. Chamar `c.Recycle_midia("midia/foo.jpg")`.
3. Observar `TypeError` (dois argumentos posicionais para um parametro), ou — se chamado com 1 argumento — `self` vai parar em `midia_path` e `os.remove` recebe um objeto invalido.

## Comportamento esperado vs atual

| | |
|---|---|
| **Esperado** | `Recycle_midia` aceita `self` + `midia_path` e remove o arquivo em `midia_path`. |
| **Atual** | Assinatura sem `self`; chamada como metodo de instancia gera `TypeError` / passa o objeto errado para `os.remove`. |

## Impacto

- **Severidade: media.** Defeito latente (metodo nao usado hoje), mas impede a limpeza de midia local se/quando for acionado. Risco de acumulo de arquivos em `midia/` no alvo Raspberry Pi 3 (armazenamento limitado).

## Sugestao de correcao

> Documental — nao alterar codigo nesta tarefa.

Incluir `self` na assinatura:

```python
def Recycle_midia(self, midia_path):
    os.remove(midia_path)
```

Alternativa: se a intencao for um utilitario sem estado, declarar como `@staticmethod`. Avaliar tambem proteger contra arquivo inexistente (`os.remove` levanta `FileNotFoundError`).

## Confirmacao automatizada

Defeito **confirmado** pela suite unitaria (ver [[Relatorios/RT-001_Suite_Unitaria_Pytest|RT-001]]):
`tests/test_control.py` chama `Recycle_midia` pela instancia e captura o `TypeError` com
`@pytest.mark.xfail(strict=False)`; um teste paralelo chama `Control.Recycle_midia('x')`
(forma estatica) e prova que a logica de `os.remove` esta correta — isolando o defeito na
assinatura (`self` ausente). Quando corrigido, o xfail vira xpass.

## Referencias

- [[BUG-001_Video_Audio_Sem_Executor|BUG-001 · Video_Audio sem executor]]
- [[RNF-001_Execucao_Raspberry_Pi3|RNF-001 · Execucao no Raspberry Pi 3]]
- [[Referencia_Modulos|Referencia de Modulos]]
- [[Arquitetura_Software|Arquitetura do Software]]
