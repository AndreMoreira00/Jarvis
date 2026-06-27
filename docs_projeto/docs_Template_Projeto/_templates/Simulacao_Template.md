---
title: SIM-XXX · {{title}}
type: simulacao
status: rascunho
serie:
ferramenta: ltspice
data_execucao:
executante:
versao_ferramenta:
modelos_spice: []
verifica_requisito: []
relacionado_tp: []
decisao_derivada: []
resultado: inconclusivo
fonte_externa:
artefatos_origem: []
tags: [simulacao]
created: 2026-04-22
updated: 2026-04-23
---

# SIM-XXX · {{title}}

## Contexto

> Por que esta simulação existe? Qual problema técnico ela responde, qual hipótese valida, qual requisito-mãe ela verifica?

## Setup

### Topologia

> Descrição do circuito (ou cenário CFD/FEM). Opcional: imagem do schematic em `_assets/Simulacoes/SIM-XXX/`.

### Modelos SPICE / componentes

| Componente | Modelo | Origem | Notas |
|---|---|---|---|
|  |  |  |  |

### Parâmetros varridos

| Variável | Faixa | Passo | Justificativa |
|---|---|---|---|
|  |  |  |  |

### Hipóteses e condições

-

## Decks de simulação

| Deck | Análise | Output principal |
|---|---|---|
| `<deck>.cir` | AC / TRAN / NOISE / DC | V(out) vs freq |

## Resultados

> Tabelas-resumo + imagens em `_assets/Simulacoes/SIM-XXX/*.png` (até 5 plots-chave). A vault deve responder isolada — sem precisar abrir o repo `LTSPICE-Simulations`.

| Métrica | Valor medido | Critério | Resultado |
|---|---|---|---|
|  |  |  |  |

## Conclusões

-

## Decisões e rastreabilidade

- **Verifica requisito**: [[]]
- **Plano de teste correspondente**: [[]]
- **Decisão derivada (ADR)**: [[]]

## Histórico

- Executada em: {{date:YYYY-MM-DD}} por {{executante}}
- Repo de origem (rastreabilidade histórica): `LTSPICE-Simulations/projects/<id>` — artefatos `.cir`/`.asc`/`.raw` lá; vault não duplica binários.
