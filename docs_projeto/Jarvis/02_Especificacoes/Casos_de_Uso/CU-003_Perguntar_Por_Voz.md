---
title: CU-003 · Perguntar por voz e ouvir a resposta
id: CU-003
type: caso-de-uso
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
prioridade: alta
tags: [module/software, layer/especificacao, tema/gestos, tema/ia, prio/alta]
---

# CU-003 · Perguntar por voz e ouvir a resposta

Faz uma pergunta falada ao Jarvis e recebe a resposta em áudio (voz do assistente).
Disparado pelo gesto **dedo levantado** com a **mão direita**.

## Ator

- **Usuário** dos óculos inteligentes.

## Pré-condições

- App `main.py` rodando, câmera aberta, mão detectada.
- `Control.ACTION == False` e `gesture_cooldown == 0`.
- Microfone disponível (`sr.Microphone`).
- `.env` com `API_GEMINI=<chave>` válida.
- Conexão com a internet (STT Google + API Gemini).
- Pasta `response/` existente (saída do TTS).

## Gesto disparador

| Atributo | Valor |
|---|---|
| Método | `Hands.Map_Speak` |
| Mão exigida | Direita (`Right`) |
| Cooldown | 20 frames |
| Estado (`state`) | `Async` |
| Ação | `Control.Audio_to_Audio(executor)` |

**Geometria (Map_Speak):** apenas o indicador levantado
(`indicador_8_y < indicador_5_y - 0.05 * h`), polegar lateral
(`polegar_4_x > polegar_1_x`) e médio, anelar e mindinho dobrados.

## Fluxo principal

1. `Check_Gesture` confirma `Map_Speak == True` e `hand_label == "Right"`.
2. `gesture_cooldown = 20`; alterna `Control_Video`; submete
   `Audio_to_Audio(executor)`.
3. `Audio_to_Audio`:
   - seta `ACTION = True` (trava global);
   - submete `Capture_Audio(executor)` e aguarda `future_audio.result()` →
     `prompt`.
4. `Capture_Audio`:
   - configura `Recognizer` (`pause_threshold=0.8`,
     `dynamic_energy_threshold=False`, `energy_threshold=300`,
     `maxAlternatives=1`);
   - abre `sr.Microphone`; `adjust_for_ambient_noise(duration=2)`;
   - toca `audios_check/video_starter.wav` (**quirk:** usa o som de início de
     **vídeo** para confirmar captura de áudio);
   - `listen(timeout=5, phrase_time_limit=5)`;
   - `recognize_google(language="pt-BR")` → texto transcrito.
5. `Audio_to_Audio` chama `asyncio.run(jarvis_system.Text_To_Text(prompt))`.
6. `Jarvis.Text_To_Text`:
   - `model.generate_content(prompt)` (modelo `gemini-2.0-flash-lite`, persona
     "Jarvis" que trata o usuário como "Mestre");
   - `Translate(response.text)` limpa caracteres e gera `response/translate.mp3`
     via `edge-tts` (voz `pt-BR-AntonioNeural`);
   - toca o mp3 via `pygame.mixer.Sound`.
7. `Audio_to_Audio` seta `ACTION = False`.

## Fluxos alternativos e de erro

- **Mão errada / cooldown / ação em curso:** não dispara.
- **STT não entende o áudio:** `sr.UnknownValueError` → `prompt = "Sem Pergunta"`;
  esse texto vira o prompt enviado ao Gemini (não há curto-circuito).
- **Falha de conexão no STT:** `sr.RequestError` → `prompt = "Erro de conexão"`.
- **Erro inesperado no STT:** `Exception` → `prompt = "Erro inesperado: <e>"`.
- **Falha na API Gemini:** exceção em `generate_content` propaga dentro do
  `asyncio.run`; `ACTION` pode permanecer `True` se a exceção não for tratada
  (ponto de atenção — não há `finally`).
- **Sem `API_GEMINI`:** cliente inicializa sem chave válida → erro na chamada.

## Pós-condições

- Resposta do Gemini reproduzida em áudio (`response/translate.mp3`).
- `ACTION == False` ao final do fluxo bem-sucedido.
- `gesture_cooldown == 20`.

## Observações

- É o único dos cinco fluxos que **não** envolve mídia (foto/vídeo) nem upload.
- O som de confirmação reaproveitado é o de vídeo (`video_starter.wav`) — não há
  som dedicado de captura de áudio no fluxo executado (`audio_starter.wav` existe
  mas não é usado aqui).

## Requisitos relacionados

- [[RF-003_Pergunta_Voz_Resposta_Falada|RF-003 · Pergunta por voz com resposta falada]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007 · Resposta falada com persona Jarvis]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008 · Debounce, cooldown e trava de ação]]

## Referências

- [[Mapa_Gestos|Mapa de gestos]]
- [[Ref_SpeechRecognition|Referência: SpeechRecognition]]
- [[Ref_Google_Gemini_API|Referência: Google Gemini API]]
- [[Ref_Edge_TTS|Referência: edge-tts]]
- [[Ref_Pygame_Mixer|Referência: pygame.mixer]]
- [[Arquitetura_Software|Arquitetura do software]]
