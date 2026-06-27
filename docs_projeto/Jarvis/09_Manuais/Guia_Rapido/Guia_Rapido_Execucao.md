---
title: Guia Rapido de Execucao do Jarvis
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 09_Manuais
categoria: manual
tags:
  - manual
  - guia
  - module/software
  - layer/manual
---

# Guia Rapido de Execucao do Jarvis

Quickstart de uma pagina para colocar o Jarvis (oculos inteligentes, controle por gestos) para rodar. Para a instalacao detalhada das bibliotecas, ver [[Instalacao_Dependencias]]; para resolver erros, ver [[Troubleshooting_Jarvis]].

> Rode **sempre a partir da raiz do repositorio**. O entry point e **`python main.py`** — nao `jarvis.py` (este so define a classe). Ver [[FAQ_Jarvis]].

## Passo a passo

### 1. Instalar dependencias

```powershell
pip install -r requirements.txt
```

**Ressalva:** o `requirements.txt` contem pseudo-pacotes da stdlib (`time`, `os`, `pathlib`) e o nome generico `google`, que podem **quebrar** o `pip install`. Se falhar, instale manualmente as dependencias reais — ver [[Instalacao_Dependencias]].

### 2. Bootstrap das pastas (rode uma vez)

```powershell
python ProjectConfig.py
```

Cria `response/` e `midia/` e um `.env` vazio. E idempotente (`os.makedirs(..., exist_ok=True)` + guard de `__main__`): rodar de novo nao quebra nem sobrescreve.

### 3. Configurar segredos

| Item | Onde | Para que serve |
|---|---|---|
| `API_GEMINI=<sua_chave>` | `.env` (raiz) | Acesso ao Google Gemini (IA). |
| `client_secret.json` | `env/client_secret.json` | OAuth desktop do Google Photos (upload). |

No primeiro upload, o fluxo OAuth abre o navegador e gera `env/token.json` automaticamente. Ver [[ADR-0005_Upload_Google_Photos_OAuth]].

### 4. Rodar o app

```powershell
python main.py
```

Abre a janela "MediaPipe Hands" com a visao da camera (`cv2.VideoCapture(0)`). Faca os gestos diante da camera.

### 5. Operar por gestos

Veja a tabela abaixo. Cada gesto exige a mao indicada e respeita um debounce em frames (`gesture_cooldown`); enquanto uma acao roda, a trava `ACTION` impede disparar outra. Ver [[RF-008_Debounce_Cooldown_E_Trava_Acao]].

### 6. Sair

Com a janela do OpenCV em foco, tecle **`q`**. O app libera a camera e fecha as janelas.

## Tabela rapida: gesto -> acao

| Gesto (`Hands.Map_*`) | Mao | Acao (`Control`) | O que acontece |
|---|---|---|---|
| OK / pinca (`Map_Ok`) | Direita | `Capture_Photo` | Tira foto (`midia/<ts>.jpg`) + sobe pro Google Photos |
| Joinha / positivo (`Map_Positive`) | Esquerda | `Capture_Video` | Grava video (`midia/<ts>.avi`) enquanto a gravacao estiver ligada |
| Dedo levantado (`Map_Speak`) | Direita | `Audio_to_Audio` | Pergunta por voz -> Gemini -> resposta falada |
| "L" (`Map_Squid`) | Esquerda | `Image_Audio` | Foto + pergunta por voz -> Gemini |
| Rock (`Map_Rock`) | Direita | `Video_Audio` | Video + pergunta por voz -> Gemini |

> Quirk: todo gesto disparado faz **toggle** de `Control_Video`, entao a flag de gravacao alterna a cada acao. Ver [[RF-002_Gravacao_Video_Gesto_Positivo]]. O gesto Rock atualmente tem um bug ([[BUG-001_Video_Audio_Sem_Executor]]).

## Referencias

- [[Instalacao_Dependencias|Instalacao de dependencias]]
- [[Troubleshooting_Jarvis|Troubleshooting do Jarvis]]
- [[FAQ_Jarvis|FAQ do Jarvis]]
- [[Mapa_Gestos|Mapa de gestos]]
- [[RF-006_Reconhecimento_Cinco_Gestos|RF-006: reconhecimento de cinco gestos]]
- [[Arquitetura_Software|Arquitetura do software]]
