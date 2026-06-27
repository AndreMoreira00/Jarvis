---
title: Google Photos Library API
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 10_Referencias
categoria: nuvem
tags: [referencia, biblioteca, module/software, tema/upload]
---

# Google Photos Library API

## O que e

API REST do Google para fazer upload e gerenciar itens de midia na biblioteca do
**Google Photos** do usuario, autenticada via **OAuth 2.0**. No Jarvis e o destino
das fotos e videos capturados: cada midia gravada e enviada para a conta do usuario.

## Como o Jarvis usa

Na classe `Manager` ([manager.py](manager.py)), com `requests` + bibliotecas
`google-auth` / `google-auth-oauthlib`.

| Etapa | Detalhe no codigo |
|---|---|
| Segredo OAuth | `CLIENT_SECRET = './env/client_secret.json'` (app desktop) |
| Token persistido | `CREDENTIALS_FILE = './env/token.json'` |
| Escopo | `SCOPES = ['https://www.googleapis.com/auth/photoslibrary']` |
| Fluxo OAuth | `InstalledAppFlow.from_client_secrets_file(...).run_local_server(port=0)` |
| Refresh | se expirado e ha `refresh_token`: `creds.refresh(Request())` |
| Upload bruto | `POST /v1/uploads` com `X-Goog-Upload-Protocol: raw` e `X-Goog-Upload-Content-Type: image/jpeg` |
| Criacao do item | `POST /v1/mediaItems:batchCreate` com `uploadToken` + `fileName` |
| URL do item | `getPhotoUrl(...)` -> `GET /v1/mediaItems/{id}` -> `baseUrl` |

O metodo `uploadMidia(image_path)` e chamado de forma assincrona via
`executor.submit(...)` em `Capture_Photo` e `Capture_Video`
([control.py](control.py)). Requisito relacionado:
[[RF-009_Upload_Automatico_Google_Photos|RF-009]].

## Pontos de atencao

- **`Content-Type` fixo `image/jpeg`** mesmo para video `.avi`: quirk do codigo. O
  upload de video pode falhar ou ser interpretado errado pelo Photos.
- **`photo_url` calculado mas nao usado**: `uploadMidia` chama `getPhotoUrl(...)`
  porem nao retorna nem armazena a URL — chamada de rede sem efeito util.
- **Primeiro uso abre navegador**: `run_local_server(port=0)` sobe servidor local e
  exige interacao do usuario para autorizar — atrito num dispositivo headless como o
  [[ADR-0007_Alvo_Raspberry_Pi3|Raspberry Pi 3]].
- **Segredos em `env/`**: `client_secret.json` e `token.json` ficam em `./env/`;
  nunca versionar. Sem `client_secret.json` o upload falha.
- **Privacidade / conectividade**: midias vao para a nuvem
  ([[RNF-005_Privacidade_Dados_Nuvem|RNF-005]]) e exigem rede
  ([[RNF-006_Dependencia_Conectividade|RNF-006]]).
- **Erro != 200**: cai em `response.raise_for_status()`, propagando excecao.
- **Versao da API**: endpoints v1 estaveis; a API do Photos passou por mudancas de
  escopo recentes — **verificar** disponibilidade do escopo `photoslibrary`.

## Link oficial

- https://developers.google.com/photos

## Referencias

- [[manager.py|Codigo: manager.py (classe Manager)]]
- [[ADR-0005_Upload_Google_Photos_OAuth|ADR-0005 — Upload Google Photos via OAuth]]
- [[RF-009_Upload_Automatico_Google_Photos|RF-009 — Upload automatico]]
- [[Ref_OpenCV|Referencia: OpenCV]]
- [[Troubleshooting_Jarvis|Troubleshooting]]
