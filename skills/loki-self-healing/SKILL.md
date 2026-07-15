---
name: loki-self-healing
description: Run the Loki `loki:self-healing` command workflow through an installable adapter projection. Use when auditing and automatically correcting internal Loki package artifacts from a specific file, directory, workflow, or staged-file set; it understands the package, analyzes files individually, applies scoped fixes to the working tree, and never stages or commits changes.
when_to_use:
  - "Use when the user asks Loki to self-heal, audit, or automatically correct internal Loki package artifacts."
  - "Use when the input is a file, directory, workflow name, or staged files that should be checked against Loki package standards."
  - "Use when corrections should be applied directly to the working tree without git add or commit."
argument-hint: "[file path, directory path, workflow name, staged]"
arguments:
  required: []
  optional:
    - file_path
    - directory_path
    - workflow_name
    - staged
    - scope
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: frontier_reasoning
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - broad package scope
  - staged-file input with working tree divergence
  - corrections affecting commands, skills, agents, templates, docs, scripts, or manifest
  - conflicting package rules or incomplete operational inventory
context: standard
agent: main
hooks: []
paths:
  package_projection: "skills/loki-self-healing/SKILL.md"
  command_contract: "commands/loki-self-healing.md"
shell: {}
type: command
projection: installable-skill
command_name: loki:self-healing
status: draft
used_by:
  - loki:self-healing
---

# loki-self-healing

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: scope_input
    input_type: string
    requirement: required
    description: Arquivo, diretório, workflow Loki ou staged.
