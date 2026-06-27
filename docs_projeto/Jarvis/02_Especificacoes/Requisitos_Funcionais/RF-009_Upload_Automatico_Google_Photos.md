---
title: RF-009 · Upload automatico para o Google Photos
id: RF-009
type: requisito
categoria: funcional
status: aprovado
prioridade: media
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
verificado_por: [TP-003_Validacao_Captura_E_Upload]
tags: [requisito, funcional, module/software, layer/especificacao, prio/media, tema/captura, tema/nuvem]
---

# RF-009 · Upload automatico para o Google Photos

## Descricao

O sistema deve enviar automaticamente toda midia capturada (foto `.jpg` e video `.avi`) ao **Google Photos**, via OAuth2, sem intervencao do usuario. O upload e disparado por `executor.submit(menager_system.uploadMidia, caminho)` em `Capture_Photo` e `Capture_Video`, rodando em paralelo ao loop de camera.

O fluxo em `Manager` e: `authorize_credentials` obtem/renova o token (`env/token.json`; primeiro uso abre `InstalledAppFlow.run_local_server` com `env/client_secret.json`), seguido de `POST /v1/uploads` (protocolo raw) e `POST /v1/mediaItems:batchCreate` com o `uploadToken` e o `fileName`.

## Criterios de aceitacao

- [ ] Toda foto salva por `Capture_Photo` e submetida a `uploadMidia`.
- [ ] Todo video salvo por `Capture_Video` e submetido a `uploadMidia`.
- [ ] No primeiro uso, o fluxo OAuth abre o navegador (`run_local_server(port=0)`) e gera `env/token.json`.
- [ ] Em usos subsequentes, o token e lido de `env/token.json` e renovado via `refresh_token` quando expirado.
- [ ] O upload usa `POST /v1/uploads` (header `X-Goog-Upload-Protocol: raw`) e, se status 200, cria o item com `mediaItems:batchCreate`.
- [ ] Em status diferente de 200, o erro e propagado via `response.raise_for_status()`.

## Casos de uso associados

- [[CU-001_Tirar_Foto|CU-001 · Tirar foto]]
- [[CU-002_Gravar_Video|CU-002 · Gravar video]]

## Testes que verificam

- [[TP-003_Validacao_Captura_E_Upload|TP-003 · Validacao de captura e upload]]

## Observacoes

- **Quirk de Content-Type:** `uploadMidia` envia sempre `X-Goog-Upload-Content-Type: image/jpeg`, mesmo para video `.avi`. O upload de video pode ser rejeitado ou interpretado incorretamente pelo Google Photos — comportamento a validar. Ver [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002]] e [[RF-005_Video_Mais_Pergunta_Analise|RF-005]].
- `getPhotoUrl` calcula `photo_url` (baseUrl), mas o valor **nao e retornado nem utilizado** por `uploadMidia` — chamada potencialmente desnecessaria.
- Requer `env/client_secret.json` (OAuth desktop) presente; sem ele, o primeiro upload falha.
- Implicacao de privacidade: midia (incluindo a usada apenas para analise da IA em [[RF-004_Foto_Mais_Pergunta_Analise|RF-004]]) e enviada a nuvem. Ver [[RNF-005_Privacidade_Dados_Nuvem|RNF-005]].
- O upload depende de conectividade. Ver [[RNF-006_Dependencia_Conectividade|RNF-006]].

## Referencias

- [[ADR-0005_Upload_Google_Photos_OAuth|ADR-0005 · Upload Google Photos OAuth]]
- [[Ref_Google_Photos_API|Referencia Google Photos API]]
- [[RF-001_Captura_Foto_Gesto_Ok|RF-001 · Captura de foto]]
- [[RNF-005_Privacidade_Dados_Nuvem|RNF-005 · Privacidade de dados na nuvem]]
