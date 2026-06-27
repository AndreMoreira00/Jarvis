---
title: CU-004 · Analisar imagem com pergunta por voz
id: CU-004
type: caso-de-uso
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
prioridade: alta
tags: [module/software, layer/especificacao, tema/gestos, tema/ia, prio/alta]
---

# CU-004 · Analisar imagem com pergunta por voz

Captura uma foto do que o usuário está vendo, faz uma pergunta falada sobre ela e
recebe a análise multimodal do Gemini em áudio. Disparado pelo gesto **"L"** com a
**mão esquerda**.

## Ator

- **Usuário** dos óculos inteligentes.

## Pré-condições

- App `main.py` rodando, câmera aberta, mão detectada.
- `Control.ACTION == False` e `gesture_cooldown == 0`.
- Microfone disponível; pastas `midia/` e `response/` existentes.
- `.env` com `API_GEMINI` válida; conexão com a internet.

## Gesto disparador

| Atributo | Valor |
|---|---|
| Método | `Hands.Map_Squid` |
| Mão exigida | Esquerda (`Left`) |
| Cooldown | 20 frames |
| Estado (`state`) | `Async` |
| Ação | `Control.Image_Audio(frame, executor)` |

**Geometria (Map_Squid):** indicador levantado
(`indicador_8_y < indicador_6_y - 0.05 * h`), polegar aberto/lateral para o lado
oposto (`polegar_4_x < polegar_2_x`) e médio, anelar e mindinho dobrados — formando
um "L".

## Fluxo principal

1. `Check_Gesture` confirma `Map_Squid == True` e `hand_label == "Left"`.
2. `gesture_cooldown = 20`; alterna `Control_Video`; submete
   `Image_Audio(frame, executor)`.
3. `Image_Audio`:
   - seta `ACTION = True`;
   - submete **em paralelo** `Capture_Photo(frame, executor)` e
     `Capture_Audio(executor)` ao executor;
   - aguarda `future_foto.result()` → `image_path` e `future_audio.result()` →
     `prompt`.
4. `Capture_Photo` grava `midia/<timestamp>.jpg`, toca `photo_take.wav` e dispara
   o upload (ver [[CU-001_Tirar_Foto]]).
5. `Capture_Audio` transcreve a fala em pt-BR (ver [[CU-003_Perguntar_Por_Voz]]).
6. `asyncio.run(jarvis_system.Image_To_Text(image_path, prompt))`:
   - `generate_content([{mime_type: image/jpeg, data: <bytes da imagem>}, prompt])`;
   - `Translate(response.text)` → `response/translate.mp3` (edge-tts);
   - toca o mp3 via `pygame.mixer`.
7. Seta `ACTION = False`.

## Fluxos alternativos e de erro

- **Mão errada / cooldown / ação em curso:** não dispara.
- **STT falha:** `prompt` assume `"Sem Pergunta"` / `"Erro de conexão"` /
  `"Erro inesperado: <e>"` e segue para o Gemini junto com a imagem (a foto ainda
  é analisada, mas o prompt textual é o de erro).
- **Foto salva mas upload falha:** `uploadMidia` levanta exceção na thread; a
  análise da imagem **não** depende do upload (lê os bytes do disco local).
- **Falha na API Gemini:** exceção propaga no `asyncio.run`; risco de `ACTION`
  permanecer `True` (sem `finally`).
- **Concorrência:** foto e áudio são submetidos ao mesmo `ThreadPoolExecutor`;
  ambos os `result()` são bloqueantes na thread de `Image_Audio`.

## Pós-condições

- `midia/<timestamp>.jpg` salvo (e upload tentado em background).
- Resposta multimodal do Gemini reproduzida em áudio.
- `ACTION == False` ao final; `gesture_cooldown == 20`.

## Observações

- Reaproveita integralmente `Capture_Photo` e `Capture_Audio` — boa separação de
  responsabilidades.
- A imagem é enviada inline (bytes), diferente do vídeo, que usa `upload_file`
  (ver [[CU-005_Analisar_Video_Com_Pergunta]]).

## Requisitos relacionados

- [[RF-004_Foto_Mais_Pergunta_Analise|RF-004 · Foto + pergunta para análise]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007 · Resposta falada com persona Jarvis]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008 · Debounce, cooldown e trava de ação]]

## Referências

- [[Mapa_Gestos|Mapa de gestos]]
- [[CU-001_Tirar_Foto|CU-001 · Tirar foto]]
- [[CU-003_Perguntar_Por_Voz|CU-003 · Perguntar por voz]]
- [[Ref_Google_Gemini_API|Referência: Google Gemini API]]
- [[Ref_SpeechRecognition|Referência: SpeechRecognition]]
- [[Ref_Edge_TTS|Referência: edge-tts]]
- [[Arquitetura_Software|Arquitetura do software]]
