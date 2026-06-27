---
title: edge-tts
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 10_Referencias
categoria: audio
tags: [referencia, biblioteca, module/software, tema/voz]
---

# edge-tts

## O que e

Biblioteca Python (`edge_tts`) que usa o servico de **Text-to-Speech do Microsoft
Edge / Azure Neural** para sintetizar fala a partir de texto. Gera audio com vozes
neurais de alta qualidade sem precisar de chave de API explicita. No Jarvis e o que
da **voz** a persona: converte a resposta em texto do Gemini num arquivo `.mp3`.

## Como o Jarvis usa

Na classe `Jarvis` ([jarvis.py](jarvis.py)), metodo `Translate(text)` (async).

| Item | Detalhe no codigo |
|---|---|
| Voz | `VOICES = ["pt-BR-AntonioNeural"]` -> `self.VOICE = VOICES[0]` |
| Sintese | `communicate = edge_tts.Communicate(text, self.VOICE)` |
| Saida | `await communicate.save(self.PATH_FILE)` |
| Caminho do arquivo | `self.PATH_FILE = "./response/translate.mp3"` |

Antes de sintetizar, `Translate` faz uma **limpeza de caracteres** que atrapalham a
fala, substituindo por espaco: tab (`\t`), asterisco (`*`), zero-width
(`​`/`‌`/`‍`), BOM (`﻿`) e espacos duplos (`  `); depois aplica
`strip()`. O `.mp3` resultante e tocado por [[Ref_Pygame_Mixer|pygame.mixer]] nos
metodos `Text_To_Text`, `Image_To_Text` e `Video_To_Text`. Requisito relacionado:
[[RF-007_Resposta_Falada_Persona_Jarvis|RF-007]].

## Pontos de atencao

- **Depende de conectividade**: a sintese ocorre via servico online da Microsoft;
  sem internet, nao ha voz ([[RNF-006_Dependencia_Conectividade|RNF-006]]).
- **Arquivo unico reutilizado**: sempre grava em `./response/translate.mp3`,
  sobrescrevendo a resposta anterior — a pasta `response/` precisa existir (criada
  por [[ProjectConfig.py|ProjectConfig.py]]).
- **Voz fixa em PT-BR**: `pt-BR-AntonioNeural` reforca o idioma do projeto
  ([[RNF-003_Idioma_PT_BR|RNF-003]]); trocar de voz e so alterar a lista `VOICES`.
- **Latencia**: a chamada de rede soma na latencia total da resposta
  ([[RNF-004_Latencia_Resposta|RNF-004]]).
- **Versao**: API `Communicate(...).save(...)` estavel; versao exata **verificar**.

## Link oficial

- https://github.com/rany2/edge-tts

## Referencias

- [[jarvis.py|Codigo: jarvis.py (metodo Translate)]]
- [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003 — TTS com edge-tts + pygame]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007 — Resposta falada com persona]]
- [[Ref_Pygame_Mixer|Referencia: pygame.mixer]]
- [[Ref_Google_Gemini_API|Referencia: Google Gemini API]]
