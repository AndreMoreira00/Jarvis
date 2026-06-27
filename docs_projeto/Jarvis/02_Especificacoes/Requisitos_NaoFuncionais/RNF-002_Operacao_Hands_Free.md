---
title: RNF-002 · Operacao hands-free (gestos e voz)
type: requisito
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
id: RNF-002
module: 02_Especificacoes
categoria: nao-funcional
prioridade: alta
tags: [requisito, layer/especificacao, prio/alta, tema/gestos, tema/usabilidade]
---

# RNF-002 · Operacao hands-free (gestos e voz)

## Descricao

Toda a interacao com o Jarvis deve ser **hands-free**: o usuario controla o sistema
por **gestos de mao** (detectados por MediaPipe) e por **voz** (perguntas faladas),
sem teclado, mouse ou toque. O produto e um par de oculos — nao ha tela tatil nem
periferico de entrada classico.

## Justificativa

A natureza do dispositivo (oculos inteligentes vestiveis) exige que as maos do
usuario fiquem livres. Os cinco gestos reconhecidos ([[RF-006_Reconhecimento_Cinco_Gestos|RF-006]])
e a captura de voz ([[control.py]], `Capture_Audio`) cobrem todas as acoes
disponiveis. Ver mapa completo em [[Mapa_Gestos]].

## Criterios de aceitacao

| # | Criterio | Status no codigo |
|---|----------|------------------|
| 1 | Todas as acoes sao disparadas por gesto | atendido — lista `checks` em [[main.py]] mapeia 5 gestos para 5 acoes |
| 2 | A entrada de perguntas e por voz (STT pt-BR) | atendido — `Capture_Audio` usa `recognize_google(language="pt-BR")` |
| 3 | Nenhuma acao exige teclado/mouse | atendido para as acoes; ver excecao abaixo |
| 4 | A saida e por audio (TTS), sem leitura de tela | atendido — ver [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007]] |

## Excecao conhecida (prototipo)

No prototipo desktop, a **tecla `q`** encerra o app (`cv2.waitKey(1) & 0xFF == ord('q')`
em [[main.py]]). Esse e o **unico** ponto de entrada por teclado e existe apenas para
encerrar a janela do OpenCV durante o desenvolvimento. No produto final (oculos sem
teclado) o encerramento deve migrar para um gesto dedicado, um botao fisico ou
comando de voz — **a definir** (sugestao: registrar como item de roadmap em
[[Roadmap_Jarvis]]).

## Riscos

- Robustez do reconhecimento de gestos sob iluminacao/angulo variaveis impacta a
  usabilidade hands-free (ver [[TP-001_Validacao_Reconhecimento_Gestos|TP-001]]).
- O quirk de toggle de `Control_Video` em qualquer gesto ([[main.py]], `Check_Gesture`)
  pode confundir o controle hands-free de gravacao (ver [[RF-002_Gravacao_Video_Gesto_Positivo|RF-002]]).

## Referencias

- [[RF-006_Reconhecimento_Cinco_Gestos|RF-006 · Reconhecimento de 5 gestos]]
- [[RNF-003_Idioma_PT_BR|RNF-003 · Idioma pt-BR]]
- [[Mapa_Gestos]]
- [[CU-003_Perguntar_Por_Voz|CU-003 · Perguntar por voz]]
- [[Roadmap_Jarvis]]
