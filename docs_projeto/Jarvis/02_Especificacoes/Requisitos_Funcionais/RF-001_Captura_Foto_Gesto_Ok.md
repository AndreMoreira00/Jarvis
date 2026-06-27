---
title: RF-001 · Captura de foto por gesto OK
id: RF-001
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

# RF-001 · Captura de foto por gesto OK

## Descricao

O sistema deve, ao reconhecer o gesto **OK/pinca** (`Hands.Map_Ok`) executado com a **mao direita**, capturar o frame atual da camera, salvar a imagem em disco no caminho `midia/{timestamp}.jpg` (timestamp no formato `%Y%m%d_%H%M%S`), tocar um som de confirmacao e enviar a foto automaticamente ao Google Photos.

A acao e disparada em `main.py` pela entrada `Map_Ok → Capture_Photo(frame, executor)` (mao `Right`, cooldown de 20 frames) e implementada em `Control.Capture_Photo`. O upload roda em paralelo via `executor.submit(menager_system.uploadMidia, caminho)`, sem bloquear o loop de camera.

## Criterios de aceitacao

- [ ] Com a mao direita formando o gesto OK (polegar 4 proximo do indicador 8, distancia < `0.05 * w`, demais dedos baixos), o sistema captura uma foto.
- [ ] A imagem e gravada via `cv2.imwrite` em `midia/{timestamp}.jpg` com timestamp `%Y%m%d_%H%M%S`.
- [ ] O som `audios_check/photo_take.wav` toca como confirmacao apos a captura.
- [ ] A foto e submetida ao upload no Google Photos (ver [[RF-009_Upload_Automatico_Google_Photos|RF-009]]).
- [ ] O gesto OK feito com a **mao esquerda** NAO dispara a captura (a mao exigida e `Right`).
- [ ] Apos disparar, o gesto respeita o cooldown de 20 frames antes de poder disparar de novo (ver [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008]]).
- [ ] `Capture_Photo` retorna o caminho da foto salva (`midia/{timestamp}.jpg`).

## Casos de uso associados

- [[CU-001_Tirar_Foto|CU-001 · Tirar foto]]
- [[Mapa_Gestos|Mapa de gestos]]

## Testes que verificam

- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Validacao de reconhecimento de gestos]]
- [[TP-003_Validacao_Captura_E_Upload|TP-003 · Validacao de captura e upload]]

## Observacoes

- `Capture_Photo` **nao** seta a trava `ACTION`, ao contrario das acoes de IA. A protecao contra disparo repetido vem apenas do `gesture_cooldown` (20 frames). Ver [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008]].
- Quirk de `Check_Gesture`: todo disparo de gesto alterna (`toggle`) a flag `Control_Video`. Isso e inofensivo para a foto, mas afeta a gravacao de video — ver [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002]].
- A pasta `midia/` precisa existir antes da execucao (criada por `ProjectConfig.py`); caso contrario `cv2.imwrite` falha silenciosamente.
- O upload usa sempre `Content-Type: image/jpeg`, o que e correto para foto `.jpg` (detalhe relevante para video em [[RF-005_Video_Mais_Pergunta_Analise|RF-005]]).

## Referencias

- [[ADR-0006_Arquitetura_Classe_Por_Arquivo|ADR-0006 · Arquitetura classe por arquivo]]
- [[Arquitetura_Software|Arquitetura do software]]
- [[Ref_OpenCV|Referencia OpenCV]]
- [[RF-009_Upload_Automatico_Google_Photos|RF-009 · Upload automatico Google Photos]]
