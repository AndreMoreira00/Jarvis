---
title: Integracoes_Cloud — Jarvis
area: Software_Auxiliar/Integracoes_Cloud
tags: [readme, software, layer/software, module/software, tema/nuvem]
project: Jarvis
created: 2026-06-27
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Integracoes Cloud

Servicos de nuvem que o Jarvis consome. Toda a logica vive no app desktop
([[Arquitetura_Software]]); aqui ficam os provedores, escopos e segredos.

## Provedores

| Servico | Onde | Papel | Segredo |
|---|---|---|---|
| **Google Gemini** (`gemini-2.0-flash-lite`) | `jarvis.py` (classe `Jarvis`) | IA multimodal (texto, imagem, video) com persona PT-BR; resposta vira fala. | `.env` -> `API_GEMINI=<chave>` |
| **Google Photos** (Library API) | `manager.py` (classe `Manager`) | Upload automatico de fotos/videos via OAuth2. | `env/client_secret.json` (OAuth desktop) -> gera `env/token.json` no 1o uso |

- Escopo OAuth: `https://www.googleapis.com/auth/photoslibrary`.
- Quirk do upload: `Content-Type`/`X-Goog-Upload-Content-Type` fixos em `image/jpeg`,
  mesmo para video `.avi` (ver [[ADR-0005_Upload_Google_Photos_OAuth]]).
- Dependencia de conectividade e privacidade dos dados na nuvem:
  [[RNF-005_Privacidade_Dados_Nuvem]], [[RNF-006_Dependencia_Conectividade]].

## Referencias

- ADRs: [[ADR-0002_Gemini_Multimodal]], [[ADR-0005_Upload_Google_Photos_OAuth]]
- Referencias externas: [[Ref_Google_Gemini_API]], [[Ref_Google_Photos_API]]
- Requisitos: [[RF-009_Upload_Automatico_Google_Photos]],
  [[RF-003_Pergunta_Voz_Resposta_Falada]]
