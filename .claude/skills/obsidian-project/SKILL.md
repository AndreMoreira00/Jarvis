---
name: obsidian-project
description: Scaffold um novo projeto de produto em Sanesoluti/01_Projetos/ a partir do _Template_Projeto canônico (hardware + firmware + software auxiliar + certificações). Use quando o usuário pedir para criar um novo projeto, produto, pasta de projeto, ou abrir um projeto novo na vault Obsidian.
created: 2026-04-24
updated: 2026-04-24
---

# Obsidian Project Scaffold — Sanesoluti

Cria um novo projeto de produto em `Sanesoluti/01_Projetos/<Nome>/` replicando a estrutura canônica do `_Template_Projeto/`. Todo projeto de produto da Sanesoluti (hardware embarcado + firmware + software auxiliar + certificações) segue exatamente esse esqueleto.

## Quando invocar

- "Criar projeto novo" / "novo produto" / "abrir projeto"
- "Duplicar o template de projeto"
- "Scaffold de projeto para \<nome\>"
- Qualquer menção a iniciar uma pasta sob `01_Projetos/`

## Fonte canônica

A única fonte de verdade é [`Sanesoluti/01_Projetos/_Template_Projeto/`](../../../Sanesoluti/01_Projetos/_Template_Projeto/). **Nunca** improvise subpastas — se a estrutura precisar mudar, edite o template primeiro e rode a skill de validação ([/validate-ingestion](../obsidian-skills/skills/obsidian-cli/SKILL.md) quando aplicável).

## Estrutura canônica (14 áreas + infra)

```
<Nome>/
├── Home.md                          # dashboard do projeto
├── 00_SGI_Aplicado/                 # ponte com SGI (objetivos, riscos, NCs, gates, auditorias, registros)
│   ├── Auditorias_do_Projeto/
│   ├── Gates_Aprovacoes/
│   ├── NCs_do_Projeto/
│   ├── Objetivos_do_Projeto/
│   ├── Registros_do_Projeto/
│   └── Riscos_do_Projeto/
├── 01_Gestao/                       # cronograma, atas, ADRs, roadmap
│   ├── Atas_Reunioes/
│   ├── Cronograma/
│   ├── Decisoes_Tecnicas/
│   └── Roadmap/
├── 02_Especificacoes/               # RF, RNF, RR, UC
│   ├── Casos_de_Uso/
│   ├── Requisitos_Funcionais/
│   ├── Requisitos_NaoFuncionais/
│   └── Requisitos_Regulatorios/
├── 03_Hardware/
│   ├── Eletronica/{BOM, Esquematicos, Gerber, PCB_Layout, Simulacoes}/
│   ├── Mecanica/{CAD_3D, Desenhos_2D, Enclosure, Moldes_Injecao}/
│   └── Prototipagem/{Rev_A, Rev_B, Rev_C}/
├── 04_Firmware/
│   ├── Bootloader/
│   ├── Codigo_Fonte/
│   ├── Documentacao_Tecnica/
│   ├── Flashing_Gravacao/
│   ├── OTA_Updates/
│   ├── Releases/
│   └── Toolchain_Build/
├── 05_Software_Auxiliar/
│   ├── API_Backend/
│   ├── App_Mobile/
│   ├── Desktop/
│   ├── Integracoes_Cloud/
│   └── Web_Dashboard/
├── 06_Testes_Validacao/
│   ├── Planos_de_Teste/
│   ├── Relatorios/
│   ├── Testes_Ambientais/
│   ├── Testes_Campo/
│   ├── Testes_EMC_EMI/
│   └── Testes_Seguranca/
├── 07_Certificacoes_Homologacoes/
│   ├── Anatel/
│   ├── CE/
│   ├── FCC/
│   ├── Inmetro/
│   ├── Outras/
│   └── RoHS_REACH/
├── 08_Producao/
│   ├── Arquivos_Fabricacao/
│   ├── Controle_Qualidade/
│   ├── Custos_BOM/
│   ├── Fornecedores/
│   └── Instrucoes_Montagem/
├── 09_Manuais/
│   ├── Guia_Instalacao/
│   ├── Guia_Rapido/
│   ├── Manual_Tecnico_Servico/
│   ├── Manual_Usuario/
│   └── Traducoes/
├── 10_Referencias/
│   ├── Artigos_Papers/
│   ├── Firmware/
│   ├── Hardware/
│   ├── Normas_Padroes/
│   └── Software_Auxiliar/
├── 11_Marketing_Comercial/
│   ├── Datasheet_Comercial/
│   ├── Fotos_Produto/
│   ├── Material_Site/
│   └── Videos/
├── 12_Suporte_PosVenda/
│   ├── FAQ/
│   ├── Notas_de_Atualizacao/
│   ├── RMA_Devolucoes/
│   └── Troubleshooting/
├── 13_Legal_IP/
│   ├── Contratos_NDAs/
│   ├── Licencas_Software/
│   ├── Marcas/
│   └── Patentes/
├── 99_Arquivo_Historico/
├── _assets/                         # anexos do projeto (imagens, PDFs, CAD)
└── _templates/                      # templates de nota deste projeto (ADR, Requisito, Teste)
```

## Workflow

### 1. Validar o nome do projeto

