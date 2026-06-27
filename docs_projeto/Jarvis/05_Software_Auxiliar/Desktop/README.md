---
title: Desktop — Jarvis
area: Software_Auxiliar/Desktop
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

# Desktop

O **app Python do Jarvis** — o nucleo do produto. Loop `asyncio` de visao
computacional que detecta gestos (MediaPipe), dispara acoes (captura de midia,
consulta ao Gemini, upload) e responde por voz (edge-tts + pygame).

- **Entry point real**: `python main.py` (tecle `q` na janela do OpenCV para sair).
  O `python jarvis.py` citado no README da raiz esta **desatualizado** — `jarvis.py`
  so define a classe `Jarvis`.
- **Bootstrap**: `python ProjectConfig.py` cria `response/` e `midia/` e um `.env`.
  `.env` precisa de `API_GEMINI=<chave>`.
- **Plataforma alvo**: Raspberry Pi 3 ([[ADR-0007_Alvo_Raspberry_Pi3]],
  [[RNF-001_Execucao_Raspberry_Pi3]]).

## Notas desta pasta

| Nota | Conteudo |
|---|---|
| [[Arquitetura_Software]] | Visao geral, tabela arquivo->classe->papel, modelo de concorrencia e diagramas Mermaid (loop, mapa de gestos, fluxos de IA, componentes). |
| [[Referencia_Modulos]] | Referencia detalhada por classe/metodo (assinaturas, efeitos colaterais), fiel ao codigo. |

## Referencias

- [[Mapa_Gestos]] — geometria dos 5 gestos
- [[Guia_Rapido_Execucao]], [[Instalacao_Dependencias]]
- [[Troubleshooting_Jarvis]], [[FAQ_Jarvis]]
