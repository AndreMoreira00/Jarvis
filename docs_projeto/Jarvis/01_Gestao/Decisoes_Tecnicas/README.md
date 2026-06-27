---
title: Decisoes_Tecnicas — Jarvis
area: Gestao/Decisoes_Tecnicas
tags: [readme, module/software, layer/gestao, tema/arquitetura]
project: Jarvis
created: 2026-06-27
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Decisoes Tecnicas

ADRs (Architecture Decision Records) do projeto **Jarvis** — registram as decisoes de
arquitetura, suas alternativas e consequencias. Novos ADRs devem seguir o template
[[ADR_Template]] e o schema de [[CONVENCOES|Convencoes]] (ID `ADR-XXXX`, zero-padded,
imutavel).

## Indice

| ID | Titulo | Status |
|---|---|---|
| ADR-0001 | [[ADR-0001_MediaPipe_Hands\|MediaPipe Hands para deteccao de mao e gestos]] | aceito |
| ADR-0002 | [[ADR-0002_Gemini_Multimodal\|Google Gemini multimodal como motor de IA]] | aceito |
| ADR-0003 | [[ADR-0003_TTS_EdgeTTS_Pygame\|edge-tts + pygame.mixer para resposta falada]] | aceito |
| ADR-0004 | [[ADR-0004_Concorrencia_Asyncio_ThreadPool\|asyncio + ThreadPoolExecutor no loop de camera]] | aceito |
| ADR-0005 | [[ADR-0005_Upload_Google_Photos_OAuth\|Google Photos Library API via OAuth2 para upload de midia]] | aceito |
| ADR-0006 | [[ADR-0006_Arquitetura_Classe_Por_Arquivo\|Uma classe por arquivo e cadeia Control->Jarvis+Manager]] | aceito |
| ADR-0007 | [[ADR-0007_Alvo_Raspberry_Pi3\|Raspberry Pi 3 como plataforma alvo]] | aceito |

## Referencias

- [[Arquitetura_Software]] — visao geral da arquitetura e do fluxo por frame
- [[Referencia_Modulos]] — mapa arquivo -> classe -> papel
- [[CONVENCOES|Convencoes]] — schema de frontmatter, naming e IDs
