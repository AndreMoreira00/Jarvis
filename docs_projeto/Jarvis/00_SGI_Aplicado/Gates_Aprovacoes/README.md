---
title: Gates_Aprovacoes — Jarvis
area: Qualidade_Aplicada/Gates_Aprovacoes
tags: [readme, template, projeto]
project: Jarvis
created: 2026-06-27
updated: 2026-06-27
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Gates_Aprovacoes

Atas de aprovação de cada gate (G0 → G5) do projeto. **Metodologia, critérios de aceitação e checklist por gate** são canônicos e vivem em [Ref_Metodologia_Analise_Projeto](../../../Ref_Metodologia_Analise_Projeto) — não duplicar aqui.

## 📌 Como usar

1. Antes de propor um gate, verifique a [Matriz_Rastreabilidade](../../06_Testes_Validacao/Matriz_Rastreabilidade.base) deste projeto e confirme que as views "❌" exigidas pelo gate-alvo estão vazias (ver tabela "Rastreabilidade mínima por gate" da metodologia).
2. Crie nesta pasta `Gate_GN_YYYY-MM-DD.md` (substituindo `N` pelo número do gate e a data real) com `type: ata`, o checklist do gate da metodologia e wikilinks para as evidências (RFs, TPs, TRs, ADRs, FO-xxx).
3. Após aprovação, atualize `Home.md` do projeto com o novo `gate_atual: "GN — <Fase>"`.
4. Reprovação → abra NC em `../NCs_do_Projeto/` apontando os critérios não atendidos.

## 🔗 Ver também

- [Ref_Metodologia_Analise_Projeto](../../../Ref_Metodologia_Analise_Projeto) — gates G0 → G5, critérios, rastreabilidade mínima
- [Matriz_Rastreabilidade](../../06_Testes_Validacao/Matriz_Rastreabilidade.base) — fonte de verdade para cobertura
