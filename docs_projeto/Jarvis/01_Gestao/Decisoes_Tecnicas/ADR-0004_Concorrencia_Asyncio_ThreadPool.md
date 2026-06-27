---
title: ADR-0004 · asyncio + ThreadPoolExecutor no loop de camera
id: ADR-0004
type: adr
status: aceito
deciders: [Andre Moreira]
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 01_Gestao
tags: [adr, decisao-tecnica, tema/concorrencia, layer/software]
---

# ADR-0004 · asyncio + ThreadPoolExecutor no loop de camera

## Contexto

O loop principal vive em [main.py](../../../../main.py) e precisa ler frames da camera
(`cv2.VideoCapture(0)`), rodar a deteccao de mao (MediaPipe) e exibir a janela
(`cv2.imshow`) a cada frame, sem travar a UI. Ao mesmo tempo, as acoes disparadas por
gesto sao **pesadas e bloqueantes**: gravar video em loop, capturar audio do microfone
(com `adjust_for_ambient_noise` de 2s e `listen` com timeout), chamar a API do Gemini e
fazer upload para o Google Photos.

As forcas em jogo:

- O loop de visao precisa manter taxa de frames estavel (cada `cap.read()` deve voltar
  rapido) — qualquer bloqueio congela a imagem.
- As acoes do [Jarvis](../../../../jarvis.py) sao escritas como corrotinas `async`
  (`Text_To_Text`, `Image_To_Text`, `Video_To_Text`, `Translate`) por causa do
  `edge-tts` e do `pygame.mixer` (que usa `await asyncio.sleep` para aguardar a duracao
  do audio).
- O codigo de captura ([control.py](../../../../control.py)) e majoritariamente
  **sincrono e bloqueante** (OpenCV, `speech_recognition`, `requests`).
- O alvo e um Raspberry Pi 3 (ver [[ADR-0007_Alvo_Raspberry_Pi3]]), com CPU limitada —
  o overhead de concorrencia precisa ser baixo.

## Decisao

Adotar um modelo **hibrido** de concorrencia:

1. **Loop `asyncio` na `main()`.** A entrada e `asyncio.run(main())`. Os construtores
   sincronos `hands.Hands()` e `control.Control()` (que carregam MediaPipe e inicializam
   o `pygame.mixer`) sao executados fora da thread do event loop via
   `loop.run_in_executor` dentro de `init_hands()` / `init_control()`, paralelizados com
   `asyncio.gather`, para nao bloquear a inicializacao do loop.

2. **Acoes pesadas em `ThreadPoolExecutor`.** Dentro do `with ThreadPoolExecutor() as
   executor:`, cada gesto reconhecido dispara a acao correspondente com
   `executor.submit(...)`, devolvendo o controle imediatamente ao loop de frames.

3. **`asyncio.run(...)` dentro da thread.** As acoes sincronas que precisam chamar o
   codigo `async` do Jarvis criam um event loop proprio na thread worker com
   `asyncio.run(self.jarvis_system.Text_To_Text(prompt))` (e analogos). Cada thread tem
   seu loop isolado, distinto do loop principal da `main()`.

4. **Trava global `ACTION` (bool).** `Control.ACTION` impede acoes concorrentes: o loop
   so avalia gestos quando `control_functions.ACTION == False`. As acoes que conversam
   com o Jarvis setam `ACTION = True` no inicio e `False` no fim, serializando o uso da
   IA, do microfone e do alto-falante.

5. **Debounce por `gesture_cooldown` (frames).** Variavel global em `main.py`,
   decrementada 1 a cada frame. Quando um gesto e aceito, recebe o valor de cooldown da
   tupla em `checks` (Ok=20, Positivo=30, Speak=20, Squid=20, Rock=20). Enquanto
   `gesture_cooldown > 0`, nenhum gesto e reavaliado — evita disparos repetidos do mesmo
   gesto em frames consecutivos.

### Quirk documentado: `Control_Video` alterna em TODO gesto

