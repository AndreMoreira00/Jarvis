#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

let input = "";
try {
  input = fs.readFileSync(0, "utf8");
} catch {}

let payload = {};
try {
  payload = JSON.parse(input || "{}");
} catch {}

const cwd = payload.cwd || process.cwd();
const skillsDir = path.join(cwd, ".claude", "skills");

let skills = [];
try {
  skills = fs
    .readdirSync(skillsDir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .sort();
} catch {}

const skillsLine = skills.length
  ? skills.join(", ")
  : "(nenhuma skill local encontrada em .claude/skills/)";

const rules = `<project-rules>
REGRAS OBRIGATORIAS DO PROJETO (injetadas via hook UserPromptSubmit):

1. CONSULTA DE SKILLS — Antes de planejar, codar ou chamar tools, revise as skills do projeto e invoque a que combinar com a tarefa via Skill tool.
   Skills locais disponiveis em .claude/skills/: ${skillsLine}

2. DOCUMENTACAO — Ao final de qualquer alteracao no codigo, ou quando o usuario citar referencias/links/conceitos, atualize docs_projeto/ com o que foi mudado ou aprendido. Nao termine a tarefa sem isso.

3. CINCO PERGUNTAS MINIMAS — Use AskUserQuestion com no minimo 5 perguntas distintas cobrindo: (a) escopo/intencao, (b) restricoes tecnicas, (c) preferencias de estilo/arquitetura, (d) criterios de aceite, (e) edge cases. Excecao: leitura factual pura (ex: "mostre o git status", "leia esse arquivo").

4. ADVOGADO DO DIABO — Em todo prompt nao-trivial, critique a abordagem proposta, aponte riscos, invalide premissas fracas e apresente pelo menos 2 caminhos alternativos com tradeoffs explicitos antes de executar.

5. QUALIDADE ARQUITETURAL — Atente para: complexidade ciclomatica de funcoes, organizacao de pastas, separacao de responsabilidades, arquitetura limpa, abstracao em arquivos coesos. Recuse implementar funcoes monoliticas; quebre em modulos.

6. INGESTAO DE REFERENCIAS — Se o usuario citar URL, biblioteca, padrao ou conceito que voce nao domina, use defuddle/WebFetch para ingerir e salve um resumo em docs_projeto/referencias/<slug>.md antes de prosseguir.
</project-rules>`;

process.stdout.write(rules);
process.exit(0);
