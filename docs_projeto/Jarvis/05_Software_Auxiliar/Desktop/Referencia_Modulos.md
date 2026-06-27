---
title: Referencia de Modulos do Jarvis
type: referencia
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 05_Software_Auxiliar
layer: software
tags: [arquitetura, software, layer/software, module/software, tema/referencia]
---

# Referencia de Modulos do Jarvis

Referencia detalhada por classe e metodo, fiel ao codigo-fonte. Para a visao de
arquitetura e os diagramas, ver [[Arquitetura_Software]].

> Convencao de landmarks (MediaPipe Hands): 21 pontos por mao, `x`/`y` normalizados
> em `[0,1]`. Convertidos para pixels com `x*w`, `y*h`. O eixo **Y cresce para baixo**,
> entao "y menor" = ponto mais **alto** na imagem. Thresholds relativos a `0.05*w`/`0.05*h`.

## 1. `main.py` (loop)

| Simbolo | Assinatura | O que faz / efeitos colaterais |
|---|---|---|
| `gesture_cooldown` | `int` (global, inicia em `0`) | Debounce em frames. Setado em `Check_Gesture`; decrementado 1 por frame no loop. |
| `main()` | `async def main()` | Cria tasks `init_hands()` e `init_control()` via `asyncio.gather`; abre `cv2.VideoCapture(0)`; entra no loop `while cap.isOpened()`. Le frame, converte BGR->RGB, `hands.process`. Por mao, monta `checks` e chama `Check_Gesture`. `imshow`; tecla `q` encerra; `cap.release()` + `destroyAllWindows()`. |
| `init_hands()` | `async def init_hands()` | Roda o construtor sincrono `hands.Hands()` em `loop.run_in_executor`. Retorna a instancia. |
| `init_control()` | `async def init_control()` | Idem para `control.Control()`. |
| `Check_Gesture(...)` | `async def Check_Gesture(func_exe, func_act, side, hand_label, state, cooldown, control_functions)` | Se `func_act()` e `hand_label == side`: seta `gesture_cooldown = cooldown`; se `state == "Async"`, faz **toggle** de `control_functions.Control_Video` e chama `func_exe()`. |
| `calculusNormalDistance(...)` | comentada | Estimativa de distancia da mao pelos landmarks 5 e 17. **Desativada**. |

Lista `checks` (tuplas `(func_exe, func_act, side, state, cooldown)`):

| `func_act` | `side` | `cooldown` | `func_exe` (submit) |
|---|---|---|---|
| `Map_Ok` | `Right` | `20` | `Capture_Photo(frame, executor)` |
| `Map_Positive` | `Left` | `30` | `Capture_Video(cap, executor)` |
| `Map_Speak` | `Right` | `20` | `Audio_to_Audio(executor)` |
| `Map_Squid` | `Left` | `20` | `Image_Audio(frame, executor)` |
| `Map_Rock` | `Right` | `20` | `Video_Audio(cap, executor)` |

Guarda do disparo no loop: so chama `Check_Gesture` se `control_functions.ACTION == False`
**e** `gesture_cooldown == 0`.

## 2. `hands.py` — classe `Hands`

| Metodo | Assinatura | O que faz |
|---|---|---|
| `__init__` | `(self)` | Cria `mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)` e `mp_drawing`. |
| `Calculate_Distance` | `(self, point1, point2)` | Distancia euclidiana entre dois pontos `(x, y)`. |
| `Map_Ok` | `(self, h, w, hand_landmarks, frame)` | OK / pinca. |
| `Map_Positive` | `(self, h, w, hand_landmarks, frame)` | Joinha / positivo. |
| `Map_Speak` | `(self, h, w, hand_landmarks, frame)` | Dedo (indicador) levantado. |
| `Map_Squid` | `(self, h, w, hand_landmarks, frame)` | "L". |
| `Map_Rock` | `(self, h, w, hand_landmarks, frame)` | Rock (chifre). |

Cada `Map_*` retorna `True` quando a pose e detectada (caso contrario, retorna `None`).
Condicoes geometricas (landmarks em pixels):

| Gesto | Condicao (resumo fiel ao codigo) |
|---|---|
| `Map_Ok` | `dist(polegar4, indicador8) < 0.05*w` **e** `indicador5_y > indicador6_y` **e** `polegar1_y > indicador6_y` **e** `polegar3_x > indicador5_x` (polegar e indicador encostam, demais baixos). |
| `Map_Positive` | `polegar4_y < polegar1_y - 0.05*h` (polegar levantado) **e** indicador/medio/anelar/mindinho dobrados (`ponta_y > base_y`). |
| `Map_Speak` | `indicador8_y < indicador5_y - 0.05*h` (indicador levantado) **e** `polegar4_x > polegar1_x` (polegar lateral) **e** medio/anelar/mindinho dobrados. |
| `Map_Squid` | `indicador8_y < indicador6_y - 0.05*h` (indicador levantado) **e** `polegar4_x < polegar2_x` (polegar aberto) **e** medio/anelar/mindinho dobrados. |
| `Map_Rock` | `indicador8_y < indicador6_y - 0.05*h` **e** `mindinho20_y < mindinho18_y - 0.05*h` (indicador e mindinho levantados) **e** medio/anelar dobrados. |

