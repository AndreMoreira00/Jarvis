---
title: CU-001 · Tirar foto com o gesto OK
id: CU-001
type: caso-de-uso
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
prioridade: alta
tags: [module/software, layer/especificacao, tema/gestos, prio/alta]
---

# CU-001 · Tirar foto com o gesto OK

Captura uma foto do campo de visão da câmera ao reconhecer o gesto **OK** (pinça
polegar + indicador) com a **mão direita**, toca o som de confirmação e envia a
imagem para o Google Photos de forma assíncrona.

## Ator

- **Usuário** dos óculos inteligentes (operação hands-free, sem toque).

## Pré-condições

- O app `main.py` está rodando com a câmera (`cv2.VideoCapture(0)`) aberta.
- O MediaPipe detecta ao menos uma mão no frame (`multi_hand_landmarks` e
  `multi_handedness` presentes).
- A trava global `Control.ACTION == False` (nenhuma outra ação em curso).
- O debounce global `gesture_cooldown == 0`.
- A pasta `midia/` existe (criada por `ProjectConfig.py`).
- Para o upload: `env/client_secret.json` configurado (OAuth) — opcional para a
  captura em si, obrigatório para a etapa de envio.

## Gesto disparador

| Atributo | Valor |
|---|---|
| Método | `Hands.Map_Ok` |
| Mão exigida | Direita (`Right`) |
| Cooldown | 20 frames |
| Estado (`state`) | `Async` |
| Ação | `Control.Capture_Photo(frame, executor)` |

**Geometria (Map_Ok):** distância euclidiana entre a ponta do polegar (landmark 4)
e a ponta do indicador (landmark 8) menor que `0.05 * w` (pinça fechada), com o
indicador dobrado (`indicador_5_y > indicador_6_y`), polegar abaixo da articulação
do indicador (`polegar_1_y > indicador_6_y`) e polegar lateralizado
(`polegar_3_x > indicador_5_x`).

## Fluxo principal

1. A cada frame, `main.py` converte BGR→RGB e roda `hands.process(rgb)`.
2. Para cada mão, lê `hand_label` (`Right`/`Left`) e percorre a lista `checks`.
3. Com `ACTION == False` e `gesture_cooldown == 0`, chama `Check_Gesture` para o
   item do `Map_Ok`.
4. `Map_Ok` retorna `True` **e** `hand_label == "Right"`:
   - `gesture_cooldown = 20`;
   - como `state == "Async"`, alterna a flag `Control.Control_Video` (ver
     [[#observações|observações]]);
   - dispara `func_exe()`, que submete `Capture_Photo(frame, executor)` ao
     `ThreadPoolExecutor`.
5. `Capture_Photo`:
   - gera timestamp `%Y%m%d_%H%M%S`;
   - grava `midia/<timestamp>.jpg` via `cv2.imwrite`;
   - toca `audios_check/photo_take.wav` (`play_confirmation_sound`);
   - submete `menager_system.uploadMidia(<caminho>)` ao executor (upload em
     background);
   - retorna o caminho da foto.
6. `Manager.uploadMidia` autentica (OAuth), faz `POST /v1/uploads` (raw) e
   `mediaItems:batchCreate` com o `uploadToken` e o `fileName`.

## Fluxos alternativos e de erro

- **Gesto na mão errada:** `Map_Ok` verdadeiro mas `hand_label == "Left"` →
  `Check_Gesture` não dispara nada.
- **Ação já em curso:** `ACTION == True` → o frame é ignorado para disparo.
- **Cooldown ativo:** `gesture_cooldown > 0` → ignora até zerar (evita rajada de
  fotos).
- **Frame inválido:** `cap.read()` retorna `ret == False` → `main` imprime erro e
  encerra o loop.
- **Falha de upload:** `uploadMidia` recebe status ≠ 200 → `response.raise_for_status()`
  levanta exceção na thread do executor. A foto local **já foi salva**.
- **Quirk do MIME:** o upload envia sempre `image/jpeg` — para foto está correto.

## Pós-condições

- Arquivo `midia/<timestamp>.jpg` salvo em disco.
- Som `photo_take.wav` reproduzido como confirmação.
- Upload para o Google Photos disparado em background (best-effort).
- `gesture_cooldown == 20` (decai 1 por frame).

## Observações

- `Capture_Photo` **não** seta `ACTION = True`; a proteção contra disparo repetido
  vem apenas do `gesture_cooldown`.
- `Check_Gesture` alterna `Control_Video` em **qualquer** gesto `Async` — efeito
  colateral irrelevante para a foto, mas relevante para o vídeo (ver
  [[CU-002_Gravar_Video]]).

## Requisitos relacionados

- [[RF-001_Captura_Foto_Gesto_Ok|RF-001 · Captura de foto com gesto OK]]
- [[RF-009_Upload_Automatico_Google_Photos|RF-009 · Upload automático para o Google Photos]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008 · Debounce, cooldown e trava de ação]]

## Referências

- [[Mapa_Gestos|Mapa de gestos]]
- [[CU-004_Analisar_Imagem_Com_Pergunta|CU-004 · Foto + pergunta]]
- [[Ref_OpenCV|Referência: OpenCV]]
- [[Ref_Google_Photos_API|Referência: Google Photos API]]
- [[Arquitetura_Software|Arquitetura do software]]
