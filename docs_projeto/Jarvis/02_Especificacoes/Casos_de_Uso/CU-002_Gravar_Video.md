---
title: CU-002 · Gravar vídeo com o gesto positivo
id: CU-002
type: caso-de-uso
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
prioridade: alta
tags: [module/software, layer/especificacao, tema/gestos, prio/alta]
---

# CU-002 · Gravar vídeo com o gesto positivo

Inicia (e, no gesto seguinte, encerra) a gravação de vídeo ao reconhecer o gesto
**positivo / joinha** com a **mão esquerda**. Ao parar, faz upload do `.avi` para
o Google Photos.

## Ator

- **Usuário** dos óculos inteligentes.

## Pré-condições

- App `main.py` rodando, câmera aberta.
- Mão detectada pelo MediaPipe no frame.
- `Control.ACTION == False` e `gesture_cooldown == 0`.
- Pasta `midia/` existente.

## Gesto disparador

| Atributo | Valor |
|---|---|
| Método | `Hands.Map_Positive` |
| Mão exigida | Esquerda (`Left`) |
| Cooldown | 30 frames |
| Estado (`state`) | `Async` |
| Ação | `Control.Capture_Video(cap, executor)` |

**Geometria (Map_Positive):** polegar levantado acima da base
(`polegar_4_y < polegar_1_y - 0.05 * h`) e os quatro dedos dobrados — indicador
(`indicador_8_y > indicador_5_y`), médio (`medio_12_y > medio_9_y`), anelar
(`anelar_16_y > anelar_13_y`) e mindinho (`mindinho_20_y > mindinho_17_y`).

## Fluxo principal

> A gravação depende da flag `Control_Video`, que é **alternada (toggle)** em todo
> gesto `Async` por `Check_Gesture` (`Control_Video = not Control_Video`). O gesto
> positivo é o disparador natural do par liga/desliga.

1. `Check_Gesture` confirma `Map_Positive == True` e `hand_label == "Left"`.
2. `gesture_cooldown = 30`; alterna `Control_Video` (ex.: `False → True`).
3. Submete `Capture_Video(cap, executor)` ao executor.
4. `Capture_Video`:
   - cria `cv2.VideoWriter` (codec `XVID`, `midia/<timestamp>.avi`, `fps=30`,
     resolução `640x480`);
   - toca `audios_check/video_starter.wav`;
   - **loop** `while self.Control_Video:` lê frames de `cap` e escreve no arquivo;
   - quando `Control_Video` volta a `False` (próximo gesto que faz toggle), sai do
     loop, faz `out.release()`;
   - toca `audios_check/video_out.wav`;
   - submete `uploadMidia(<caminho .avi>)` ao executor;
   - retorna o caminho do vídeo.

## Fluxos alternativos e de erro

- **Mão errada:** gesto na mão direita → não dispara.
- **Ação em curso / cooldown:** `ACTION == True` ou `gesture_cooldown > 0` → ignora.
- **Parada da gravação:** qualquer gesto `Async` subsequente alterna `Control_Video`
  para `False` e encerra o loop — não é necessário repetir exatamente o gesto
  positivo (efeito do toggle global). Esse acoplamento é um ponto de atenção
  conhecido.
- **Falha de leitura no loop:** `cap.read()` pode retornar `status == False`;
  `out.write(frame)` é chamado mesmo assim (sem checagem de `status`).
- **Quirk de upload:** `uploadMidia` envia header `Content-Type: image/jpeg` mesmo
  para um arquivo `.avi` — o Google Photos pode rejeitar o vídeo. Ver
  [[BUG-001_Video_Audio_Sem_Executor]] e notas no [[Mapa_Gestos]].
- **Falha de upload:** status ≠ 200 → `raise_for_status()` na thread; o `.avi`
  local permanece salvo.

## Pós-condições

- Arquivo `midia/<timestamp>.avi` gravado enquanto `Control_Video == True`.
- Sons de início (`video_starter.wav`) e fim (`video_out.wav`) reproduzidos.
- Upload do vídeo disparado em background (sujeito ao quirk de MIME).
- `gesture_cooldown == 30`.

## Observações

- A gravação ocupa uma thread do `ThreadPoolExecutor` durante todo o intervalo —
  enquanto grava, `Capture_Video` segura o frame loop interno.
- `Capture_Video` não usa `ACTION`; o controle de início/fim é pela flag
  `Control_Video`.

## Requisitos relacionados

- [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002 · Gravação de vídeo com gesto positivo]]
- [[RF-009_Upload_Automatico_Google_Photos|RF-009 · Upload automático para o Google Photos]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008 · Debounce, cooldown e trava de ação]]

## Referências

- [[Mapa_Gestos|Mapa de gestos]]
- [[CU-005_Analisar_Video_Com_Pergunta|CU-005 · Vídeo + pergunta]]
- [[Ref_OpenCV|Referência: OpenCV]]
- [[Ref_Google_Photos_API|Referência: Google Photos API]]
- [[Arquitetura_Software|Arquitetura do software]]
