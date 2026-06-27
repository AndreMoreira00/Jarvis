---
title: Home — Jarvis
area: Dashboard
tags: [dashboard, home, jarvis]
project: Jarvis
created: 2026-06-27
updated: 2026-06-27
type: home
status: aprovado
---

# Home — Jarvis

**Jarvis** e o software de um par de oculos inteligentes (alvo de execucao: **Raspberry Pi 3**) operado inteiramente por **controle por gestos** — sem teclado, mouse ou toque. A camera frontal observa as maos do usuario, reconhece poses pre-definidas e dispara acoes que vao de tirar uma foto a fazer perguntas a uma IA multimodal, respondendo sempre **por voz**, em portugues do Brasil, com a persona "Jarvis".

O fluxo de processamento, executado **por frame** da camera, e: camera (OpenCV `cv2.VideoCapture(0)`) → deteccao de mao (**MediaPipe Hands**, 21 landmarks) → reconhecimento de gesto por geometria → acao de controle (classe `Control`) → **IA Google Gemini** (`gemini-2.0-flash-lite`, multimodal: texto/imagem/video) e/ou **upload no Google Photos** → resposta falada (**edge-tts** voz `pt-BR-AntonioNeural` + **pygame.mixer**). Cinco gestos sao reconhecidos (OK, joinha, dedo levantado, "L" e rock), cada um mapeado a uma acao na lista `checks` do loop principal. Veja o detalhamento em [[Mapa_Gestos|Mapa de Gestos]].

O codigo segue o padrao **uma classe por arquivo** ([[Arquitetura_Software|arquitetura]]): o loop `asyncio` vive em `main.py`; `Hands`, `Control`, `Jarvis` e `Manager` concentram, respectivamente, visao computacional, orquestracao de acoes, cliente Gemini+TTS e upload OAuth. O entry point real e `python main.py` (tecle `q` na janela do OpenCV para sair). Nesta fase o projeto e um **prototipo de software**: nao ha hardware fisico, firmware, suite de testes nem linter — a validacao e manual, rodando o app. Modulos de hardware, firmware, certificacoes, producao, marketing e legal estao **fora de escopo** e marcados para fases futuras.

## Areas

- [[00_SGI_Aplicado/README|00 · SGI Aplicado]] — objetivos, riscos e gates aplicados ao projeto
- [[01_Gestao/README|01 · Gestao]] — roadmap, atas, ADRs
- [[02_Especificacoes/README|02 · Especificacoes]] — requisitos, casos de uso, mapa de gestos
- [[03_Hardware/README|03 · Hardware]] — fora de escopo nesta fase
- [[04_Firmware/README|04 · Firmware]] — fora de escopo nesta fase
- [[05_Software_Auxiliar/README|05 · Software Auxiliar]] — arquitetura e modulos do app Python
- [[06_Testes_Validacao/README|06 · Testes & Validacao]] — planos de teste e bugs conhecidos
- [[07_Certificacoes_Homologacoes/README|07 · Certificacoes]] — fora de escopo nesta fase
- [[08_Producao/README|08 · Producao]] — fora de escopo nesta fase
- [[09_Manuais/README|09 · Manuais]] — guia rapido e instalacao
- [[10_Referencias/README|10 · Referencias]] — bibliotecas e servicos externos
- [[11_Marketing_Comercial/README|11 · Marketing & Comercial]] — fora de escopo nesta fase
- [[12_Suporte_PosVenda/README|12 · Suporte Pos-Venda]] — troubleshooting e FAQ
- [[13_Legal_IP/README|13 · Legal & IP]] — fora de escopo nesta fase
- [[99_Arquivo_Historico/README|99 · Arquivo Historico]]

## Documentacao chave

- [[Arquitetura_Software|Arquitetura do Software]] — loop async, classes e fluxo por frame
- [[Mapa_Gestos|Mapa de Gestos]] — os 5 gestos, a mao exigida e a acao disparada
- [[Roadmap_Jarvis|Roadmap]] — estado atual e proximos passos
- [[Troubleshooting_Jarvis|Troubleshooting]] — problemas comuns e solucoes
- [[Guia_Rapido_Execucao|Guia Rapido de Execucao]] — bootstrap e como rodar

## Views (Bases)

- [[../_views/Documentos_por_Clausula|Documentos por Clausula]]
- [[../_views/Rascunhos_Pendentes|Rascunhos Pendentes]]
- [[../_views/Documentos_Obsoletos|Documentos Obsoletos]]

## Templates

Inserir com `Ctrl+P` → "Insert template":

- [[_templates/ADR_Template]] — decisao tecnica
- [[_templates/Requisito_Template]] — requisito funcional/nao-funcional
- [[_templates/Teste_Template]] — plano de teste
- [[_templates/Ata_Template]] — ata de reuniao
- [[_templates/Bug_Template]] — registro de bug
- [[_templates/Release_Template]] — release notes
