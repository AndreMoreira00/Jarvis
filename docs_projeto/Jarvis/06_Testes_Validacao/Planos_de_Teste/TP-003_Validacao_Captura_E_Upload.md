---
title: TP-003 · Validacao de Captura e Upload (Google Photos)
id: TP-003
type: plano-de-teste
status: rascunho
requisitos_cobertos: [RF-001, RF-002, RF-009]
executante:
data_execucao:
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 06_Testes_Validacao
prioridade: alta
tags: [teste, plano, tema/midia, tema/upload, layer/teste, prio/alta]
---

# TP-003 · Validacao de Captura e Upload (Google Photos)

## Objetivo

Verificar que a captura de **foto** (gesto OK) e de **video** (gesto Positivo) grava os arquivos corretos em `midia/` e que esses arquivos sao **enviados automaticamente** ao Google Photos via OAuth2 (`manager.py`).

Teste **manual** rodando `python main.py`.

## Requisitos verificados

- [[RF-001_Captura_Foto_Gesto_Ok|RF-001 · Captura de foto (gesto OK)]]
- [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002 · Gravacao de video (gesto Positivo)]]
- [[RF-009_Upload_Automatico_Google_Photos|RF-009 · Upload automatico no Google Photos]]

Relacionado: [[ADR-0005_Upload_Google_Photos_OAuth|ADR-0005 · Upload Google Photos OAuth]].

## Equipamento e setup

| Item | Requisito | Observacao |
|------|-----------|------------|
| Webcam | Dispositivo `0` | `Capture_Photo` usa o frame atual; `Capture_Video` le do `cap` |
| Conexao com a internet | Estavel | Upload e API online |
| `env/client_secret.json` | OAuth desktop (Google Cloud) | Escopo `photoslibrary` |
| `env/token.json` | Gerado no 1o uso | `run_local_server(port=0)` abre o consentimento no navegador |
| Pasta `midia/` | Existente | Destino dos arquivos (`{timestamp}.jpg` / `{timestamp}.avi`) |
| Conta Google Photos | Acessivel | Para verificar o item enviado |

> 1a execucao do upload: o navegador abrira para autorizar. Concluir o consentimento; `token.json` sera salvo e reutilizado (refresh automatico).

## Procedimento

### Parte A — Foto (`Capture_Photo`, RF-001 + RF-009)

1. Fazer o gesto **OK** (`Map_Ok`) com a mao **Right**.
2. Confirmar o som `photo_take.wav`.
3. Verificar em `midia/` um arquivo `{YYYYMMDD_HHMMSS}.jpg` recem-criado.
4. Abrir o arquivo e confirmar que e a imagem capturada (nao corrompida).
5. Aguardar o `executor.submit(uploadMidia, ...)`. Abrir o Google Photos e confirmar que a **foto aparece** (nome = basename do arquivo).

### Parte B — Video (`Capture_Video`, RF-002 + RF-009)

6. Fazer o gesto **Positivo / joinha** (`Map_Positive`) com a mao **Left** para **iniciar** a gravacao (alterna `Control_Video` para `True`). Confirmar `video_starter.wav`.
   - Quirk: qualquer gesto alterna `Control_Video` (toggle em `Check_Gesture`). Atencao ao estado real da flag. Ver [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002]].
7. Manter a cena por alguns segundos (o loop `while self.Control_Video` grava frames a 30 fps, resolucao 640x480, codec XVID).
8. Repetir um gesto que desligue `Control_Video` para **parar**. Confirmar `video_out.wav`.
9. Verificar em `midia/` um arquivo `{YYYYMMDD_HHMMSS}.avi`; abrir e confirmar a reproducao.
10. Confirmar que o video aparece no Google Photos.
    - Quirk: `uploadMidia` envia sempre com `Content-Type: image/jpeg`, mesmo para `.avi`. Registrar se o Photos aceita/recusa o `.avi`. Ver [[RF-009_Upload_Automatico_Google_Photos|RF-009]] e [[ADR-0005_Upload_Google_Photos_OAuth|ADR-0005]].

### Parte C — Integridade do upload

11. Confirmar `mediaItems:batchCreate` retornou sucesso (item criado). Em caso de status != 200, o codigo levanta `raise_for_status()` — registrar o erro.
    - Nota: `photo_url` e calculado em `uploadMidia` (`getPhotoUrl`) mas **nao e retornado nem usado**; nao deve impactar o resultado do upload.

## Criterios de aprovacao

- [ ] **A**: foto `.jpg` salva em `midia/` com timestamp correto e conteudo valido (RF-001).
- [ ] **B**: video `.avi` salvo em `midia/` (XVID, 640x480, 30 fps), reproduzivel (RF-002).
- [ ] **A/B**: ambos os arquivos aparecem no Google Photos (RF-009).
- [ ] OAuth funciona: 1o uso gera `token.json`; usos seguintes reaproveitam/renovam o token.
- [ ] Sons de confirmacao corretos por etapa (`photo_take`, `video_starter`, `video_out`).
- [ ] Comportamento do `.avi` com `Content-Type image/jpeg` documentado (aceito/recusado).

## Resultados

| Item | Salvo em `midia/`? | Conteudo valido? | No Google Photos? | Observacoes |
|------|--------------------|------------------|-------------------|-------------|
| Foto `.jpg` | | | | |
| Video `.avi` | | | | quirk: upload como image/jpeg |

Ver relatorio: [[]]

## Referencias

- [[RF-001_Captura_Foto_Gesto_Ok|RF-001]]
- [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002]]
- [[RF-009_Upload_Automatico_Google_Photos|RF-009]]
- [[ADR-0005_Upload_Google_Photos_OAuth|ADR-0005 · Upload Google Photos OAuth]]
- [[Ref_Google_Photos_API|Referencia · Google Photos API]]
- [[Ref_OpenCV|Referencia · OpenCV]]
- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Validacao de gestos]]
- [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002 · Validacao do fluxo de IA]]
