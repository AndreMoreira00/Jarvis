---
title: Requisitos_NaoFuncionais — Jarvis
area: Especificacoes/Requisitos_NaoFuncionais
tags: [readme, module/software, layer/especificacao]
project: Jarvis
created: 2026-06-27
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Requisitos NaoFuncionais

Requisitos nao-funcionais (RNF-NNN) do **Jarvis**: desempenho, idioma, privacidade,
confiabilidade e restricoes de plataforma. Definem *como* o sistema deve operar
(qualidade), complementando os [[../Requisitos_Funcionais/README|requisitos funcionais]]
que definem *o que* ele faz.

## Indice de RNFs

| ID | Requisito | Prioridade | Tema |
|----|-----------|------------|------|
| [[RNF-001_Execucao_Raspberry_Pi3\|RNF-001]] | Execucao no Raspberry Pi 3 (plataforma-alvo) | alta | desempenho / hardware |
| [[RNF-002_Operacao_Hands_Free\|RNF-002]] | Operacao hands-free (gestos e voz, sem teclado/mouse) | alta | usabilidade / gestos |
| [[RNF-003_Idioma_PT_BR\|RNF-003]] | Idioma portugues do Brasil em STT, persona e TTS | alta | idioma / voz |
| [[RNF-004_Latencia_Resposta\|RNF-004]] | Latencia de resposta falada aceitavel para conversa | media | desempenho / latencia |
| [[RNF-005_Privacidade_Dados_Nuvem\|RNF-005]] | Privacidade dos dados enviados a servicos de terceiros | alta | privacidade / seguranca |
| [[RNF-006_Dependencia_Conectividade\|RNF-006]] | Dependencia de conectividade para IA, STT e upload | alta | conectividade / confiabilidade |

## Notas

- Metas numericas (FPS, latencia, uso de memoria) ainda **nao** estao definidas no
  codigo; aparecem como "a definir" com a forma de medir proposta em cada nota.
- Plataforma-alvo e decisao registrada em [[ADR-0007_Alvo_Raspberry_Pi3|ADR-0007]].

## Referencias

- [[../Requisitos_Funcionais/README|Requisitos Funcionais]]
- [[Arquitetura_Software|Arquitetura do software]]
- [[Roadmap_Jarvis]]
- [[Home]]
