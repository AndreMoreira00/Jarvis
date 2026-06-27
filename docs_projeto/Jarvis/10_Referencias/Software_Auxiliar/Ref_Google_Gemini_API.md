---
title: Google Gemini API (google.generativeai)
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 10_Referencias
categoria: ia
tags: [referencia, biblioteca, module/software, tema/ia]
---

# Google Gemini API (google.generativeai)

## O que e

SDK Python oficial do **Google Gemini** (`google.generativeai`, importado como
`genai`). Da acesso aos modelos generativos multimodais da Google, capazes de
processar **texto, imagem e video** num mesmo prompt. E o "cerebro" do Jarvis:
recebe a pergunta (e opcionalmente a midia capturada) e devolve a resposta que sera
falada.

## Como o Jarvis usa

Encapsulado na classe `Jarvis` ([jarvis.py](jarvis.py)).

| Item | Detalhe no codigo |
|---|---|
| Chave de API | `os.getenv("API_GEMINI")` via `python-dotenv` (`.env`) |
| Configuracao | `genai.configure(api_key=self.API_KEY)` |
| Modelo | `genai.GenerativeModel("gemini-2.0-flash-lite", system_instruction=self.template)` |
| Persona | `self.template` (PT-BR, IA "Jarvis" que trata o usuario como "Mestre") |
| Texto | `model.generate_content(prompt)` em `Text_To_Text` |
| Imagem | `generate_content([{'mime_type':'image/jpeg', 'data': pathlib.Path(...).read_bytes()}, prompt])` em `Image_To_Text` |
| Video (upload) | `genai.upload_file(path=video_path)` em `Video_To_Text` |
| Video (poll) | `while video_file.state.name == "PROCESSING": time.sleep(10)` + `genai.get_file(...)` |
| Video (geracao) | `generate_content([video_file, prompt], request_options={"timeout": 600})` |
| Limpeza | `Delete_Cahche_Files()` -> `genai.list_files()` + `get_file(...).delete()` |

O resultado e lido em `response.text`, passado a `Translate()` (TTS via
[[Ref_Edge_TTS|edge-tts]]) e tocado com [[Ref_Pygame_Mixer|pygame.mixer]]. Fluxos de
negocio em [[RF-003_Pergunta_Voz_Resposta_Falada|RF-003]],
[[RF-004_Foto_Mais_Pergunta_Analise|RF-004]] e
[[RF-005_Video_Mais_Pergunta_Analise|RF-005]].

## Pontos de atencao

- **`time.sleep(10)` bloqueante** no loop de processamento de video: o proprio codigo
  comenta "Bomba, precisa ser limpo". Trava o fluxo enquanto o Gemini processa o
  video (ver [[Troubleshooting_Jarvis|Troubleshooting]]).
- **Mime type fixo `image/jpeg`** em `Image_To_Text`: coerente com as fotos `.jpg`,
  mas nao generaliza para outros formatos.
- **Armazenamento de arquivos no servidor**: `upload_file` deixa o video na conta
  Gemini; `Delete_Cahche_Files()` (note o typo "Cahche" no codigo) limpa **todos** os
  arquivos listados — cuidado em ambiente compartilhado.
- **Privacidade**: imagens/videos sao enviados para a nuvem da Google
  ([[RNF-005_Privacidade_Dados_Nuvem|RNF-005]]) e exigem conectividade
  ([[RNF-006_Dependencia_Conectividade|RNF-006]]).
- **Versao do modelo**: `gemini-2.0-flash-lite` confirmado no codigo; disponibilidade
  e nome podem mudar — **verificar** na console.

## Link oficial

- https://ai.google.dev

## Referencias

- [[jarvis.py|Codigo: jarvis.py (classe Jarvis)]]
- [[ADR-0002_Gemini_Multimodal|ADR-0002 — Gemini multimodal]]
- [[RF-003_Pergunta_Voz_Resposta_Falada|RF-003 — Pergunta por voz]]
- [[RF-004_Foto_Mais_Pergunta_Analise|RF-004 — Foto + pergunta]]
- [[RF-005_Video_Mais_Pergunta_Analise|RF-005 — Video + pergunta]]
- [[Ref_Edge_TTS|Referencia: edge-tts]]
- [[Ref_Pygame_Mixer|Referencia: pygame.mixer]]
- [[Arquitetura_Software|Arquitetura do Software]]
