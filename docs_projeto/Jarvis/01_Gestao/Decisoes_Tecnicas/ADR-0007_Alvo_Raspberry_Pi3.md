---
title: ADR-0007 · Raspberry Pi 3 como plataforma alvo
id: ADR-0007
type: adr
status: aceito
deciders: [Andre Moreira]
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 01_Gestao
tags: [adr, decisao-tecnica, tema/hardware, layer/software]
---

# ADR-0007 · Raspberry Pi 3 como plataforma alvo

## Contexto

O Jarvis e o software de um par de **oculos inteligentes** controlados por gestos. O
dispositivo precisa ser pequeno, leve, alimentado por bateria e capaz de embarcar uma
camera, microfone e alto-falante, alem de rodar todo o pipeline de visao + IA + fala.

Forcas em jogo:

- **Pipeline pesado**: por frame, roda OpenCV (captura), MediaPipe Hands (inferencia de
  21 landmarks), reconhecimento geometrico de gesto e, sob demanda, chamadas a IA e TTS.
- **Forma e peso** importam (montagem nos oculos) — placas grandes ou com dissipacao
  ativa sao indesejaveis.
- **Custo e disponibilidade**: projeto academico/pessoal, hardware acessivel facilita.
- **Ecossistema**: necessidade de Python 3, OpenCV, MediaPipe, drivers de camera/audio e
  rede (para Gemini e Google Photos).

## Decisao

Definir o **Raspberry Pi 3** como plataforma alvo de hardware para os oculos.

Justificativa:

- Placa amplamente disponivel, barata e com vasto suporte de comunidade.
- Roda Linux e Python 3 com OpenCV/MediaPipe; tem GPIO, CSI (camera) e audio.
- Tamanho e consumo compativeis com um wearable alimentado por bateria.
- O design ja **descarrega o trabalho pesado na nuvem** (Gemini para inferencia
  multimodal — ver [[ADR-0002_Gemini_Multimodal]] — e Google Photos para armazenamento —
  ver [[ADR-0005_Upload_Google_Photos_OAuth]]), aliviando a CPU local.

O alvo orienta as decisoes de software: modelo de concorrencia leve
(ver [[ADR-0004_Concorrencia_Asyncio_ThreadPool]]), evitar frameworks pesados
(ver [[ADR-0006_Arquitetura_Classe_Por_Arquivo]]) e manter a resolucao de captura
modesta (video gravado em 640x480, 30fps).

## Alternativas consideradas

- **Raspberry Pi 4 / Pi Zero 2 W** — o Pi 4 tem CPU/RAM melhores (rodaria MediaPipe com
  mais folga), mas e maior, esquenta mais e consome mais bateria; o Zero 2 W e menor e
  mais leve (ideal para wearable), porem com menos margem termica e de I/O. Ambos ficam
  como candidatos de reavaliacao caso o Pi 3 nao atenda a latencia
  (ver [[RNF-004_Latencia_Resposta]]). Registrado no [[Roadmap_Jarvis]].
- **NVIDIA Jetson Nano** — GPU para inferencia local aceleraria o MediaPipe e abriria
  espaco para modelos on-device, mas e maior, mais caro e consome mais energia —
  desproporcional para um wearable cujo pesado ja vai para a nuvem. Rejeitada.
- **Smartphone como host** — hardware abundante, camera/mic/alto-falante integrados e
  conectividade. Rejeitada por nao casar com o conceito de oculos dedicados e por
  amarrar o projeto a um SO movel e suas restricoes de background.

## Consequencias

### Positivas
- Hardware barato, disponivel e bem documentado.
- Forma/peso/consumo adequados a um wearable com bateria.
- Stack Python/OpenCV/MediaPipe roda nativamente.

### Negativas / riscos
- **CPU/RAM limitadas**: MediaPipe Hands a 30fps + OpenCV pode saturar o Pi 3, derrubando
  a taxa de frames e a responsividade dos gestos (ver [[RISCO-001_Desempenho_Raspberry_Pi]]).
- **Dependencia de rede critica**: como o trabalho pesado (IA, upload) vai para a nuvem,
  sem boa conectividade a experiencia degrada (ver [[RNF-006_Dependencia_Conectividade]]).
- **Sem aceleracao de inferencia local**: nao ha GPU util; tudo que nao for offloadado
  compete pela CPU.
- **Termico/energia**: cargas continuas de visao podem aquecer e drenar bateria rapido em
  formato wearable.
- O alvo restringe escolhas de software (concorrencia leve, resolucao modesta) e fixa um
  teto de desempenho que pode exigir migrar de placa no futuro.

## Referencias

- [[RNF-001_Execucao_Raspberry_Pi3]] — requisito de execucao no RPi3
- [[RISCO-001_Desempenho_Raspberry_Pi]] — risco de desempenho do hardware
- [[RNF-004_Latencia_Resposta]] — latencia de resposta esperada
- [[RNF-006_Dependencia_Conectividade]] — dependencia de rede
- [[ADR-0002_Gemini_Multimodal]] — offload da inferencia para a nuvem
- [[ADR-0005_Upload_Google_Photos_OAuth]] — offload do armazenamento
- [[ADR-0004_Concorrencia_Asyncio_ThreadPool]] — concorrencia leve motivada pelo alvo
