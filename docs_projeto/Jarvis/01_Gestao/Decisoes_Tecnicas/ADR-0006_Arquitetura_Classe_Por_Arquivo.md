---
title: ADR-0006 · Uma classe por arquivo e cadeia Control->Jarvis+Manager
id: ADR-0006
type: adr
status: aceito
deciders: [Andre Moreira]
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 01_Gestao
tags: [adr, decisao-tecnica, tema/arquitetura, layer/software]
---

# ADR-0006 · Uma classe por arquivo e cadeia Control->Jarvis+Manager

## Contexto

O Jarvis tem responsabilidades bem distintas no fluxo por frame: capturar imagem
(OpenCV), detectar mao e reconhecer gestos (MediaPipe), orquestrar acoes, conversar com
a IA (Gemini + TTS) e fazer upload (Google Photos). E preciso uma organizacao de codigo
que mantenha essas responsabilidades separadas, fique facil de navegar para um projeto
academico/pessoal e nao introduza camadas de abstracao desproporcionais ao tamanho do
sistema.

Forcas em jogo:

- Projeto pequeno, sem suite de testes nem linter — a clareza visual importa mais que
  abstracoes elaboradas.
- O alvo e o RPi3 (ver [[ADR-0007_Alvo_Raspberry_Pi3]]): sobra pouco para frameworks.
- A documentacao (este repo) precisa mapear arquivo -> classe -> papel de forma direta.

## Decisao

Adotar **uma classe por arquivo**, cada classe com um papel unico, instanciadas em
cadeia a partir do `Control`:

| Arquivo | Classe | Papel |
|---|---|---|
| [main.py](../../../../main.py) | — | Loop `asyncio` da camera; percorre `checks` e dispara acoes via `ThreadPoolExecutor`. So o loop, sem regra de negocio. |
| [hands.py](../../../../hands.py) | `Hands` | Wrapper do MediaPipe Hands; cada `Map_*` retorna `True` para a pose detectada (geometria dos 21 landmarks). Isola toda a dependencia do MediaPipe. |
| [control.py](../../../../control.py) | `Control` | Orquestra as acoes (foto/video/audio), toca sons de confirmacao e encadeia os fluxos. Instancia `Jarvis` e `Manager`. |
| [jarvis.py](../../../../jarvis.py) | `Jarvis` | Cliente do Gemini com persona PT-BR; converte resposta em fala (edge-tts) e toca (pygame). |
| [manager.py](../../../../manager.py) | `Manager` | Upload de midia para o Google Photos via OAuth2. |
| [ProjectConfig.py](../../../../ProjectConfig.py) | — | Bootstrap de pastas e `.env`. |

**Cadeia de instanciacao.** `Control.__init__` cria `self.jarvis_system = jarvis.Jarvis(mixer)`
e `self.menager_system = manager.Manager()`. A `main()` instancia `Hands` e `Control`
(via `run_in_executor`). Assim, o grafo de dependencia e linear e explicito:

```
main  ──cria──>  Hands
main  ──cria──>  Control  ──cria──>  Jarvis
                          ──cria──>  Manager
```

O `Control` e o unico ponto que conhece tanto a IA quanto o upload; `Hands` nao conhece
ninguem alem do MediaPipe; `main` so conhece `Hands` e `Control`.

## Alternativas consideradas

- **Monolito (tudo em um arquivo)** — simples de comecar, mas mistura visao, IA, upload e
  loop num so lugar, dificultando leitura e a documentacao por modulo. Rejeitada.
- **Arquitetura por camadas formal** (dominio / aplicacao / infraestrutura, com
  interfaces e injecao de dependencia) — robusta e testavel, mas pesada demais para o
  tamanho do projeto e para o RPi3. Adiada; registrada como evolucao possivel no
  [[Roadmap_Jarvis]] se o sistema crescer.
- **Arquitetura orientada a eventos** (barramento/fila desacoplando captura de acao) —
  resolveria o acoplamento do `Control` e o quirk de concorrencia
  (ver [[ADR-0004_Concorrencia_Asyncio_ThreadPool]]), mas introduz infra que ainda nao se
  justifica. Mantida como direcao futura.

## Consequencias

### Positivas
- Mapa mental imediato: 1 arquivo = 1 responsabilidade = 1 classe.
- A documentacao em [[Referencia_Modulos]] espelha 1:1 a estrutura de arquivos.
- `Hands` isola o MediaPipe e `Manager` isola o Google Photos — trocar qualquer um afeta
  so o seu arquivo.
- `main` fica enxuto (apenas o loop), facilitando entender o fluxo principal.

### Negativas / riscos
- **`Control` concentra acoplamento**: conhece `Hands` (indiretamente, via os resultados),
  `Jarvis`, `Manager`, OpenCV, `speech_recognition` e o `pygame.mixer`. Tende a virar um
  ponto de inchaco (varias responsabilidades de captura + orquestracao no mesmo lugar).
- **Estado global e de instancia espalhado**: `gesture_cooldown` (global em `main.py`),
  `ACTION` e `Control_Video` (atributos do `Control`) acoplam o loop ao orquestrador e
  dificultam testar isoladamente.
- **Sem interfaces/inversao de dependencia**: as classes se referenciam concretamente
  (`jarvis.Jarvis`, `manager.Manager`), entao mockar para teste exige patch de modulo.
- Acoplamento de construcao: instanciar `Control` ja inicializa Gemini, mixer e prepara
  OAuth — efeitos colaterais pesados no `__init__`.

## Referencias

- [[Arquitetura_Software]] — diagrama e fluxo por frame
- [[Referencia_Modulos]] — tabela arquivo -> classe -> papel
- [[ADR-0004_Concorrencia_Asyncio_ThreadPool]] — concorrencia e estado global
- [[ADR-0001_MediaPipe_Hands]] — isolamento do MediaPipe na classe `Hands`
- [[ADR-0002_Gemini_Multimodal]] — cliente de IA na classe `Jarvis`
- [[ADR-0005_Upload_Google_Photos_OAuth]] — upload na classe `Manager`
