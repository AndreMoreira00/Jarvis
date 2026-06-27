---
title: RF-004 · Foto + pergunta por voz com analise de imagem
id: RF-004
type: requisito
categoria: funcional
status: aprovado
prioridade: alta
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
verificado_por: [TP-001_Validacao_Reconhecimento_Gestos, TP-002_Validacao_Fluxo_IA_Gemini]
tags: [requisito, funcional, module/software, layer/especificacao, prio/alta, tema/gestos, tema/ia, tema/visao]
---

# RF-004 · Foto + pergunta por voz com analise de imagem

## Descricao

O sistema deve, ao reconhecer o gesto **"L"** (`Hands.Map_Squid`) executado com a **mao esquerda**, capturar uma foto e a pergunta por voz do usuario, enviar ambos ao Gemini para analise multimodal da imagem e reproduzir a resposta em audio.

A acao e disparada em `main.py` pela entrada `Map_Squid → Image_Audio(frame, executor)` (mao `Left`, cooldown de 20 frames) e implementada em `Control.Image_Audio`, que captura foto e audio **em paralelo** (`executor.submit`) e depois chama `asyncio.run(jarvis_system.Image_To_Text(image_path, prompt))`.

## Criterios de aceitacao

- [ ] Com a mao esquerda formando o "L" (indicador levantado, polegar aberto `polegar_4_x < polegar_2_x`, medio/anelar/mindinho dobrados), o fluxo inicia.
- [ ] Uma foto e capturada via `Capture_Photo` e salva em `midia/{timestamp}.jpg` (e enviada ao Google Photos, ver [[RF-009_Upload_Automatico_Google_Photos|RF-009]]).
- [ ] A pergunta e capturada e transcrita por `Capture_Audio` (STT pt-BR), em paralelo a captura da foto.
- [ ] `Image_To_Text` envia ao Gemini a imagem (`mime_type image/jpeg`, bytes via `pathlib.Path.read_bytes`) junto do prompt.
- [ ] A resposta do Gemini sobre a imagem e convertida em fala e reproduzida (ver [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007]]).
- [ ] A trava `ACTION` fica `True` durante o fluxo e volta a `False` ao final (ver [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008]]).

## Casos de uso associados

- [[CU-004_Analisar_Imagem_Com_Pergunta|CU-004 · Analisar imagem com pergunta]]
- [[Mapa_Gestos|Mapa de gestos]]

## Testes que verificam

- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Validacao de reconhecimento de gestos]]
- [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002 · Validacao do fluxo de IA (Gemini)]]

## Observacoes

- A foto usada na analise tambem e enviada ao Google Photos como efeito colateral de `Capture_Photo`. Para uso "so para a IA", isso pode ser indesejado (privacidade). Ver [[RNF-005_Privacidade_Dados_Nuvem|RNF-005]].
- A captura paralela de foto e audio reduz latencia, mas o resultado depende de ambos os `future.result()` retornarem; falha de STT envia string de erro como prompt (ver [[RF-003_Pergunta_Voz_Resposta_Falada|RF-003]]).
- A imagem e enviada inline (bytes), nao via `upload_file` — diferente do fluxo de video em [[RF-005_Video_Mais_Pergunta_Analise|RF-005]].

## Referencias

- [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini multimodal]]
- [[Ref_Google_Gemini_API|Referencia Google Gemini API]]
- [[RF-001_Captura_Foto_Gesto_Ok|RF-001 · Captura de foto]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007 · Resposta falada persona Jarvis]]
