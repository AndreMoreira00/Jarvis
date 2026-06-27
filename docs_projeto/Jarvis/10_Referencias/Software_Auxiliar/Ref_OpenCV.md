---
title: OpenCV (cv2)
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 10_Referencias
categoria: visao-computacional
tags: [referencia, biblioteca, module/software, tema/camera]
---

# OpenCV (cv2)

## O que e

Biblioteca de visao computacional e processamento de imagem/video, usada em Python
via o pacote `cv2`. No Jarvis e a **camada de I/O da camera**: captura frames,
converte cores para o MediaPipe, grava fotos/videos em disco e exibe a janela de
preview.

## Como o Jarvis usa

Distribuida entre [main.py](main.py), [control.py](control.py) e [hands.py](hands.py).

| Funcao cv2 | Onde | Para que |
|---|---|---|
| `VideoCapture(0)` | [main.py](main.py) | Abre a camera padrao (indice 0) |
| `cap.read()` | [main.py](main.py), [control.py](control.py) | Le um frame (`ret, frame`) |
| `cvtColor(frame, COLOR_BGR2RGB)` | [main.py](main.py) | Converte BGR->RGB para o MediaPipe |
| `imwrite("midia/{ts}.jpg", frame)` | [control.py](control.py) | Salva foto (`Capture_Photo`) |
| `VideoWriter_fourcc(*"XVID")` | [control.py](control.py) | Codec do video |
| `VideoWriter("midia/{ts}.avi", fourcc, 30, (640,480))` | [control.py](control.py) | Grava video (`Capture_Video`) |
| `out.write(frame)` / `out.release()` | [control.py](control.py) | Escreve frames e fecha o arquivo |
| `imshow("MediaPipe Hands", frame)` | [main.py](main.py) | Janela de preview |
| `waitKey(1) & 0xFF == ord('q')` | [main.py](main.py) | Sair com a tecla `q` |
| `cap.release()` / `destroyAllWindows()` | [main.py](main.py) | Encerramento |

Os frames alimentam o [[Ref_MediaPipe_Hands|MediaPipe Hands]]; as midias gravadas
sobem para o [[Ref_Google_Photos_API|Google Photos]] e/ou viram input do
[[Ref_Google_Gemini_API|Gemini]]. Fluxos em
[[RF-001_Captura_Foto_Gesto_Ok|RF-001]] e
[[RF-002_Gravacao_Video_Gesto_Positivo|RF-002]].

## Pontos de atencao

- **Espaco de cor BGR**: OpenCV usa BGR por padrao; a conversao para RGB e
  obrigatoria antes de `hands.process(...)`, senao a deteccao degrada.
- **Resolucao de video fixa `(640, 480)` e `fps=30`**: se a camera real entregar
  resolucao diferente, frames podem ficar corrompidos ou ser descartados pelo
  `VideoWriter` (ver [[Troubleshooting_Jarvis|Troubleshooting]]).
- **Codec XVID / container `.avi`**: o arquivo gravado e `.avi`, mas o upload ao
  Google Photos manda header `image/jpeg` (quirk do [[manager.py|Manager]]).
- **Indice de camera `0`**: hard-coded; em maquinas com varias cameras pode abrir a
  errada.
- **`waitKey(1)`**: a janela so responde dentro do loop; a UI trava se o loop bloquear.
- **Versao**: pacote `opencv-python`; versao exata **verificar**.

## Link oficial

- https://opencv.org

## Referencias

- [[main.py|Codigo: main.py (loop da camera)]]
- [[control.py|Codigo: control.py (captura/gravacao)]]
- [[RF-001_Captura_Foto_Gesto_Ok|RF-001 — Captura de foto]]
- [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002 — Gravacao de video]]
- [[Ref_MediaPipe_Hands|Referencia: MediaPipe Hands]]
- [[Ref_Google_Photos_API|Referencia: Google Photos API]]
