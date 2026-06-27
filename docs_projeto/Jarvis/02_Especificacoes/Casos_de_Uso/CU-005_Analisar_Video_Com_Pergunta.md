---
title: CU-005 · Analisar vídeo com pergunta por voz
id: CU-005
type: caso-de-uso
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 02_Especificacoes
prioridade: alta
tags: [module/software, layer/especificacao, tema/gestos, tema/ia, prio/alta]
---

# CU-005 · Analisar vídeo com pergunta por voz

Grava um vídeo, faz uma pergunta falada sobre ele e recebe a análise multimodal do
Gemini em áudio. Disparado pelo gesto **rock** com a **mão direita**.

## Ator

- **Usuário** dos óculos inteligentes.

## Pré-condições

- App `main.py` rodando, câmera aberta, mão detectada.
- `Control.ACTION == False` e `gesture_cooldown == 0`.
- Microfone disponível; pastas `midia/` e `response/` existentes.
- `.env` com `API_GEMINI` válida; conexão estável (upload de vídeo ao Gemini).

## Gesto disparador

| Atributo | Valor |
|---|---|
| Método | `Hands.Map_Rock` |
| Mão exigida | Direita (`Right`) |
| Cooldown | 20 frames |
| Estado (`state`) | `Async` |
| Ação | `Control.Video_Audio(cap, executor)` |

**Geometria (Map_Rock):** indicador levantado
(`indicador_8_y < indicador_6_y - 0.05 * h`) e mindinho levantado
(`mindinho_20_y < mindinho_18_y - 0.05 * h`), com médio e anelar dobrados —
formando os "chifres".

## Fluxo principal

1. `Check_Gesture` confirma `Map_Rock == True` e `hand_label == "Right"`.
2. `gesture_cooldown = 20`; alterna `Control_Video`; submete
   `Video_Audio(cap, executor)`.
3. `Video_Audio`:
   - submete `Capture_Video(cap, executor)` (gravação enquanto `Control_Video`);
   - submete `Capture_Audio` para captar a pergunta;
   - aguarda `video_path` e `prompt`;
   - seta `ACTION = True`;
   - `asyncio.run(jarvis_system.Video_To_Text(video_path, prompt))`;
   - seta `ACTION = False`.
4. `Jarvis.Video_To_Text`:
   - `genai.upload_file(video_path)` envia o vídeo à memória do Gemini;
   - faz polling `while state == "PROCESSING": time.sleep(10)` (**bloqueante** —
     comentado no código como "Bomba, precisa ser limpo");
   - se `state == "FAILED"` → `raise ValueError`;
   - `generate_content([video_file, prompt], request_options={"timeout": 600})`;
   - `Translate(response.text)` → `response/translate.mp3` (edge-tts) e toca;
   - `Delete_Cahche_Files()` limpa os arquivos no Gemini.

## Fluxos alternativos e de erro

- **Mão errada / cooldown / ação em curso:** não dispara.
- **BUG conhecido:** `Capture_Audio` é submetido **sem** o argumento `executor`
  (`executor.submit(self.Capture_Audio)`), mas a assinatura exige
  `Capture_Audio(self, executor)` → `TypeError` ao resolver `future_audio.result()`.
  Ver [[BUG-001_Video_Audio_Sem_Executor]]. Na prática, este fluxo tende a falhar.
- **Toggle de gravação:** como o gesto rock também alterna `Control_Video`, o
  encerramento da gravação depende do estado da flag — acoplamento frágil (ver
  [[CU-002_Gravar_Video]]).
- **Vídeo em PROCESSING longo:** o `time.sleep(10)` bloqueia a thread durante todo
  o processamento; o app fica menos responsivo.
- **Processamento FAILED:** `raise ValueError(state)` interrompe o fluxo; `ACTION`
  pode permanecer `True` (sem `finally`).
- **STT falha:** `prompt` assume mensagem de erro (`"Sem Pergunta"`, etc.) e segue
  para o Gemini.
- **Quirk de upload no Photos:** o `Capture_Video` envia o `.avi` com MIME
  `image/jpeg` (ver [[CU-002_Gravar_Video]]).

## Pós-condições

- `midia/<timestamp>.avi` gravado e (tentativa de) upload ao Photos.
- Vídeo analisado pelo Gemini; resposta reproduzida em áudio.
- Cache de arquivos no Gemini limpo via `Delete_Cahche_Files`.
- `ACTION == False` no caminho feliz; `gesture_cooldown == 20`.

## Observações

- É o fluxo mais pesado e o mais frágil (bug do `executor` + sleep bloqueante +
  upload de vídeo). Forte candidato a refatoração — ver [[Roadmap_Jarvis]].
- Diferente da imagem (inline), o vídeo usa `genai.upload_file` por tamanho
  variável.

## Requisitos relacionados

- [[RF-005_Video_Mais_Pergunta_Analise|RF-005 · Vídeo + pergunta para análise]]
- [[RF-007_Resposta_Falada_Persona_Jarvis|RF-007 · Resposta falada com persona Jarvis]]
- [[RF-008_Debounce_Cooldown_E_Trava_Acao|RF-008 · Debounce, cooldown e trava de ação]]

## Referências

- [[Mapa_Gestos|Mapa de gestos]]
- [[CU-002_Gravar_Video|CU-002 · Gravar vídeo]]
- [[CU-003_Perguntar_Por_Voz|CU-003 · Perguntar por voz]]
- [[BUG-001_Video_Audio_Sem_Executor|BUG-001 · Video_Audio sem executor]]
- [[Ref_Google_Gemini_API|Referência: Google Gemini API]]
- [[Arquitetura_Software|Arquitetura do software]]