Em `Check_Gesture`, quando um gesto e aceito e o `state == "Async"` (que e o caso de
**todos** os checks atuais), executa-se:

```python
control_functions.Control_Video = not control_functions.Control_Video
func_exe()
```

Ou seja, a flag `Control_Video` — que controla o loop `while self.Control_Video:` da
gravacao em `Capture_Video` — e **invertida a cada acao disparada**, nao apenas no gesto
de video (Positivo). Consequencia pratica: a gravacao so roda enquanto a flag estiver
`True`; como qualquer gesto a alterna, o estado de gravacao depende da paridade
(numero par/impar) de gestos disparados ate ali. Isso e um efeito colateral fragil e
implicito, candidato a refatoracao (separar o toggle de video do disparo dos demais
gestos). Ver [[RF-008_Debounce_Cooldown_E_Trava_Acao]].

## Alternativas consideradas

- **`multiprocessing`** — isolaria as acoes em processos separados (sem GIL para CPU).
  Rejeitada: custo de serializar frames/handles de camera entre processos, maior consumo
  de RAM (critico no RPi3) e complexidade de IPC desproporcional ao ganho, ja que o
  gargalo das acoes e I/O (rede, audio), nao CPU.
- **Fila de eventos / produtor-consumidor** — uma `queue.Queue` (ou `asyncio.Queue`)
  recebendo eventos de gesto e workers consumindo. Mais limpa e elimina o quirk do
  toggle, mas adiciona uma camada de orquestracao que o projeto atual nao tem. Fica
  registrada como evolucao recomendada no [[Roadmap_Jarvis]].
- **Somente `threading` puro (sem asyncio)** — usar apenas threads e callbacks. Rejeitada
  porque o Jarvis ja e escrito em `async` (edge-tts/pygame com `await`), e converter tudo
  para sincrono perderia a ergonomia das corrotinas e exigiria reescrever o cliente da IA.

## Consequencias

### Positivas
- Loop de visao permanece responsivo: acoes longas nao congelam a janela do OpenCV.
- Reaproveita o codigo `async` do Jarvis sem reescreve-lo.
- `ACTION` + `gesture_cooldown` dao um controle de concorrencia simples e legivel, sem
  locks explicitos.
- Baixo overhead — adequado ao RPi3 (ver [[ADR-0007_Alvo_Raspberry_Pi3]]).

### Negativas / riscos
- **Dois niveis de event loop**: o loop da `main()` e os `asyncio.run(...)` criados nas
  threads. Confunde e dificulta debugar; `asyncio.run` cria/destroi um loop a cada acao.
- **`ACTION` nao e thread-safe de fato**: e um `bool` lido/escrito sem lock. Janelas de
  corrida sao curtas mas existem (duas threads poderiam passar pelo `if ACTION == False`).
- **Bloqueio dentro das threads**: `Video_To_Text` usa `time.sleep(10)` bloqueante no
  polling do upload do video (o proprio codigo comenta "Bomba, precisa ser limpo").
  Prende uma thread do pool por dezenas de segundos.
- **Quirk do `Control_Video`**: estado de gravacao acoplado a paridade de gestos
  (ver acima) — comportamento nao intuitivo e fonte provavel de bugs.
- Estado global espalhado (`gesture_cooldown` em `main.py`, `ACTION`/`Control_Video` no
  `Control`) dificulta testar isoladamente.

## Referencias

- [[Arquitetura_Software]] — visao geral do fluxo e das classes
- [[RF-008_Debounce_Cooldown_E_Trava_Acao]] — requisito de debounce e trava de acao
- [[ADR-0006_Arquitetura_Classe_Por_Arquivo]] — separacao de responsabilidades por classe
- [[ADR-0007_Alvo_Raspberry_Pi3]] — restricoes de hardware que motivam o modelo leve
- [[Roadmap_Jarvis]] — evolucoes propostas (fila de eventos, remover bloqueios)
