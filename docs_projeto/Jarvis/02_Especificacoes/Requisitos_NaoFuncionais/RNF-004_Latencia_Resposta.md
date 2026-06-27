---
title: RNF-004 · Latencia de resposta falada
type: requisito
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
id: RNF-004
module: 02_Especificacoes
categoria: nao-funcional
prioridade: media
tags: [requisito, layer/especificacao, prio/media, tema/desempenho, tema/latencia]
---

# RNF-004 · Latencia de resposta falada

## Descricao

A resposta falada do Jarvis deve iniciar em um tempo **aceitavel para conversa**,
medido do momento do gesto/pergunta ate o **inicio** do audio de resposta. A meta
numerica nao esta definida no codigo e deve ser fixada por experimento.

## Justificativa

Interacao por voz tem expectativa conversacional: pausas longas degradam a
experiencia hands-free ([[RNF-002_Operacao_Hands_Free|RNF-002]]). A latencia e
composta por varias etapas, algumas locais (Pi 3) e outras na nuvem.

## Cadeia de latencia (do gesto ao audio)

1. Deteccao de gesto + debounce (`gesture_cooldown`, [[main.py]]).
2. Captura de audio: `adjust_for_ambient_noise(duration=2)` + `listen(timeout=5,
   phrase_time_limit=5)` em [[control.py]] — **ate ~7 s so de captura**.
3. STT online (`recognize_google`).
4. Inferencia do Gemini (`generate_content`).
5. TTS (`edge_tts` salva `response/translate.mp3`).
6. Playback via `pygame.mixer`.

## Gargalo critico: analise de video

`Video_To_Text` em [[jarvis.py]] faz upload do video para o Gemini e **bloqueia em
polling**:

```python
while video_file.state.name == "PROCESSING":
    print('.', end='')
    time.sleep(10)  # Bomba, precisa ser limpo ...
    video_file = genai.get_file(video_file.name)
```

O `time.sleep(10)` e **sincrono e bloqueante** (o proprio comentario do codigo o
chama de "Bomba"). Para videos longos, a resposta pode demorar dezenas de segundos
a minutos. Isso inviabiliza latencia conversacional na acao de video
([[RF-005_Video_Mais_Pergunta_Analise|RF-005]], gesto Rock).

## Criterios de aceitacao

| # | Criterio | Como medir | Meta |
|---|----------|------------|------|
| 1 | Tempo gesto → inicio do audio (texto/imagem) | cronometrar do disparo ate `SOUND.play()` | a definir |
| 2 | Tempo gesto → inicio do audio (video) | idem, fluxo `Video_To_Text` | a definir (espera-se > demais por causa do polling) |
| 3 | Captura de audio nao excede o necessario | revisar `duration`/`timeout`/`phrase_time_limit` | a definir |

> Sugestao de otimizacao: substituir `time.sleep(10)` por polling assincrono
> (`asyncio.sleep`) ou backoff menor; reduzir `adjust_for_ambient_noise` se o ruido
> for estavel. Registrar em [[Roadmap_Jarvis]].

## Referencias

- [[ADR-0004_Concorrencia_Asyncio_ThreadPool|ADR-0004 · Concorrencia asyncio + ThreadPool]]
- [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini multimodal]]
- [[RF-005_Video_Mais_Pergunta_Analise|RF-005 · Video + pergunta]]
- [[RNF-001_Execucao_Raspberry_Pi3|RNF-001 · Execucao no Pi 3]]
- [[Roadmap_Jarvis]]
