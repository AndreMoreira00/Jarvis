---
title: FAQ do Jarvis
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 12_Suporte_PosVenda
categoria: suporte
tags:
  - faq
  - suporte
  - module/software
  - layer/suporte
---

# FAQ do Jarvis

Perguntas frequentes sobre operacao do Jarvis (oculos inteligentes, controle por gestos, alvo Raspberry Pi 3). Para diagnostico de erros, ver [[Troubleshooting_Jarvis]]; para operar passo a passo, ver [[Guia_Rapido_Execucao]].

## Como eu rodo o Jarvis?

A partir da **raiz do repositorio**:

1. `pip install -r requirements.txt` (com ressalva — ver [[Instalacao_Dependencias]]).
2. `python ProjectConfig.py` uma vez (cria `response/`, `midia/` e um `.env` vazio; idempotente).
3. Configure o `.env` com `API_GEMINI=<sua_chave>` e coloque `env/client_secret.json` para o Google Photos.
4. `python main.py`.

Detalhes em [[Guia_Rapido_Execucao]].

## Por que `python jarvis.py` nao inicia o programa?

Porque `jarvis.py` **so define a classe `Jarvis`** (cliente do Gemini + TTS); ele nao tem bloco `if __name__ == "__main__"`. O entry point real e `main.py`, que contem o loop `asyncio` da camera. O README da raiz cita `jarvis.py` e esta desatualizado nesse ponto. Use **`python main.py`**.

## Preciso de internet?

Sim, para os fluxos de IA, voz e upload:

- **Reconhecimento de voz** (STT) usa `recognize_google` (online).
- **IA** usa o Google Gemini (`gemini-2.0-flash-lite`).
- **TTS** usa `edge-tts` (voz `pt-BR-AntonioNeural`), que baixa o audio.
- **Upload** envia midia para o Google Photos.

A deteccao de gestos (MediaPipe) roda localmente, mas qualquer acao que envolva IA/voz/upload exige conexao. Ver [[RNF-006_Dependencia_Conectividade]].

## Como eu saio do programa?

Com a janela do OpenCV ("MediaPipe Hands") em foco, tecle **`q`**. O loop encerra, libera a camera (`cap.release()`) e fecha as janelas (`cv2.destroyAllWindows()`).

## Onde ficam as fotos e os videos?

Na pasta **`midia/`** na raiz do repo, nomeados por timestamp `%Y%m%d_%H%M%S`:

- Fotos: `midia/<timestamp>.jpg`.
- Videos: `midia/<timestamp>.avi` (codec XVID, 30 fps, 640x480).

Apos a captura, a midia tambem e enviada ao **Google Photos** (se o OAuth estiver configurado). A resposta falada do Jarvis e salva em `response/translate.mp3`.

## Quais gestos existem e o que cada um faz?

| Gesto | Mao | Acao |
|---|---|---|
| OK / pinca | Direita | Tira foto e sobe pro Google Photos |
| Joinha / positivo | Esquerda | Grava video enquanto a gravacao estiver ligada |
| Dedo levantado | Direita | Pergunta por voz -> Gemini -> resposta falada |
| "L" | Esquerda | Foto + pergunta por voz -> Gemini |
| Rock | Direita | Video + pergunta por voz -> Gemini |

Detalhes da geometria em [[Mapa_Gestos]] e [[RF-006_Reconhecimento_Cinco_Gestos]].

## Qual modelo de IA o Jarvis usa?

O **Google Gemini `gemini-2.0-flash-lite`**, multimodal (texto, imagem e video), com uma `system_instruction` que define a persona PT-BR (a IA "Jarvis" trata o usuario como "Mestre", foco em programacao, ML, ciencia de dados e visao computacional). Ver [[ADR-0002_Gemini_Multimodal]] e [[RF-007_Resposta_Falada_Persona_Jarvis]].

## Em qual idioma o Jarvis funciona?

**Portugues do Brasil (pt-BR)** de ponta a ponta:

- STT: `recognize_google(language="pt-BR")`.
- IA: persona e respostas em PT-BR.
- TTS: voz `pt-BR-AntonioNeural`.

Ver [[RNF-003_Idioma_PT_BR]].

## A IA guarda meus dados? Onde?

Fotos/videos vao para a sua conta do **Google Photos** (via OAuth) e arquivos enviados ao Gemini sao apagados ao final do fluxo de video (`Delete_Cahche_Files`). Consideracoes de privacidade em [[RNF-005_Privacidade_Dados_Nuvem]].

## Referencias

- [[Guia_Rapido_Execucao|Guia rapido de execucao]]
- [[Instalacao_Dependencias|Instalacao de dependencias]]
- [[Troubleshooting_Jarvis|Troubleshooting do Jarvis]]
- [[Mapa_Gestos|Mapa de gestos]]
- [[RNF-003_Idioma_PT_BR|RNF-003: idioma PT-BR]]
- [[RNF-006_Dependencia_Conectividade|RNF-006: dependencia de conectividade]]
- [[ADR-0002_Gemini_Multimodal|ADR-0002: Gemini multimodal]]