Regras:
- PascalCase ou snake_case em ASCII (sem acentos, espaços ou pontuação)
- Match regex `^[A-Za-z][A-Za-z0-9_]*$`
- Único dentro de `Sanesoluti/01_Projetos/`
- Se o usuário não informou, pergunte antes de prosseguir

### 2. Rodar o scaffolder

```bash
python .claude/scripts/new_project.py <NomeDoProjeto>
```

O script:
1. Copia recursivamente `_Template_Projeto/` → `<NomeDoProjeto>/`
2. Em todo `.md` copiado:
   - `project: _Template_Projeto` → `project: <NomeDoProjeto>`
   - `— _Template_Projeto` (título/H1) → `— <NomeDoProjeto>`
3. Reescreve `created: <hoje>` e `updated: <hoje>` em todos os frontmatters
4. Aborta se o destino já existir (idempotente)

### 3. Preencher o Home.md

Abra `Sanesoluti/01_Projetos/<Nome>/Home.md` e ajuste:
- `title:` para o nome real
- Seção "Atalhos": remova os links de exemplo que ainda não existem

### 4. Preencher SGI Aplicado

1. Abra `00_SGI_Aplicado/Procedimentos_Aplicaveis.md` e marque quais procedimentos SGQ/SGL se aplicam
2. Preencha `FO-001_Abertura_de_Projeto` (formulário do SGQ) e salve a cópia em `00_SGI_Aplicado/Registros_do_Projeto/`

### 5. Registrar no portfólio

Nada a fazer — a base [`Carteira_Projetos.base`](../../../Sanesoluti/01_Projetos/Carteira_Projetos.base) lê `module: 01_Projetos + type: home` automaticamente.

## Convenções de nomenclatura (dentro do projeto)

Prefixos de notas (detalhe completo em [`PADRAO_INGESTAO.md`](../../../Sanesoluti/01_Projetos/PADRAO_INGESTAO.md)):

| Prefixo | Tipo | Dígitos | Pasta |
|---|---|---|---|
| `ADR-NNNN` | Architecture Decision Record | 4 | `01_Gestao/Decisoes_Tecnicas/` |
| `RF-NNN` | Requisito funcional | 3 | `02_Especificacoes/Requisitos_Funcionais/` |
| `RNF-NNN` | Requisito não-funcional | 3 | `02_Especificacoes/Requisitos_NaoFuncionais/` |
| `RR-NNN` | Requisito regulatório | 3 | `02_Especificacoes/Requisitos_Regulatorios/` |
| `UC-NNN` | Caso de uso | 3 | `02_Especificacoes/Casos_de_Uso/` |
| `TP-NNN` | Plano de teste | 3 | `06_Testes_Validacao/Planos_de_Teste/` |
| `TR-NNN` | Relatório de teste | 3 | `06_Testes_Validacao/Relatorios/` |
| `Ata_YYYY-MM-DD_Assunto` | Ata de reunião | data | `01_Gestao/Atas_Reunioes/` |

Após prefixo: `_CamelCase_Com_Underscores` (sem acentos). Ex: `ADR-0001_Escolha_MCU.md`, `RF-001_Comunicacao_BLE.md`.

## Frontmatter obrigatório em notas de projeto

```yaml
---
title: "Título legível"
created: YYYY-MM-DD
updated: YYYY-MM-DD
module: 01_Projetos
type: <tipo>              # adr | requisito | caso-de-uso | plano-de-teste | relatorio-de-teste | ata | release | certificacao | manual-usuario | referencia | home | readme
project: <NomeDoProjeto>  # nome da pasta, bate exatamente
status: rascunho          # rascunho | proposto | aprovado | aceito | substituido
tags: [<tags>]
---
```

Campos adicionais por `type` e exemplos completos: [`01_Projetos/PADRAO_INGESTAO.md`](../../../Sanesoluti/01_Projetos/PADRAO_INGESTAO.md).

O hook [`update-frontmatter.py`](../../hooks/update-frontmatter.py) atualiza `updated:` automaticamente a cada Edit/Write — não mexa manualmente.

## Erros comuns

- **Subpasta faltando**: algum diretório da estrutura canônica sumiu. Rode `python .claude/scripts/new_project.py --verify <Nome>` para diffar contra o template.
- **`project:` divergente**: o frontmatter ficou com `_Template_Projeto` após a cópia. O script cobre isso; se sobrou, é porque a nota foi criada fora do scaffolder — corrija na mão.
- **Nome com acento/espaço**: Obsidian aceita, mas quebra wikilinks curtos e o validador. Use só ASCII.
- **Projeto abandonado**: mova a pasta inteira para `99_Arquivo_Historico/` do próprio projeto ou para um `99_Arquivo_Historico/` raiz de `01_Projetos/`.

## Ver também

- [`PADRAO_INGESTAO.md`](../../../Sanesoluti/01_Projetos/PADRAO_INGESTAO.md) — perfis de frontmatter por tipo de documento
- [`_Template_Projeto/Home.md`](../../../Sanesoluti/01_Projetos/_Template_Projeto/Home.md) — dashboard de referência
- [`_Template_Projeto/_templates/`](../../../Sanesoluti/01_Projetos/_Template_Projeto/_templates/) — templates de ADR, Requisito, Teste
- [`Sanesoluti/CLAUDE.md`](../../../Sanesoluti/CLAUDE.md) — regras globais da vault
