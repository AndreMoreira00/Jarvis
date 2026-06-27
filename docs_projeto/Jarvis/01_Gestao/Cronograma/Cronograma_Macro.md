---
title: Cronograma Macro do Jarvis
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 01_Gestao
layer: gestao
tags: [cronograma, module/software, layer/gestao, tema/produto]
---

# Cronograma Macro do Jarvis

Marcos de alto nivel do **Jarvis**, alinhados as fases do [[Roadmap_Jarvis|Roadmap]]. Nao ha datas calendario definidas — o cronograma usa **janelas relativas** a partir de um marco zero (T0). T0 corresponde ao inicio do trabalho de estabilizacao (fim da Fase 1).

> Convencao de janelas: `T0`, `T0+1`, `T0+2`, ... sao periodos relativos (a unidade — sprint, mes — fica **a definir**). Datas absolutas serao fixadas quando houver baseline de planejamento.

## Marcos de alto nivel

| Marco | Janela | Fase do roadmap | Descricao | Criterio de saida | Status |
|---|---|---|---|---|---|
| M0 | T0 | [[Roadmap_Jarvis#fase-1-prototipo-de-software-atual\|Fase 1]] | Prototipo de software ponta a ponta em desktop (gestos + IA + voz + upload) | Demo completa rodando via `python main.py` | Em andamento |
| M1 | T0+1 | [[Roadmap_Jarvis#fase-1-prototipo-de-software-atual\|Fase 1]] | Validacao manual dos gestos e fluxos de IA | Planos [[TP-001_Validacao_Reconhecimento_Gestos\|TP-001]] / [[TP-002_Validacao_Fluxo_IA_Gemini\|TP-002]] / [[TP-003_Validacao_Captura_E_Upload\|TP-003]] executados | A definir |
| M2 | T0+2 | [[Roadmap_Jarvis#fase-2-estabilizar-e-empacotar\|Fase 2]] | Correcao dos bugs conhecidos | [[BUG-001_Video_Audio_Sem_Executor\|BUG-001]], [[BUG-002_Recycle_Midia_Sem_Self\|BUG-002]], [[BUG-003_ProjectConfig_Mkdir_Sem_ExistOk\|BUG-003]] fechados | A definir |
| M3 | T0+2 | [[Roadmap_Jarvis#fase-2-estabilizar-e-empacotar\|Fase 2]] | Saneamento de dependencias e polling nao-bloqueante do video | `requirements.txt` limpo; `Video_To_Text` sem `time.sleep` bloqueante | A definir |
| M4 | T0+3 | [[Roadmap_Jarvis#fase-2-estabilizar-e-empacotar\|Fase 2]] | Build reprodutivel no Raspberry Pi 3 | App executa no alvo — ver [[RNF-001_Execucao_Raspberry_Pi3\|RNF-001]], [[ADR-0007_Alvo_Raspberry_Pi3\|ADR-0007]] | A definir |
| M5 | T0+4 | [[Roadmap_Jarvis#fase-3-hardware-dos-oculos-e-firmware\|Fase 3]] | Selecao de hardware (camera frontal, audio por conducao ossea) | Componentes definidos e adquiridos | A definir |
| M6 | T0+5 | [[Roadmap_Jarvis#fase-3-hardware-dos-oculos-e-firmware\|Fase 3]] | Integracao do prototipo vestivel + firmware de bring-up | Oculos com perifericos integrados ao software | A definir |
| M7 | T0+6 | [[Roadmap_Jarvis#fase-4-testes-de-campo-e-otimizacao\|Fase 4]] | Testes de campo com usuarios | Sessoes de uso real registradas | A definir |
| M8 | T0+7 | [[Roadmap_Jarvis#fase-4-testes-de-campo-e-otimizacao\|Fase 4]] | Otimizacao de desempenho e latencia no alvo | Metas de [[RNF-004_Latencia_Resposta\|RNF-004]] e [[RNF-001_Execucao_Raspberry_Pi3\|RNF-001]] atingidas | A definir |

## Dependencias entre marcos

- **M2/M3 dependem de M1**: estabilizar exige saber o que falha (validacao manual primeiro).
- **M4 depende de M2/M3**: so faz sentido portar para o Pi 3 com o software corrigido e as dependencias saneadas.
- **M5/M6 dependem de M4**: o hardware integra-se ao software ja portavel ao alvo.
- **M7/M8 dependem de M6**: testes de campo e otimizacao exigem o prototipo vestivel montado.

## Observacoes

- As janelas relativas (`T0+n`) **nao** implicam duracao fixa por marco; servem apenas para ordenacao.
- A unidade de tempo (sprint/mes) e a baseline de datas absolutas permanecem **a definir**.
- Mudancas de escopo nas fases devem refletir tanto aqui quanto no [[Roadmap_Jarvis|Roadmap]].

## Referencias

- [[Roadmap_Jarvis|Roadmap do Jarvis]] — fases macro que estes marcos detalham
- [[Arquitetura_Software|Arquitetura do Software]]
- Planos de teste: [[TP-001_Validacao_Reconhecimento_Gestos|TP-001]], [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002]], [[TP-003_Validacao_Captura_E_Upload|TP-003]]
- Bugs: [[BUG-001_Video_Audio_Sem_Executor|BUG-001]], [[BUG-002_Recycle_Midia_Sem_Self|BUG-002]], [[BUG-003_ProjectConfig_Mkdir_Sem_ExistOk|BUG-003]]
- [[Home|Home do projeto]]
