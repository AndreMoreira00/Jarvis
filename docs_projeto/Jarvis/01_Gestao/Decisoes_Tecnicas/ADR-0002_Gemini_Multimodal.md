---
title: ADR-0002 · Google Gemini (gemini-2.0-flash-lite) como IA multimodal
type: adr
status: aceito
id: ADR-0002
deciders: [Andre Moreira]
date: 2026-06-27
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
module: 01_Gestao
layer: gestao
tags: [adr, module/software, layer/gestao, tema/ia, tema/multimodal]
---

# ADR-0002 · Google Gemini (gemini-2.0-flash-lite) como IA multimodal

## Contexto

O cerebro de IA do Jarvis precisa responder ao "Mestre" a partir de tres tipos de
entrada, todos disparados por gesto (ver [[Mapa_Gestos]]):

- **texto** — pergunta por voz transcrita ([[CU-003_Perguntar_Por_Voz]]);
- **imagem + texto** — foto da camera + pergunta ([[CU-004_Analisar_Imagem_Com_Pergunta]]);
- **video + texto** — clipe gravado + pergunta ([[CU-005_Analisar_Video_Com_Pergunta]]).

Ou seja, exige um modelo **multimodal** unico que aceite texto, imagem e video, com
uma **persona** consistente (a IA "Jarvis", que trata o usuario como "Mestre", com
foco em programacao, machine learning, ciencia de dados e visao computacional). O
custo de manutencao tem de ser baixo (1 dev) e a latencia compativel com uso
embarcado no oculos.

## Decisao

Adotar **Google Gemini** via SDK `google.generativeai`, modelo
**`gemini-2.0-flash-lite`**, instanciado em [jarvis.py](../../../../jarvis.py)
(`class Jarvis`) com `system_instruction` carregando a persona PT-BR.

| Aspecto | Decisao |
|---|---|
| Modelo | `gemini-2.0-flash-lite` (variante leve/barata, baixa latencia) |
| SDK | `google.generativeai` (`genai.configure`, `genai.GenerativeModel`) |
| Persona | `system_instruction=template` (texto PT-BR "Jarvis"/"Mestre") |
| Chave | `API_GEMINI` lida do `.env` via `python-dotenv` |
| Texto | `Text_To_Text` → `model.generate_content(prompt)` |
| Imagem | `Image_To_Text` → `generate_content([{mime_type:'image/jpeg', data:bytes}, prompt])` |
| Video | `Video_To_Text` → `genai.upload_file(...)` + polling de estado + `generate_content([video_file, prompt], request_options={"timeout":600})` |
| Limpeza | `Delete_Cahche_Files` percorre `genai.list_files()` e apaga cada arquivo apos uso |

A saida (texto) e encaminhada para sintese de voz e reproducao, decisao tratada em
[[ADR-0003_TTS_EdgeTTS_Pygame]].

## Alternativas consideradas

| Alternativa | Por que foi descartada |
|---|---|
| **GPT-4o (OpenAI)** | Multimodal e competente, mas implicaria outro provedor/billing; Gemini foi escolhido pela variante `flash-lite` barata e integracao direta com o ecossistema Google ja usado (Google Photos, ver [[ADR-0005_Upload_Google_Photos_OAuth]]). |
| **Modelo local (ex.: LLaVA)** | Removeria a dependencia de internet, mas e inviavel rodar visao multimodal no Raspberry Pi 3 com latencia aceitavel (ver [[ADR-0007_Alvo_Raspberry_Pi3]]). |
| **Separar visao + LLM** (detector/legenda local + LLM so texto) | Mais pecas para manter e orquestrar; um unico modelo multimodal simplifica o codigo e o fluxo de `generate_content`. |

## Consequencias

### Positivas

- **Um unico modelo** cobre os tres modos (texto/imagem/video), reduzindo
  complexidade do codigo em [[Arquitetura_Software|jarvis.py]].
- **`flash-lite`** prioriza custo e latencia baixos, adequado a uso interativo.
- **Persona centralizada** em `system_instruction`: a identidade "Jarvis"/"Mestre"
  e mantida em um unico ponto (ver [[RF-007_Resposta_Falada_Persona_Jarvis]]).
- Reuso do **mesmo ecossistema Google** ja necessario para o upload de midia.

### Negativas / riscos

- **Dependencia de internet, chave e custo**: sem conectividade ou sem
  `API_GEMINI` valido, todo o fluxo de IA para (ver [[RNF-006_Dependencia_Conectividade]]).
- **Upload de video bloqueante**: em `Video_To_Text`, o polling do estado usa
  `time.sleep(10)` sincrono num loop `while ... == "PROCESSING"`. O proprio codigo
  comenta *"Bomba, precisa ser limpo"* — isso **bloqueia a thread** enquanto o video
  e processado, prejudicando a latencia e a responsividade (ver
  [[RNF-004_Latencia_Resposta]] e [[ADR-0004_Concorrencia_Asyncio_ThreadPool]]).
- **Necessidade de `Delete_Cahche_Files`**: arquivos enviados ao Gemini precisam
  ser apagados manualmente apos uso para nao acumular na conta/armazenamento; se
  isso falhar, ha acumulo. (O metodo tem typo no nome: `Cahche`.)
- **Privacidade**: imagens e videos do ambiente do usuario sao enviados a um
  servico de nuvem de terceiros (ver [[RNF-005_Privacidade_Dados_Nuvem]]).
- **Acoplamento ao SDK**: mudancas de API ou desativacao do modelo
  `gemini-2.0-flash-lite` exigem revisao.

## Referencias

- [[Ref_Google_Gemini_API]] — referencia da API/SDK do Gemini
- [[RNF-006_Dependencia_Conectividade]] — requisito de conectividade
- [[RNF-005_Privacidade_Dados_Nuvem]] — privacidade de dados na nuvem
- [[RNF-004_Latencia_Resposta]] — requisito de latencia
- [[ADR-0003_TTS_EdgeTTS_Pygame]] — sintese e reproducao da resposta
- [[ADR-0004_Concorrencia_Asyncio_ThreadPool]] — modelo de concorrencia
- [[CU-003_Perguntar_Por_Voz]] · [[CU-004_Analisar_Imagem_Com_Pergunta]] · [[CU-005_Analisar_Video_Com_Pergunta]]
- [[TP-002_Validacao_Fluxo_IA_Gemini]] — plano de teste do fluxo de IA
