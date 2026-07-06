---
title: Decisoes do repo template
type: readme
status: aprovado
created: 2026-05-28
updated: 2026-05-28
tags: [readme, decisoes]
---

# Decisoes do repo template

Registro de mudancas estruturais feitas **neste repositorio** (nao nos projetos derivados dele). Cada entrada e uma nota datada com o que mudou e por que.

> Para decisoes tecnicas **dentro de um projeto**, use o template ADR em `docs_Template_Projeto/_templates/ADR_Template.md` (modulo `01_Gestao/Decisoes_Tecnicas/`).

## Indice

- [[2026-05-28_configuracao_obsidian_template]] — configuracao inicial da estrutura Obsidian do template
- [[2026-06-27_testes_unitarios]] — suite de testes unitarios com pytest + mock total (cobertura ~92%, CI com gate, 10 bugs reais mapeados)
- [[2026-06-27_arquitetura_tres_pilares]] — arquitetura de produto (firmware/hardware/app): oculos cliente-fino ESP32-S3 + celular cerebro com LLM offline, em duas fases
- [[2026-06-28_separacao_repos_firmware_app]] — divisao em 2 repos (firmware aqui / app em Jarvis-APP) e onde mora o contrato de comunicacao
- [[2026-06-29_plano_firmware_esp32s3]] — plano de implementacao do firmware (mapa firmware↔app, componentes ESP-IDF, tasks, energia, roadmap; BLE como 1º subsistema real)
- [[2026-06-29_contrato_ble_gatt_proposta]] — proposta v1 do contrato BLE GATT oculos↔app (JarvisService + Battery), a sincronizar com o repo do app