```

## Objetivo

Você executa o Loki Self-Healing para manutenção interna do Loki Framework.

Objetivos:

- Auditar artefatos internos do pacote Loki contra os padrões do próprio pacote.
- Nunca fazer stage, commit, reset, checkout nem alterar o índice git.
- Encerrar com um relatório revisável para que o usuário revise o diff e faça o stage manualmente.

## Conceitos do Framework

### Classificação operacional

- Agentes são contratos em `agents/**` ou suas projeções de adaptador.
- Comandos usam `loki:` em `commands/**` ou `loki-` em uma projeção
  instalável `skills/loki-*/SKILL.md`.
- Skills operacionais usam `lf-` ou um namespace explícito de domínio ou
  tecnologia.

A identidade operacional prevalece sobre diretório, extensão e formato de
instalação. Se `skills/loki-<stem>/SKILL.md` possuir
`commands/loki-<stem>.md`, classifique o par como **Comando**. O `SKILL.md` é
somente a projeção instalável do comando e nunca deve ser classificado ou
reescrito como conhecimento de skill.

Ausência do comando pareado para um artefato `loki-*` é blocker de estrutura;
não autoriza classificá-lo como skill.

### Separação de responsabilidades

#### Comandos

Trate comandos como orquestradores.

Eles coordenam:

- Input
- Execution
- Response

#### Skills

Trate skills como conhecimento especializado reutilizável.

Nunca transforme skills em mini-orquestradores.

#### Agentes

Trate agentes como personas especializadas em conhecimento.

## Referências obrigatórias

Antes de analisar qualquer artefato, carregue as referências correspondentes.
Classifique cada artefato como:

- Agente
- Comando
- Skill

- Para comandos, inclusive `skills/loki-*/SKILL.md`, leia:
  - references/how-to-improve-command.md
- Para skills `lf-*` ou de domínio/tecnologia, leia:
  - references/how-to-improve-skills.md
- Para agentes, leia:
  - references/how-to-improve-agents.md

Nunca carregue `how-to-improve-skills.md` para uma projeção `loki-*` com
comando correspondente.

## Workflow

### Etapa 1 — Resolver entrada e package root

- Receba scope_input como:
  - arquivo;
  - diretório;
  - workflow Loki.
- Infira loki_root subindo a partir do escopo até encontrar:
  - manifest.yaml
  - commands/
  - skills/
  - agents/
  - docs/

### Etapa 2 — Resolver escopo

#### Se o escopo for um arquivo

Selecione:

- o arquivo;
- seus metadados obrigatórios relacionados.

#### Se o escopo for um diretório

Enumere todos os arquivos do pacote sob esse diretório.

#### Se o escopo for um workflow

Mapeie:

- command;
- projeção instalável do command em `skills/loki-*/SKILL.md`;
- helper skills;
- referências;
- templates;
- documentação;
- manifest;
- inventário;
- command router;
- instalador relacionados.

### Etapa 3 — Ler contexto global

Antes de escrever qualquer arquivo, leia no mínimo:

- README.md
- install-scopes.json
- docs/operational-inventory.md
- manifest.yaml
- docs/package-authoring-guardrails.md

Além disso, leia todos os artefatos relacionados ao escopo:

- comandos;
- skills;
- referências;
- templates;
- documentação;
- scripts;
- agentes;
- instalador.

### Etapa 4 — Classificar install scope

Antes de qualquer escrita em:

- commands/**
- skills/**

Leia:

- install-scopes.json

Classifique cada comando ou skill como:

- internal-only
- both
- consumer-only
- unclassified-blocker

Regras:

- Nunca edite arquivos classificados como unclassified-blocker.
- Registre-os como bloqueados.
- Para artefatos both, aplique o checklist de neutralidade antes de qualquer correção.

### Etapa 5 — Montar source map

Registre:

- escopo resolvido;
- arquivos candidatos;
- install scope de comandos e skills;
- fontes globais lidas;
- relações esperadas com:
  - manifest;
  - inventário;
  - documentação;
  - instalador;
  - referências;
- validators aplicáveis;
- forbidden writes.

### Etapa 6 — Analisar arquivos

Analise cada arquivo individualmente considerando:

- clareza;
- contrato;
- metadata;
- referências;
- sincronização;
- limites de autonomia;
- gates;
- validators;
- forbidden writes;
- neutralidade de both;
- redundância;
- conflitos;
- output actionability.

Execução:

- Utilize handoffs read-only por arquivo ou grupo.
- Handoffs retornam apenas:
  - achados;
  - propostas.
- Handoffs nunca escrevem arquivos.
- Se não houver paralelismo seguro, mantenha subseções independentes por arquivo na thread principal.

### Etapa 7 — Classificar achados

Classifique cada achado como:

#### corrigir agora

Mudança:

- clara;
- escopada;
- verificável;
- coerente com as regras do pacote;
- de baixo risco.

#### nao alterar

Quando:

- já estiver coberto;
- ou a mudança apenas adicionaria ruído.

#### investigar

Quando:

- houver potencial;
- mas faltar evidência;
- ou o escopo for amplo demais.

#### fora de escopo

Quando não for obrigatório para manter consistência.

#### bloqueado

Quando depender de:

- decisão humana;
- pesquisa externa;
- forbidden write.

Aplique somente os achados classificados como corrigir agora.
Os achados investigar devem aparecer no relatorio final.

### Etapa 8 — Aplicar correções

Antes de escrever:

- consolide todos os achados.

Depois:

- escreva serialmente;
- utilize o menor patch coerente;
- preserve o estilo do pacote;
- nunca permita dois handoffs escreverem o mesmo arquivo em paralelo;
- não amplie silenciosamente o escopo.

A única exceção é quando:

- allow_required_consistency_files for verdadeiro;
- e arquivos obrigatórios de consistência precisarem ser atualizados.

## Política de escrita

### Allowed writes

É permitido escrever apenas em:

- commands/**
- skills/**
- agents/**
- codex/agents/**
- templates/**
- docs/**
- README.md
- index.md
- manifest.yaml
- scripts/**

Também podem ser alterados arquivos obrigatórios de consistência do pacote, como:

- manifest;
- inventário;
- command workflow skill;
- instalador;

desde que a correção realmente exija isso.

### Forbidden writes

Nunca:

- executar git add;
- executar git commit;
- executar git reset;
- executar git checkout;
- alterar o índice git;
- escrever fora do package root;
- alterar runtime;
- alterar engine;
- alterar framework;
- alterar projeto consumidor;
- alterar arquivos fora do escopo sem necessidade de consistência.

### Stop conditions

Pare imediatamente e solicite decisão humana quando:

- o escopo não puder ser resolvido;
- o escopo sair do package root;
- a única correção possível exigir forbidden write;
- a correção depender de informação externa, pesquisa na web ou decisão de produto ausente;
- existir conflito interno sem critério claro;
- uma edição em commands/** ou skills/** depender de um install scope inexistente.

## Relatório final

Responda em Markdown contendo:

- escopo resolvido;
- fontes lidas;
- arquivos analisados;
- install scopes;
- achados classificados;
- correções aplicadas;
- arquivos alterados;
- validadores executados e respectivos resultados;
- falhas ou validadores não executados, com seus motivos;
- itens deliberadamente não alterados;
- riscos residuais;
- próximo passo do usuário: revisar o diff e fazer manualmente o stage dos arquivos que desejar manter.