> Nota: `Map_Ok` e `Map_Speak` tem trechos do retorno antigo comentados
> (`# return save_foto(frame)`, `# return save_video()`), sem efeito no fluxo atual.

## 3. `control.py` — classe `Control`

`mixer.init()` (pygame) e chamado no `__init__` (e nao no import do modulo) para evitar
efeito colateral ao importar e permitir testar sem dispositivo de audio.

### 3.1 Estado e sons

| Atributo | Valor inicial | Papel |
|---|---|---|
| `ACTION` | `False` | Trava global: impede acao concorrente. |
| `jarvis_system` | `jarvis.Jarvis(mixer)` | Cliente de IA + TTS. |
| `menager_system` | `manager.Manager()` | Upload Google Photos. |
| `Control_Video` | `False` | Liga/desliga gravacao de video. |
| `photo_take_sound` | `audios_check/photo_take.wav` | Confirma foto. |
| `audio_start_sound` | `audios_check/audio_starter.wav` | Confirma inicio de audio (**definido mas nao usado**; ver quirk em `Capture_Audio`). |
| `video_start_sound` | `audios_check/video_starter.wav` | Confirma inicio de video (e tambem usado no audio). |
| `video_end_sound` | `audios_check/video_out.wav` | Confirma fim de video. |

### 3.2 Metodos

| Metodo | Assinatura | O que faz / efeitos colaterais |
|---|---|---|
| `play_confirmation_sound` | `async (self, sound_file)` | `mixer.Sound(sound_file).play()`; `await asyncio.sleep(SOUND.get_length())`; `stop()`. |
| `Recycle_midia` | `(midia_path)` | `os.remove(midia_path)`. **BUG**: declarado como metodo mas sem `self` na assinatura ([[BUG-002_Recycle_Midia_Sem_Self]]). |
| `Capture_Photo` | `(self, frame, executor)` | `ts = %Y%m%d_%H%M%S`; `cv2.imwrite(midia/{ts}.jpg, frame)`; toca `photo_take_sound`; `executor.submit(uploadMidia, midia/{ts}.jpg)`; retorna o caminho. |
| `Capture_Video` | `(self, cap, executor)` | `VideoWriter(fourcc XVID, midia/{ts}.avi, fps=30, (640,480))`; toca `video_start_sound`; loop `while self.Control_Video: cap.read -> out.write`; `out.release()`; toca `video_end_sound`; submit `uploadMidia`; retorna o caminho. |
| `Capture_Audio` | `(self, executor)` | `ACTION=True`; `sr.Recognizer` (`pause_threshold=0.8`, `dynamic_energy_threshold=False`, `energy_threshold=300`, `maxAlternatives=1`); `sr.Microphone`; `adjust_for_ambient_noise(duration=2)`; toca `video_start_sound` (**quirk**: usa o som de video); `listen(timeout=5, phrase_time_limit=5)`; `recognize_google(language="pt-BR")`. Retorna o texto. Excecoes: `UnknownValueError`->`"Sem Pergunta"`; `RequestError`->`"Erro de conexao"`; `Exception`->`"Erro inesperado: ..."`. |
| `Audio_to_Audio` | `(self, executor) -> None` | `ACTION=True`; `prompt = Capture_Audio`; `asyncio.run(jarvis_system.Text_To_Text(prompt))`; `ACTION=False`. |
| `Image_Audio` | `(self, frame, executor) -> None` | `ACTION=True`; submit `Capture_Photo` e `Capture_Audio` em paralelo; pega `image_path` e `prompt`; `asyncio.run(jarvis_system.Image_To_Text(image_path, prompt))`; `ACTION=False`. |
| `Video_Audio` | `(self, cap, executor) -> None` | submit `Capture_Video`; submit `Capture_Audio` (**BUG**: sem o arg `executor` — [[BUG-001_Video_Audio_Sem_Executor]]); pega `video_path` e `prompt`; `ACTION=True`; `asyncio.run(jarvis_system.Video_To_Text(video_path, prompt))`; `ACTION=False`. |

## 4. `jarvis.py` — classe `Jarvis`

