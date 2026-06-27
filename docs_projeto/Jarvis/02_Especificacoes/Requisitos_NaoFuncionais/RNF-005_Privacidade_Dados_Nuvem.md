---
title: RNF-005 · Privacidade de dados enviados a nuvem
type: requisito
status: aprovado
created: 2026-06-27
updated: 2026-06-27
project: Jarvis
id: RNF-005
module: 02_Especificacoes
categoria: nao-funcional
prioridade: alta
tags: [requisito, layer/especificacao, prio/alta, tema/privacidade, tema/seguranca]
---

# RNF-005 · Privacidade de dados enviados a nuvem

## Descricao

Imagens, videos e audio capturados pelos oculos sao **enviados a servicos de
terceiros** para processamento. O sistema deve tratar esses dados com consentimento
explicito do usuario e politica de retencao clara, dado que os oculos podem capturar
ambientes e terceiros sem que estes saibam.

## Dados que saem do dispositivo

| Dado | Servico de destino | Onde no codigo |
|------|--------------------|----------------|
| Fotos (`.jpg`) | Google Photos (upload) + Google Gemini (analise) | [[manager.py]] `uploadMidia`; [[jarvis.py]] `Image_To_Text` |
| Videos (`.avi`) | Google Photos (upload) + Google Gemini (upload + analise) | [[manager.py]] `uploadMidia`; [[jarvis.py]] `Video_To_Text` |
| Audio (voz) | Google Speech (`recognize_google`) | [[control.py]] `Capture_Audio` |
| Texto da pergunta | Google Gemini | [[jarvis.py]] `Text_To_Text` |

## Justificativa

Captura vestivel + envio a nuvem implica exposicao de dados pessoais e de terceiros.
Sem consentimento e retencao definidos, o produto incorre em risco legal (ex.: LGPD)
e etico. Decisoes correlatas: [[ADR-0002_Gemini_Multimodal|ADR-0002]] e
[[ADR-0005_Upload_Google_Photos_OAuth|ADR-0005]].

## Mitigacao parcial ja presente no codigo

`Delete_Cahche_Files` em [[jarvis.py]] percorre `genai.list_files()` e apaga os
arquivos enviados ao Gemini (chamado ao fim de `Video_To_Text`), reduzindo retencao
no lado do Gemini. **Limitacoes**:

- So roda no fluxo de video; fotos analisadas por `Image_To_Text` nao usam
  `upload_file`, mas confirmar retencao do `inline data`.
- **Nao** apaga o que foi enviado ao **Google Photos** (continua na conta do usuario).
- A foto/video local em `midia/` permanece no disco (ver `Recycle_midia`, que existe
  mas tem o bug de assinatura sem `self` — ver [[BUG-002_Recycle_Midia_Sem_Self|BUG-002]]).

## Criterios de aceitacao

| # | Criterio | Status | Como medir |
|---|----------|--------|------------|
| 1 | Existe consentimento explicito antes do primeiro envio | a definir | nao implementado no codigo |
| 2 | Politica de retencao documentada (local e nuvem) | a definir | documentar e publicar |
| 3 | Cache do Gemini e limpo apos uso | parcial | `Delete_Cahche_Files` no fluxo de video |
| 4 | Midia local pode ser descartada apos upload | parcial | `Recycle_midia` (com bug) — ver BUG-002 |
| 5 | Segredos OAuth (`env/`) fora do versionamento | a verificar | conferir `.gitignore` |

## Riscos

- Captura de terceiros sem consentimento (privacidade de quem esta no campo de visao).
- `env/client_secret.json` e `env/token.json` sao credenciais sensiveis; vazamento da
  acesso a conta Google Photos do usuario (ver [[ADR-0005_Upload_Google_Photos_OAuth|ADR-0005]]).

## Referencias

- [[RNF-006_Dependencia_Conectividade|RNF-006 · Dependencia de conectividade]]
- [[ADR-0002_Gemini_Multimodal|ADR-0002 · Gemini multimodal]]
- [[ADR-0005_Upload_Google_Photos_OAuth|ADR-0005 · Upload Google Photos OAuth]]
- [[BUG-002_Recycle_Midia_Sem_Self|BUG-002 · Recycle_midia sem self]]
- [[Ref_Google_Photos_API]]
- [[Ref_Google_Gemini_API]]
