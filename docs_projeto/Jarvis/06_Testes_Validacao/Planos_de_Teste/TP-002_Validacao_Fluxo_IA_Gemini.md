---
title: TP-002 · Validacao do Fluxo de IA (Gemini)
id: TP-002
type: plano-de-teste
status: rascunho
requisitos_cobertos: [RF-003, RF-004, RF-005, RF-007]
executante:
data_execucao:
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 06_Testes_Validacao
prioridade: alta
tags: [teste, plano, tema/ia, layer/teste, prio/alta]
---

# TP-002 · Validacao do Fluxo de IA (Gemini)

## Objetivo

Verificar de ponta a ponta os tres fluxos multimodais que enviam contexto ao **Google Gemini** (`gemini-2.0-flash-lite`) e retornam **resposta falada** com a persona Jarvis (PT-BR, voz `pt-BR-AntonioNeural`, via `edge-tts` + `pygame.mixer`):

| Fluxo | Gesto | Metodo `Control` | Metodo `Jarvis` |
|---|---|---|---|
| Pergunta por voz | `Map_Speak` (Right) | `Audio_to_Audio` | `Text_To_Text` |
| Foto + pergunta | `Map_Squid` (Left) | `Image_Audio` | `Image_To_Text` |
| Video + pergunta | `Map_Rock` (Right) | `Video_Audio` | `Video_To_Text` |

Teste **manual** rodando `python main.py`.

## Requisitos verificados

- [[RF-003_Pergunta_Voz_Resposta_Falada|RF-003 · Pergunta por voz, resposta falada]]
- [[RF-004_Foto_Mais_Pergunta_Analise|RF-004 · Foto + pergunta (analise)]]
- [[RF-005_Video_Mais_Pergunta_Analise|RF-005 · Video + pergunta (analise)]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007 · Resposta falada com persona Jarvis]]

Relacionado: [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini Multimodal]], [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003 · TTS edge-tts + pygame]].

## Equipamento e setup

| Item | Requisito | Observacao |
|------|-----------|------------|
| Webcam | Dispositivo `0` | Necessaria para os fluxos de foto e video |
| Microfone | Conectado e funcional | STT via `SpeechRecognition.recognize_google(language="pt-BR")` |
| Conexao com a internet | Estavel | Gemini, Google STT e edge-tts sao **servicos online** |
| `.env` | `API_GEMINI=<chave valida>` | Sem chave valida o `generate_content` falha |
| Pasta `response/` | Existente | Recebe `translate.mp3` (saida do TTS) |
| Pasta `midia/` | Existente | Recebe a foto (`Image_Audio`) e o video (`Video_Audio`) |
| Caixa de som / fone | Funcional | Reproducao via `pygame.mixer` |
| Ambiente | Baixo ruido | `adjust_for_ambient_noise(duration=2)`; `energy_threshold=300` |

## Procedimento

### Parte A — `Audio_to_Audio` (`Map_Speak`, RF-003)

1. Fazer o gesto `Map_Speak` com a mao **Right**.
2. Ao ouvir o som de inicio, falar uma pergunta clara em PT-BR (ex.: "Mestre pergunta: o que e visao computacional?").
   - Quirk: o codigo toca o som de **inicio de video** (`video_start_sound`) ao capturar audio. Registrar, nao e falha do teste.
3. Aguardar a captura (timeout 5s, `phrase_time_limit` 5s) e o envio ao Gemini.
4. Confirmar que a resposta falada e **coerente** com a pergunta, em PT-BR, e com tom de persona ("Mestre").

### Parte B — `Image_Audio` (`Map_Squid`, RF-004)

5. Posicionar um objeto reconhecivel no campo da camera.
6. Fazer o gesto `Map_Squid` ("L") com a mao **Left**.
7. Falar uma pergunta sobre a cena (ex.: "Mestre pergunta: o que voce ve nesta imagem?").
8. Confirmar que: (a) uma foto `.jpg` foi salva em `midia/`; (b) a resposta falada **descreve o conteudo da imagem** de forma coerente.

### Parte C — `Video_To_Text` / `Video_Audio` (`Map_Rock`, RF-005)

> ATENCAO: o fluxo `Map_Rock -> Control.Video_Audio` esta **bloqueado por um defeito conhecido** — ver [[BUG-001_Video_Audio_Sem_Executor|BUG-001]] (`self.Capture_Audio()` chamado sem o argumento `executor`, gera `TypeError`). Enquanto BUG-001 nao for corrigido, a Parte C deve ser executada de forma **isolada** chamando `Jarvis.Video_To_Text(video_path, prompt)` diretamente (ex.: pequeno script de bancada), para validar o lado do Gemini.

9. Gravar/obter um clipe `.avi` curto em `midia/`.
10. Invocar `Video_To_Text` com o caminho do video e um prompt textual.
11. Observar o loop de PROCESSING (imprime `.` e dorme 10s por iteracao — bloqueante; o codigo comenta "Bomba, precisa ser limpo").
12. Confirmar que a resposta falada e coerente com o conteudo do video e que `Delete_Cahche_Files()` limpa os arquivos no Gemini ao final.

### Verificacoes transversais de persona/voz (RF-007)

13. Em todas as respostas: voz `pt-BR-AntonioNeural`, PT-BR, tratamento "Mestre", sem ler caracteres de markdown (o `Translate` remove `*`, tabs, zero-width, BOM, espacos duplos).

## Criterios de aprovacao

- [ ] **A**: `Map_Speak` -> resposta falada coerente com a pergunta de voz (RF-003).
- [ ] **B**: `Map_Squid` -> foto salva em `midia/` + resposta que descreve a imagem (RF-004).
- [ ] **C**: `Video_To_Text` (isolado) -> resposta coerente com o video (RF-005); registrar que o fluxo via gesto esta bloqueado por [[BUG-001_Video_Audio_Sem_Executor|BUG-001]].
- [ ] Todas as respostas em PT-BR, voz correta, persona "Mestre" (RF-007).
- [ ] O `response/translate.mp3` e (re)gerado a cada resposta.
- [ ] Sem leitura de simbolos de markdown na fala.

## Resultados

| Parte | Fluxo | Resposta coerente? | Latencia aprox. | Observacoes |
|-------|-------|--------------------|-----------------|-------------|
| A | `Audio_to_Audio` | | | |
| B | `Image_Audio` | | | |
| C | `Video_To_Text` (isolado) | | | BUG-001 bloqueia via gesto |

Ver relatorio: [[]]

## Referencias

- [[RF-003_Pergunta_Voz_Resposta_Falada|RF-003]]
- [[RF-004_Foto_Mais_Pergunta_Analise|RF-004]]
- [[RF-005_Video_Mais_Pergunta_Analise|RF-005]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007]]
- [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini Multimodal]]
- [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003 · TTS edge-tts + pygame]]
- [[Ref_Google_Gemini_API|Referencia · Google Gemini API]]
- [[Ref_Edge_TTS|Referencia · edge-tts]]
- [[Ref_SpeechRecognition|Referencia · SpeechRecognition]]
- [[BUG-001_Video_Audio_Sem_Executor|BUG-001 · Video_Audio sem executor]]
- [[TP-001_Validacao_Reconhecimento_Gestos|TP-001 · Validacao de gestos]]
- [[TP-003_Validacao_Captura_E_Upload|TP-003 · Validacao de captura e upload]]
