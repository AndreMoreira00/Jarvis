---
title: RISCO-002 · Dependencia de conectividade com a nuvem
id: RISCO-002
type: risco
status: aberto
prioridade: alta
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 00_SGI_Aplicado
tags: [risco, module/software, prio/alta, tema/conectividade]
---

# RISCO-002 · Dependencia de conectividade com a nuvem

## Descricao

As funcoes centrais do Jarvis dependem de **servicos online** e, portanto, de **conexao com a internet**. Sem rede, as acoes que envolvem IA, transcricao de voz e upload **falham**:

| Servico | Usado em | Falha sem internet |
|---|---|---|
| Google Gemini | `Text_To_Text`, `Image_To_Text`, `Video_To_Text` | sem resposta da IA |
| Google STT (`recognize_google`) | `Capture_Audio` | retorna "Erro de conexao" (`sr.RequestError`) |
| edge-tts | `Translate` | nao gera o `translate.mp3` (sem fala) |
| Google Photos API | `uploadMidia` | upload nao acontece |

So a captura local (foto/video em `midia/`) e o reconhecimento de gestos (MediaPipe roda offline) seguem funcionando.

## Probabilidade x Impacto

| Dimensao | Avaliacao | Justificativa |
|---|---|---|
| Probabilidade | **Media** | Oculos moveis podem perder rede facilmente (uso em campo) |
| Impacto | **Alto** | Sem rede, o assistente de IA — o coracao do produto — fica inutilizado |
| Severidade resultante | **Alta** | — |

## Gatilhos / sintomas

- Resposta falada nunca chega apos um gesto de pergunta.
- Mensagem "Erro de conexao" retornada pela captura de audio.
- Midia capturada nao aparece no Google Photos.

## Mitigacoes

- Tratar e **sinalizar ao usuario** quedas de rede (hoje `Capture_Audio` ja captura `RequestError`, mas a falha de `edge-tts`/Gemini nao tem feedback falado).
- Avaliar fila de upload para reenviar midia quando a rede voltar.
- Considerar STT/TTS locais e modelos on-device como evolucao para reduzir a dependencia.

## Dono e status

- Status: **aberto**.
- Vinculado a [[RNF-006_Dependencia_Conectividade|RNF-006]] e [[RNF-005_Privacidade_Dados_Nuvem|RNF-005]] (dados trafegam para a nuvem).

## Referencias

- [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini multimodal]]
- [[ADR-0005_Upload_Google_Photos_OAuth|ADR-0005 · Upload Google Photos]]
- [[Troubleshooting_Jarvis|Troubleshooting]]
- [[Home|Home — Jarvis]]