| Metodo | Assinatura | O que faz / efeitos colaterais |
|---|---|---|
| `__init__` | `(self, mixer)` | `load_dotenv()`; `API_KEY = os.getenv("API_GEMINI")`; define `template` (persona PT-BR: IA "Jarvis" que trata o usuario como "Mestre", foco em programacao/ML/ciencia de dados/visao computacional, proativa); `genai.configure(api_key)`; `model = GenerativeModel("gemini-2.0-flash-lite", system_instruction=template)`; `VOICE = "pt-BR-AntonioNeural"`; `PATH_FILE = "./response/translate.mp3"`. |
| `Delete_Cahche_Files` | `(self)` | Percorre `genai.list_files()` e deleta cada arquivo (limpa armazenamento do Gemini). Mantem o typo "Cahche" como esta no codigo. |
| `Translate` | `async (self, text) -> None` | Substitui caracteres (`\t`, `*`, zero-width `​`/`‌`/`‍`, BOM `﻿`, espacos duplos) por espaco; `strip`; `edge_tts.Communicate(text, VOICE)`; `await communicate.save(PATH_FILE)`. |
| `Text_To_Text` | `async (self, prompt) -> None` | `model.generate_content(prompt)`; `Translate(response.text)`; `mixer.Sound(PATH_FILE).play()`; `await asyncio.sleep(len)`; `stop()`. |
| `Image_To_Text` | `async (self, image_path, prompt) -> None` | `generate_content([{mime_type: image/jpeg, data: pathlib.Path(image_path).read_bytes()}, prompt])`; `Translate`; toca o mp3. |
| `Video_To_Text` | `async (self, video_path, prompt) -> None` | `genai.upload_file(path=video_path)`; enquanto `state.name == "PROCESSING"`: `print('.')`, `time.sleep(10)` (**bloqueante** — comentario do codigo: "Bomba, precisa ser limpo"), `get_file`; se `FAILED` -> `raise ValueError`; `generate_content([video_file, prompt], request_options={"timeout": 600})`; `Translate`; toca; `Delete_Cahche_Files()`. |

## 5. `manager.py` — classe `Manager`

| Metodo | Assinatura | O que faz / efeitos colaterais |
|---|---|---|
| `__init__` | `(self)` | `CLIENT_SECRET = ./env/client_secret.json`; `CREDENTIALS_FILE = ./env/token.json`; `SCOPES = [photoslibrary]`. |
| `authorize_credentials` | `(self)` | Le `token.json` se existe; se invalido e tem `refresh_token`, `refresh`; senao `InstalledAppFlow.from_client_secrets_file(...).run_local_server(port=0)`; salva `token.json`; retorna `creds.token`. |
| `getPhotoUrl` | `(self, access_token, photo_id)` | `GET /v1/mediaItems/{id}`; retorna `baseUrl`. |
| `uploadMidia` | `(self, image_path)` | Pega token; `POST /v1/uploads` (raw, `X-Goog-Upload-Protocol: raw`, `Content-Type: image/jpeg` — **quirk**: fixo, mesmo para video `.avi`); se `200`: `POST /v1/mediaItems:batchCreate` com `uploadToken` + `fileName`; pega `photo_id`; chama `getPhotoUrl`. **`photo_url` e calculado mas nao e retornado nem usado.** Se `!= 200`: `raise_for_status()`. |

## 6. `ProjectConfig.py` (bootstrap)

| Simbolo | Assinatura | O que faz |
|---|---|---|
| `Config_Project()` | `def Config_Project()` | `os.makedirs('response', exist_ok=True)`; `os.makedirs('midia', exist_ok=True)`; `open('.env', 'a').close()`. **Idempotente** (nao quebra na 2a execucao). |
| guard `__main__` | — | So roda `Config_Project()` quando executado direto (`python ProjectConfig.py`), permitindo importar sem efeito colateral. |

> O codigo **atual** ja corrige o problema historico de `os.mkdir` sem `exist_ok`
> descrito em [[BUG-003_ProjectConfig_Mkdir_Sem_ExistOk]] (manter a nota para historico).

## 7. Dependencias externas

| Biblioteca / Servico | Papel | Referencia |
|---|---|---|
| OpenCV (`cv2`) | Camera, IO de imagem/video, janela. | [[Ref_OpenCV]] |
| MediaPipe Hands | Deteccao dos 21 landmarks. | [[Ref_MediaPipe_Hands]] |
| `google.generativeai` (Gemini) | IA multimodal `gemini-2.0-flash-lite`. | [[Ref_Google_Gemini_API]] |
| `edge-tts` | TTS, voz `pt-BR-AntonioNeural`. | [[Ref_Edge_TTS]] |
| `pygame.mixer` | Playback de audio. | [[Ref_Pygame_Mixer]] |
| `SpeechRecognition` | STT (`recognize_google`, pt-BR). | [[Ref_SpeechRecognition]] |
| Google Photos Library API | Upload via OAuth2. | [[Ref_Google_Photos_API]] |
| `python-dotenv` | Carrega `.env` (`API_GEMINI`). | — |

## 8. Referencias

- [[Arquitetura_Software]] — visao geral e diagramas
- [[Mapa_Gestos]] — geometria dos gestos
- [[Guia_Rapido_Execucao]], [[Instalacao_Dependencias]]
- [[Troubleshooting_Jarvis]], [[FAQ_Jarvis]]
- Bugs: [[BUG-001_Video_Audio_Sem_Executor]], [[BUG-002_Recycle_Midia_Sem_Self]],
  [[BUG-003_ProjectConfig_Mkdir_Sem_ExistOk]]
