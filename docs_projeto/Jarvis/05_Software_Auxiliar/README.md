---
title: Software Auxiliar — Jarvis
area: Software_Auxiliar
tags: [readme, software, layer/software, module/software]
project: Jarvis
created: 2026-06-27
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Software Auxiliar

Neste projeto, o **software auxiliar e o produto inteiro**: o Jarvis e essencialmente
um app Python que roda na borda (alvo Raspberry Pi 3) e fala com a nuvem. Nao ha
firmware/hardware proprio aqui — o "auxiliar" e, na pratica, o sistema principal.

## Subpastas

| Pasta | Conteudo |
|---|---|
| [[Arquitetura_Software\|Desktop/]] | O app Python: arquitetura, modulos, loop por frame, concorrencia, entry point `python main.py`. |
| Integracoes_Cloud/ | Os servicos de nuvem consumidos: Google Gemini (IA multimodal) e Google Photos (upload). |

## Pontos de entrada

- Arquitetura completa (diagramas Mermaid): [[Arquitetura_Software]]
- Referencia por classe/metodo: [[Referencia_Modulos]]
- Integracoes de nuvem: [[ADR-0002_Gemini_Multimodal]], [[ADR-0005_Upload_Google_Photos_OAuth]]

## Referencias

- [[Guia_Rapido_Execucao]], [[Instalacao_Dependencias]]
- [[Roadmap_Jarvis]]
