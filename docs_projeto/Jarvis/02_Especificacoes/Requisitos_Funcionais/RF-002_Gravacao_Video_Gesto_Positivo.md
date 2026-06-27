---
title: RF-002 · Gravacao de video por gesto positivo
id: RF-002
type: requisito
categoria: funcional
status: aprovado
prioridade: alta
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
verificado_por: [TP-001_Validacao_Reconhecimento_Gestos, TP-003_Validacao_Captura_E_Upload]
tags: [requisito, funcional, module/software, layer/especificacao, prio/alta, tema/gestos, tema/captura]
---

# RF-002 · Gravacao de video por gesto positivo

## Descricao

O sistema deve, ao reconhecer o gesto **positivo/joinha** (`Hands.Map_Positive`) executado com a **mao esquerda**, gravar um arquivo de video em `midia/{timestamp}.avi`, codec **XVID**, **30 fps**, resolucao **640x480**, enquanto a flag `Control.Control_Video` estiver ligada. Ao parar, o sistema toca um som de confirmacao e envia o video ao Google Photos.

A acao e disparada em `main.py` pela entrada `Map_Positive → Capture_Video(cap, executor)` (mao `Left`, cooldown de 30 frames) e implementada em `Control.Capture_Video`. O loop de gravacao (`while self.Control_Video: cap.read() → out.write(frame)`) escreve frame a frame ate a flag ser desligada.

## Criterios de aceitacao

- [ ] Com a mao esquerda formando o joinha (polegar 4 acima do polegar 1 em `0.05 * h`, indicador/medio/anelar/mindinho dobrados), a gravacao inicia.
- [ ] O arquivo e criado via `cv2.VideoWriter` com fourcc `XVID`, fps `30`, resolucao `(640, 480)`, em `midia/{timestamp}.avi`.
- [ ] O som `audios_check/video_starter.wav` toca no inicio da gravacao.
- [ ] Enquanto `Control_Video == True`, cada frame lido de `cap` e escrito no arquivo de video.
- [ ] Ao encerrar, `out.release()` e chamado, o som `audios_check/video_out.wav` toca e o video e submetido ao upload (ver [[RF-009_Upload_Automatico_Google_Photos|RF-009]]).
- [ ] `Capture_Video` retorna o caminho do video salvo (`midia/{timestamp}.avi`).

## Casos de uso associados

- [[CU-002_Gravar_Video|CU-002 · Gravar video]]
- [[Mapa_Gestos|Mapa de gestos]]

## Testes que verificam

- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Validacao de reconhecimento de gestos]]
- [[TP-003_Validacao_Captura_E_Upload|TP-003 · Validacao de captura e upload]]

## Observacoes

- **Quirk de controle de estado:** a gravacao depende de `Control_Video`, mas essa flag e alternada (`toggle`) por `Check_Gesture` em **todo** disparo de gesto, nao so no gesto positivo. Na pratica, o estado de gravacao liga/desliga de forma acoplada a qualquer acao, o que e fragil e dificulta um inicio/fim deterministico. Ver [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008]].
- A resolucao e fixa em `640x480`. Se a camera entregar frames de tamanho diferente, o `VideoWriter` pode gerar arquivo invalido — comportamento a definir/validar em campo.
- O upload de video usa `Content-Type: image/jpeg` (hardcoded em `Manager.uploadMidia`), inadequado para `.avi`. Risco documentado em [[RF-009_Upload_Automatico_Google_Photos|RF-009]].
- `Capture_Video` nao seta a trava `ACTION`; protecao apenas pelo cooldown (30 frames).

## Referencias

- [[ADR-0004_Concorrencia_Asyncio_ThreadPool|ADR-0004 · Concorrencia asyncio/ThreadPool]]
- [[Ref_OpenCV|Referencia OpenCV]]
- [[RF-005_Video_Mais_Pergunta_Analise|RF-005 · Video + pergunta]]
- [[RF-009_Upload_Automatico_Google_Photos|RF-009 · Upload automatico Google Photos]]
