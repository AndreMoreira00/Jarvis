---
title: ADR-0005 · Google Photos Library API via OAuth2 para upload de midia
id: ADR-0005
type: adr
status: aceito
deciders: [Andre Moreira]
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 01_Gestao
tags: [adr, decisao-tecnica, tema/upload, tema/nuvem, layer/software]
---

# ADR-0005 · Google Photos Library API via OAuth2 para upload de midia

## Contexto

O Jarvis captura fotos (`.jpg`) e videos (`.avi`) na pasta `midia/` e precisa de um
destino persistente para essa midia fora do dispositivo. O alvo e um Raspberry Pi 3
(ver [[ADR-0007_Alvo_Raspberry_Pi3]]), com armazenamento limitado (cartao SD) e sem
garantia de backup — manter tudo localmente nao escala e arrisca perda de dados.

Forcas em jogo:

- O usuario ja vive no ecossistema Google (a IA usada e o Gemini — ver
  [[ADR-0002_Gemini_Multimodal]]), entao reaproveitar credenciais Google reduz atrito.
- O Google Photos oferece armazenamento de fotos/videos com app movel para consulta.
- O upload acontece em background, disparado pela acao de captura, sem bloquear o loop
  de visao (ver [[ADR-0004_Concorrencia_Asyncio_ThreadPool]]).

## Decisao

Implementar o upload na classe `Manager` ([manager.py](../../../../manager.py)) usando a
**Google Photos Library API** com autenticacao **OAuth2 desktop**:

1. **Credenciais.** `client_secret` lido de `./env/client_secret.json` (OAuth desktop).
   Escopo unico: `https://www.googleapis.com/auth/photoslibrary`.
2. **Fluxo de autorizacao** (`authorize_credentials`): se `./env/token.json` existir,
   carrega as credenciais; se invalidas mas com `refresh_token`, faz `refresh`; senao
   roda `InstalledAppFlow.from_client_secrets_file(...).run_local_server(port=0)` (abre o
   navegador no primeiro uso). Persiste o token em `./env/token.json` e retorna
   `creds.token`.
3. **Upload em duas etapas** (`uploadMidia`):
   - `POST /v1/uploads` com os bytes brutos do arquivo, headers
     `X-Goog-Upload-Protocol: raw` e `X-Goog-Upload-Content-Type: image/jpeg`.
   - Se `status_code == 200`, `POST /v1/mediaItems:batchCreate` com `uploadToken` +
     `fileName` (`os.path.basename`), recebendo o `photo_id`.
   - Em qualquer outro status, `response.raise_for_status()`.
4. **Disparo.** As acoes de captura em [control.py](../../../../control.py)
   (`Capture_Photo`, `Capture_Video`) chamam `executor.submit(self.menager_system.uploadMidia, caminho)`,
   rodando o upload em uma thread do pool.

### Quirks documentados

- **Content-Type fixo `image/jpeg` mesmo para video `.avi`.** O header
  `X-Goog-Upload-Content-Type` esta hard-coded como `image/jpeg`, mas `Capture_Video`
  tambem chama `uploadMidia` para arquivos `.avi`. O tipo declarado nao corresponde ao
  conteudo real para videos — risco de rejeicao/processamento incorreto pelo Google
  Photos. Candidato a correcao (derivar o MIME da extensao).
- **`photo_url` calculado mas nao usado.** Apos o `batchCreate`, `uploadMidia` chama
  `self.getPhotoUrl(access_token, photo_id)` e atribui o resultado a `photo_url`, porem
  a variavel **nao e retornada nem usada** — `uploadMidia` nao tem `return`. A chamada
  extra `getPhotoUrl` (um `GET mediaItems/{id}`) e desperdicada.

## Alternativas consideradas

- **Armazenamento somente local** (manter em `midia/` no cartao SD) — sem dependencia de
  rede nem OAuth. Rejeitada: nao resolve backup nem consulta remota, e o SD do RPi3 e
  pequeno e fragil.
- **S3 / Google Drive / storage generico** — mais flexivel para tipos de arquivo e
  metadados. Rejeitada por ora: exigiria gerenciar buckets/billing e nao oferece a UX de
  galeria pronta do Photos. Fica registrada como alternativa no [[Roadmap_Jarvis]].
- **Sem upload (descartar apos uso)** — simplicidade maxima. Rejeitada: perde-se o
  registro das capturas, que e parte do valor do produto.

## Consequencias

### Positivas
- Backup automatico e galeria consultavel no app Google Photos.
- Reaproveita o ecossistema Google ja presente (Gemini).
- Upload assincrono nao bloqueia o loop de visao.

### Negativas / riscos
- **Setup OAuth manual**: exige `env/client_secret.json` e um primeiro login interativo
  (`run_local_server`) — incomodo em um dispositivo headless como o RPi3 montado nos
  oculos.
- **Escopo amplo `photoslibrary`**: concede acesso de leitura/escrita a biblioteca de
  fotos do usuario — implicacoes de privacidade (ver [[RNF-005_Privacidade_Dados_Nuvem]]).
- **Dependencia de rede**: sem conectividade, o upload falha
  (ver [[RNF-006_Dependencia_Conectividade]]).
- **Quirk do Content-Type**: videos `.avi` enviados como `image/jpeg` podem falhar ou
  ser processados incorretamente.
- **`photo_url` desperdicado**: chamada de rede inutil e codigo morto.
- **Erros sobem como excecao** dentro da thread do executor; sem tratamento, podem passar
  despercebidos (futures nao aguardadas).

## Referencias

- [[Ref_Google_Photos_API]] — referencia da Google Photos Library API
- [[RF-009_Upload_Automatico_Google_Photos]] — requisito de upload automatico
- [[RNF-005_Privacidade_Dados_Nuvem]] — privacidade dos dados na nuvem
- [[RNF-006_Dependencia_Conectividade]] — dependencia de conectividade
- [[ADR-0002_Gemini_Multimodal]] — uso do ecossistema Google para a IA
- [[Arquitetura_Software]] — papel do `Manager` na arquitetura
