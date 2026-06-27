---
title: RF-005 · Video + pergunta por voz com analise de video
id: RF-005
type: requisito
categoria: funcional
status: aprovado
prioridade: media
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
verificado_por: [TP-001_Validacao_Reconhecimento_Gestos, TP-002_Validacao_Fluxo_IA_Gemini]
tags: [requisito, funcional, module/software, layer/especificacao, prio/media, tema/gestos, tema/ia, tema/visao]
---

# RF-005 · Video + pergunta por voz com analise de video

## Descricao

O sistema deve, ao reconhecer o gesto **rock** (`Hands.Map_Rock`) executado com a **mao direita**, gravar um video e capturar a pergunta por voz, enviar o video e o prompt ao Gemini para analise e reproduzir a resposta em audio.

A acao e disparada em `main.py` pela entrada `Map_Rock → Video_Audio(cap, executor)` (mao `Right`, cooldown de 20 frames) e implementada em `Control.Video_Audio`, que submete `Capture_Video` e `Capture_Audio` ao executor e depois chama `asyncio.run(jarvis_system.Video_To_Text(video_path, prompt))`. O `Video_To_Text` faz `genai.upload_file`, aguarda o processamento e, ao final, limpa os arquivos no Gemini (`Delete_Cahche_Files`).

## Criterios de aceitacao

- [ ] Com a mao direita formando o rock (indicador e mindinho levantados, medio e anelar dobrados), o fluxo inicia.
- [ ] Um video e gravado via `Capture_Video` (`midia/{timestamp}.avi`, XVID, 30 fps, 640x480) e a pergunta e capturada por `Capture_Audio`.
- [ ] `Video_To_Text` envia o video ao Gemini via `genai.upload_file` e aguarda enquanto `state == "PROCESSING"`; se `FAILED`, levanta `ValueError`.
- [ ] A resposta do Gemini e convertida em fala e reproduzida (ver [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007]]).
- [ ] Ao final, `Delete_Cahche_Files` remove os arquivos carregados no Gemini.
- [ ] A trava `ACTION` fica `True` durante o fluxo e volta a `False` ao final (ver [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008]]).

## Casos de uso associados

- [[CU-005_Analisar_Video_Com_Pergunta|CU-005 · Analisar video com pergunta]]
- [[Mapa_Gestos|Mapa de gestos]]

## Testes que verificam

- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Validacao de reconhecimento de gestos]]
- [[TP-002_Validacao_Fluxo_IA_Gemini|TP-002 · Validacao do fluxo de IA (Gemini)]]

## Observacoes

- **BUG conhecido:** em `Video_Audio`, `Capture_Audio` e submetido **sem** o argumento `executor` (`executor.submit(self.Capture_Audio)`), mas a assinatura exige `executor`. Isso quebra a captura de audio neste fluxo. Ver [[BUG-001_Video_Audio_Sem_Executor|BUG-001]].
- **Bloqueio sincrono:** `Video_To_Text` faz `time.sleep(10)` em loop enquanto o video processa (comentario no codigo: "Bomba, precisa ser limpo"). Isso bloqueia a thread e impacta latencia/responsividade. Ver [[RNF-004_Latencia_Resposta|RNF-004]].
- O upload do `.avi` ao Google Photos usa `Content-Type: image/jpeg` (hardcoded), inadequado para video. Ver [[RF-009_Upload_Automatico_Google_Photos|RF-009]].
- Dependencia da gravacao via `Control_Video`, sujeita ao quirk de toggle descrito em [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002]].

## Referencias

- [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini multimodal]]
- [[BUG-001_Video_Audio_Sem_Executor|BUG-001 · Video_Audio sem executor]]
- [[Ref_Google_Gemini_API|Referencia Google Gemini API]]
- [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002 · Gravacao de video]]
