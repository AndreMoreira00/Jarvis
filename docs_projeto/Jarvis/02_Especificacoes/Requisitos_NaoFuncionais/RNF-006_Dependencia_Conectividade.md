---
title: RNF-006 · Dependencia de conectividade
type: requisito
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
id: RNF-006
module: 02_Especificacoes
categoria: nao-funcional
prioridade: alta
tags: [requisito, layer/especificacao, prio/alta, tema/conectividade, tema/confiabilidade]
---

# RNF-006 · Dependencia de conectividade

## Descricao

As capacidades principais do Jarvis — IA (Gemini), reconhecimento de fala (STT) e
upload de midia — **exigem conexao com a internet**. Sem rede, o app perde quase toda
a funcionalidade util e fica restrito a captura local.

## Funcoes que exigem internet

| Funcao | Servico online | Onde no codigo |
|--------|----------------|----------------|
| STT (voz → texto) | Google Speech | [[control.py]] `Capture_Audio` (`recognize_google`) |
| Resposta de IA (texto/imagem/video) | Google Gemini | [[jarvis.py]] `Text_To_Text` / `Image_To_Text` / `Video_To_Text` |
| Sintese de voz (TTS) | Microsoft Edge TTS (online) | [[jarvis.py]] `Translate` (`edge_tts.Communicate`) |
| Upload de midia | Google Photos API | [[manager.py]] `uploadMidia` |

## Funcoes que rodam offline

| Funcao | Observacao |
|--------|------------|
| Captura de camera / deteccao de gestos | OpenCV + MediaPipe rodam local ([[main.py]], [[hands.py]]) |
| Captura de foto/video para `midia/` | `cv2.imwrite` / `VideoWriter` ([[control.py]]) |
| Sons de confirmacao | `pygame.mixer` toca `audios_check/` localmente |

## Comportamento sem rede (atual)

- `recognize_google` lanca `RequestError`, tratado em `Capture_Audio` retornando a
  string **"Erro de conexao"** — que e enviada como prompt ao Gemini (que tambem
  falhara sem rede).
- Chamadas ao Gemini e ao Google Photos levantam excecao de rede sem fallback
  dedicado.

## Criterios de aceitacao

| # | Criterio | Status | Como medir |
|---|----------|--------|------------|
| 1 | Sem rede, o app degrada de forma controlada (sem crash silencioso) | a definir | desligar rede e exercitar cada gesto |
| 2 | Usuario recebe feedback audivel de "sem conexao" | a definir | hoje so ha a string interna "Erro de conexao" |
| 3 | Captura local continua funcionando offline | atendido | fotos/videos salvos em `midia/` |
| 4 | Upload pendente e reenfileirado quando a rede volta | a definir | nao implementado |

## Riscos

- Latencia adicional e ponto unico de falha na nuvem (ver [[RNF-004_Latencia_Resposta|RNF-004]]).
- TTS via Edge tambem e online — mesmo a "voz" do Jarvis depende de rede
  (ver [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003]]).
- Implicacoes de privacidade do trafego de dados em [[RNF-005_Privacidade_Dados_Nuvem|RNF-005]].

## Referencias

- [[RNF-004_Latencia_Resposta|RNF-004 · Latencia de resposta]]
- [[RNF-005_Privacidade_Dados_Nuvem|RNF-005 · Privacidade de dados na nuvem]]
- [[ADR-0003_TTS_EdgeTTS_Pygame|ADR-0003 · TTS Edge-TTS + Pygame]]
- [[Troubleshooting_Jarvis]]
- [[Ref_SpeechRecognition]]
- [[Ref_Google_Gemini_API]]
