---
title: Separacao em dois repositorios - firmware (este) e app (Jarvis-APP)
type: decisao-repo
status: aprovado
date: 2026-06-28
created: 2026-06-28
updated: 2026-06-28
project: Jarvis
tags: [decisao, repositorios, firmware, app, escopo, contrato, tema/arquitetura]
---

# Separacao em dois repositorios - firmware (este) e app (Jarvis-APP)

## Contexto

A decisao de arquitetura macro ([[2026-06-27_arquitetura_tres_pilares]]) definiu **oculos =
cliente fino (ESP32-S3) + celular = cerebro (app Android com IA offline)**. Esses dois lados tem
ciclos de vida, linguagens e toolchains distintos (C/C++ ESP-IDF vs Kotlin/Android). Manter os dois
no mesmo repo misturaria build systems e historico.

O dono ja criou: (a) a branch `Jarvis-ESP-Frimware` e o projeto ESP-IDF em `Jarvis-ESP-Frimeware/`
neste repo; (b) o repo separado `Jarvis-APP` (vazio, so com o template de documentacao).

## Decisao

Dividir o produto em **dois repositorios**, com fronteira de responsabilidade explicita.

### Repo Jarvis (este) = firmware + spec
- Firmware dos oculos em `Jarvis-ESP-Frimeware/` (ESP-IDF, C/C++): camera DVP -> MJPEG por WiFi,
  audio I2S (mic + conducao ossea via MAX98357A), wake word (ESP-SR), IMU, energia/sleep.
- O pacote Python `src/jarvis` permanece como **spec executavel** do comportamento a ser portado
  (regras de gesto, fluxos, persona PT-BR) — nao e descartado, vira referencia.
- Toda a doc de arquitetura macro, hardware, energia e audio fica aqui (`docs_projeto/`).

### Repo Jarvis-APP = cerebro (app Android)
- App Kotlin: percepcao de gestos (MediaPipe), IA on-device (VLM/LLM offline), STT/TTS, orquestracao, UI.
- Documentacao instanciada do template em `docs_projeto/Jarvis_App/` (modulos de HW/firmware/
  certificacao/producao podados; o app e software puro).

### Contrato de comunicacao oculos<->app
- **Fonte da verdade no repo Jarvis-APP**: `docs_projeto/Jarvis_App/05_Software_Auxiliar/App_Mobile/Contrato_Comunicacao_Oculos.md`.
- O firmware (este repo) **implementa e referencia** — nao redefine. Justificativa: o app orquestra
  o sistema e evolui mais rapido; manter o contrato perto da orquestracao reduz divergencia
  (decisao espelhada na ADR-0003 do repo do app).

## Alternativas consideradas

- **Monorepo (firmware + app juntos)** — historico unico · mas mistura toolchains (ESP-IDF/CMake vs
  Gradle/Android), polui build e CI, e acopla ciclos de release distintos. Descartado.
- **Contrato dono do firmware** — logico se o hardware expusesse a interface · mas o app muda mais
  rapido; geraria atrito de versao. Descartado (ver ADR-0003 do app).
- **Contrato duplicado nos dois repos** — visibilidade dos dois lados · mas duplicar a spec canonica
  diverge ao evoluir. Adotado so como **resumo/ponteiro** aqui, com a fonte no app.

## Consequencias

### Positivas
- Toolchains e CI isolados por repo; releases independentes.
- Fronteira clara reduz confusao sobre "onde mexer".
- App auto-contido (doc instanciada do template, do jeito que o template manda).

### Negativas / riscos
- **Contrato precisa de disciplina de versao** (campo `protocolVersion` no handshake) — mudanca no
  app pode quebrar o firmware se nao versionar.
- Doc do produto agora vive em **dois lugares**; manter os ponteiros cruzados atualizados
  (CLAUDE.md daqui aponta para o app; Home do app aponta para ca).
- O MVP Python coexiste com o firmware no mesmo repo — deixar claro que e spec, nao runtime do produto.

## Arquivos alterados/criados

Neste repo:
- `CLAUDE.md` — nova secao "Escopo dos repositorios (LEIA PRIMEIRO)".
- `docs_projeto/decisoes/2026-06-28_separacao_repos_firmware_app.md` (este arquivo).
- `docs_projeto/decisoes/README.md` — indice.

No repo Jarvis-APP:
- `docs_projeto/Jarvis_App/` instanciado do template (Home, Roadmap, ADR-0001/0002/0003, RF/RNF/CU,
  Arquitetura, Pipeline de IA, Contrato de comunicacao, 2 referencias, READMEs de modulo).

## Referencias

- [[2026-06-27_arquitetura_tres_pilares]]
- Repo Jarvis-APP: `docs_projeto/Jarvis_App/Home.md` e `.../App_Mobile/Contrato_Comunicacao_Oculos.md`
