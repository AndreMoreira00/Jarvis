---
title: Troubleshooting do Jarvis
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 12_Suporte_PosVenda
categoria: suporte
tags:
  - troubleshooting
  - suporte
  - module/software
  - layer/suporte
---

# Troubleshooting do Jarvis

Guia de diagnostico do Jarvis (oculos inteligentes, controle por gestos, alvo Raspberry Pi 3). Organizado como tabela **Sintoma -> Causa provavel -> Acao**, derivado das armadilhas reais do codigo. Para o passo a passo de operacao, ver [[Guia_Rapido_Execucao]]; para instalacao, ver [[Instalacao_Dependencias]].

> Lembrete: rode **sempre a partir da raiz do repositorio** (`python main.py`). O entry point e `main.py`, **nao** `jarvis.py` (este so define a classe `Jarvis`, sem bloco `__main__`). Ver [[FAQ_Jarvis]].

## Inicializacao e ambiente

| Sintoma | Causa provavel | Acao |
|---|---|---|
| `python jarvis.py` nao inicia / nada acontece | `jarvis.py` so define a classe `Jarvis`, nao tem `if __name__ == "__main__"` | Use o entry point correto: `python main.py`. O README da raiz esta desatualizado nesse ponto. |
| `FileNotFoundError` em `midia/{...}.jpg`, `response/translate.mp3` ou nos sons de `audios_check/` | App rodado fora da raiz do repo (paths relativos) e/ou pastas `response/`/`midia/` ausentes | Rode da raiz do repo. Crie as pastas com `python ProjectConfig.py` (idempotente: `os.makedirs(..., exist_ok=True)`, nao quebra se ja existirem). |
| `python ProjectConfig.py` "nao faz nada" na segunda execucao | Comportamento esperado: o script e idempotente e tem guard de `__main__` | Sem acao. As pastas/`.env` ja existem; nao recria nem sobrescreve. Historico do bug original (mkdir sem `exist_ok`) em [[BUG-003_ProjectConfig_Mkdir_Sem_ExistOk]]. |
| `pip install -r requirements.txt` falha ("No matching distribution" / pacote inexistente) | `requirements.txt` lista pseudo-pacotes da stdlib (`time`, `os`, `pathlib`) e o nome generico `google`, que quebram a resolucao | Instale manualmente o que faltar (ver [[Instalacao_Dependencias]]). Ignore as entradas da stdlib; `os`/`time`/`pathlib` ja vem com o Python. |

## Configuracao de segredos (IA e upload)

| Sintoma | Causa provavel | Acao |
|---|---|---|
| Sem resposta falada / erro de autenticacao do Gemini | Falta `API_GEMINI` no `.env`; `os.getenv("API_GEMINI")` retorna `None` | Adicione `API_GEMINI=<sua_chave>` ao `.env` na raiz. O `.env` vazio e criado por `ProjectConfig.py`. Ver [[Ref_Google_Gemini_API]]. |
| Upload para o Google Photos falha ao tirar foto/video | Falta `env/client_secret.json` (OAuth desktop) ou `env/token.json` invalido | Coloque o `client_secret.json` em `env/`. No primeiro uso o fluxo OAuth abre o navegador (`run_local_server`) e gera `env/token.json`. Ver [[ADR-0005_Upload_Google_Photos_OAuth]] e [[Ref_Google_Photos_API]]. |
| Foto sobe, mas video `.avi` "nao aparece" corretamente no Photos | `uploadMidia` envia `X-Goog-Upload-Content-Type: image/jpeg` fixo, mesmo para video | Limitacao conhecida do upload. Trate como issue aberta; corrigir o mime-type por extensao do arquivo. Ver [[RF-009_Upload_Automatico_Google_Photos]]. |

## Gestos, camera e microfone

