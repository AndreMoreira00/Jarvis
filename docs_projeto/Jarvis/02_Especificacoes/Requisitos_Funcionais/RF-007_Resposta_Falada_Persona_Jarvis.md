---
title: RF-007 · Resposta falada com persona Jarvis
id: RF-007
type: requisito
categoria: funcional
status: aprovado
prioridade: alta
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
verificado_por: [TP-002_Validacao_Fluxo_IA_Gemini]
tags: [requisito, funcional, module/software, layer/especificacao, prio/alta, tema/ia, tema/voz, tema/persona]
---

# RF-007 · Resposta falada com persona Jarvis

## Descricao

O sistema deve converter as respostas textuais do Gemini em fala, usando **edge-tts** com a voz **`pt-BR-AntonioNeural`**, e reproduzir o audio via `pygame.mixer`. A IA deve adotar a persona **"Jarvis"**: um assistente que trata o usuario como **"Mestre"**, com foco em programacao, machine learning, ciencia de dados e visao computacional, sendo preciso, objetivo e proativo.

A persona e definida pelo `system_instruction` (template em `jarvis.py`) passado ao `GenerativeModel("gemini-2.0-flash-lite")`. A sintese ocorre em `Jarvis.Translate` (limpeza de caracteres + `edge_tts.Communicate(text, VOICE).save("./response/translate.mp3")`), e a reproducao em `Text_To_Text` / `Image_To_Text` / `Video_To_Text` via `mixer.Sound`.

## Criterios de aceitacao

- [ ] O modelo Gemini e instanciado com o `system_instruction` da persona Jarvis (trata o usuario como "Mestre").
- [ ] A resposta textual passa por `Translate`, que remove caracteres indesejados (tab, `*`, zero-width `​/c/d`, BOM `﻿`, espacos duplos) e faz `strip`.
- [ ] O audio e gerado por edge-tts com a voz `pt-BR-AntonioNeural` e salvo em `./response/translate.mp3`.
- [ ] O `.mp3` e reproduzido via `pygame.mixer.Sound`, aguardando a duracao completa (`asyncio.sleep(get_length())`).
- [ ] Todos os fluxos de IA (texto, imagem, video) usam o mesmo caminho de sintese e reproducao.

## Casos de uso associados

- [[CU-003_Perguntar_Por_Voz|CU-003 · Perguntar por voz]]
- [[CU-004_Analisar_Imagem_Com_Pergunta|CU-004 · Analisar imagem]]
- [[CU-005_Analisar_Video_Com_Pergunta|CU-005 · Analisar video]]

## Testes que verificam

- [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002 · Validacao do fluxo de IA (Gemini)]]

## Observacoes

- A pasta `response/` precisa existir (criada por `ProjectConfig.py`); caso contrario `Communicate.save` falha.
- O arquivo `translate.mp3` e sobrescrito a cada resposta — nao ha historico de audios. Comportamento intencional.
- A geracao de TTS e online (edge-tts usa servico Microsoft). Ver [[RNF-006_Dependencia_Conectividade|RNF-006]] e [[RNF-003_Idioma_PT_BR|RNF-003]].
- A persona e parametrizada apenas pelo `system_instruction`; mudancas de tom/escopo nao exigem alterar o codigo de fluxo.

## Referencias

- [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003 · TTS edge-tts + pygame]]
- [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini multimodal]]
- [[Ref_Edge_TTS|Referencia edge-tts]]
- [[Ref_Pygame_Mixer|Referencia pygame.mixer]]