| Sintoma | Causa provavel | Acao |
|---|---|---|
| Janela do OpenCV abre preta / "Erro ao capturar o frame." | `cv2.VideoCapture(0)` aponta para indice/camera errada ou camera ocupada | Verifique a camera. Em maquina com mais de uma camera, teste outro indice (1, 2). Feche apps que estejam usando a webcam. |
| Gesto detectado dispara a acao varias vezes seguidas | Sem respeitar o debounce em frames (`gesture_cooldown`) | Comportamento esperado e o cooldown por gesto (20-30 frames). Se persistir, refaca o gesto mais nitido; ver [[RF-008_Debounce_Cooldown_E_Trava_Acao]]. |
| Nenhuma nova acao dispara apos uma acao "travar" | `Control.ACTION` ficou `True` (acao nao chegou ao `False` final, ex.: excecao no meio) | Trava global por design. Reinicie o app. Investigue excecao na acao que travou. Ver [[ADR-0004_Concorrencia_Asyncio_ThreadPool]]. |
| Gravacao de video nao para / liga e desliga "sozinha" | Todo gesto disparado faz toggle de `Control_Video` (`Control_Video = not Control_Video` em `Check_Gesture`) | Quirk conhecido: a flag de gravacao alterna a cada acao, nao so no gesto de video. Ver [[RF-002_Gravacao_Video_Gesto_Positivo]]. |
| Gesto "Rock" (video + pergunta) lanca `TypeError` | `Video_Audio` chama `self.Capture_Audio` **sem** o argumento `executor` obrigatorio | Bug conhecido. Ver [[BUG-001_Video_Audio_Sem_Executor]] para a correcao (passar `executor`). |
| `OSError`/`No Default Input Device` ao perguntar por voz | Microfone nao detectado ou `PyAudio` ausente (backend do `SpeechRecognition`/`sr.Microphone`) | Instale `PyAudio` e confira o microfone padrao do SO. Ver [[Instalacao_Dependencias]] e [[Ref_SpeechRecognition]]. |
| Pergunta por voz responde "Sem Pergunta" / "Erro de conexao" | `recognize_google` exige internet; silencio/ruido gera `UnknownValueError` | Verifique a conexao e fale dentro da janela de captura (`timeout=5`, `phrase_time_limit=5`). Ver [[RNF-006_Dependencia_Conectividade]]. |
| Som de confirmacao de **video** toca ao capturar **audio** | `Capture_Audio` reusa `video_start_sound` como confirmacao | Quirk cosmetico, sem impacto funcional. Nao e erro. |

## Desempenho e travamentos

| Sintoma | Causa provavel | Acao |
|---|---|---|
| App "congela" alguns segundos ao analisar video | `Video_To_Text` faz polling bloqueante com `time.sleep(10)` enquanto o Gemini processa o upload | Esperado para videos. O proprio codigo marca como "Bomba, precisa ser limpo". Aguarde o processamento. Ver [[ADR-0002_Gemini_Multimodal]]. |
| Latencia alta no Raspberry Pi 3 | Pipeline pesado (MediaPipe + Gemini + TTS) no hardware alvo | Esperado. Ver expectativas em [[RNF-001_Execucao_Raspberry_Pi3]] e [[RNF-004_Latencia_Resposta]]. |

## Referencias

- [[Guia_Rapido_Execucao|Guia rapido de execucao]]
- [[Instalacao_Dependencias|Instalacao de dependencias]]
- [[FAQ_Jarvis|FAQ do Jarvis]]
- [[BUG-001_Video_Audio_Sem_Executor|BUG-001: Video_Audio sem executor]]
- [[BUG-002_Recycle_Midia_Sem_Self|BUG-002: Recycle_Midia sem self]]
- [[BUG-003_ProjectConfig_Mkdir_Sem_ExistOk|BUG-003: ProjectConfig mkdir sem exist_ok]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008: debounce, cooldown e trava de acao]]
- [[Arquitetura_Software|Arquitetura do software]]
