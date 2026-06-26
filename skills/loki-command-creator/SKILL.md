---
name: loki-command-creator
description: Create or revise Loki commands, Claude Code custom commands, or Codex reusable command-like workflows. Use when a workflow has explicit inputs, outputs, gates, allowed writes, forbidden writes, handoffs, validators, and resumable state; also use when deciding whether a change belongs as a command, skill, agent, template, standard, or backlog item.
when_to_use:
  - "Use when creating or revising Loki commands, Claude Code custom commands, or Codex reusable command-like workflows."
  - "Use when a workflow needs explicit inputs, outputs, gates, writes, handoffs, validators, and resumable state."
  - "Use when deciding whether a change belongs as a command, skill, agent, template, standard, or backlog item."
argument-hint: "[workflow goal, inputs, outputs, writes, gates]"
arguments:
  required: []
  optional:
    - workflow_goal
    - inputs
    - outputs
    - writes
    - gates
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
  - command contract changes
  - durable workflow policy
  - complex gates, validators, or resume state
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-command-creator/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:continuous-improvement
  - manual-framework-evolution
---

# loki-command-creator

## When To Use

Use para criar ou revisar um comando Loki, comando Claude Code, ou workflow invocavel equivalente em Codex quando o trabalho tiver inicio, fim, entradas, saidas, gates e estado retomavel.

Use tambem quando houver duvida se uma melhoria deve virar `command`, `skill`, `agent`, `template`, `standard` ou backlog.

## Procedure

1. Leia primeiro `loki-taxonomy.md`, `command-handoff-contracts.md`, `validators-and-gates.md`, `feature-artifact-structure.md`, `continuous-improvement-design.md`, `docs/package-authoring-guardrails.md` e o `manifest.yaml` do pacote local.
2. Procure comandos existentes em `commands/` e no catalogo aprovado antes de criar um novo nome.
3. Classifique a necessidade:
   - `command` quando for fluxo invocavel com orquestracao, estado, handoffs, outputs e gates.
   - `skill` quando for procedimento tecnico reutilizavel que outros fluxos chamam.
   - `agent` quando houver julgamento especialista, isolamento de contexto ou proposta `read-only`/`proposal-only`.
   - `template` quando o valor principal for formato de saida repetivel.
4. Rode preflight de autoria quando o destino for o proprio pacote: namespace, artefato correto, docs/manifest impactados, referencias externas classificadas e validacoes finais.
5. Defina o contrato minimo do comando: `name`, `purpose`, `inputs`, `outputs`, `allowed_writes`, `forbidden_writes`, `required_skills`, `handoffs`, `validators`, `human_gates`, `stop_conditions` e `resume_contract`.
6. Escreva o comando como fluxo curto e auditavel. Mova detalhes tecnicos para skills e exemplos longos para templates ou referencias.
7. Nao embuta regras de projeto, engine ou framework em comandos core. Quando retrospectivas tecnicas revelarem padroes de uma tecnologia, gere ou atualize uma skill especializada e referencie-a em `<technology_required_skills>`.
8. Use placeholders genericos para fronteiras do consumidor: `<consumer_runtime_surfaces>`, `<sensitive_write_patterns>`, `<domain_ids>` e `<human_validation_gate>`.
9. Trate Claude Code e Codex como adaptadores diferentes:
   - Claude Code: comandos antigos em `.claude/commands/*.md` ainda funcionam, mas skills sao preferidas quando o workflow precisa de arquivos de apoio, argumentos, controle de invocacao, ferramentas pre-aprovadas ou execucao em subagente.
   - Codex: comandos slash sao principalmente controle de sessao. Para workflows reutilizaveis, prefira skills; prompts customizados locais estao depreciados. Use `AGENTS.md` para instrucao duravel de projeto.
10. Inclua placeholders de argumentos somente quando o comando for realmente invocado por texto. Para Claude Code, use `$ARGUMENTS`; para Codex, prefira skill com `description` clara e entradas documentadas.
11. Modele gates antes de modelar escrita. Toda escrita sensivel deve ter owner unico, escopo permitido, validator e criterio de parada.
12. Para comandos Loki, preserve a politica core agnostica: superficies do consumidor, escritas sensiveis, IDs de dominio e validacoes humanas devem permanecer como placeholders ate uma skill especializada resolver a tecnologia.
13. Atualize `manifest.yaml` apenas quando o novo comando for aceito no pacote local.

## References

- Read [command-contract-template.md](references/command-contract-template.md) when drafting a new command contract, auditing contract completeness, or citing the external Claude Code/Codex research basis.

## Quality Checklist

- O comando nao duplica comando existente.
- O nome e curto, consistente com o namespace pretendido e nao corrige namespace historico fora de escopo.
- A descricao explica quando usar e quando nao usar.
- `allowed_writes` e `forbidden_writes` sao explicitos.
- O fluxo separa leitura paralela de escrita serializada.
- Handoffs retornam proposta, nao aplicam mudanca direta.
- O output e revisavel em Markdown/YAML.
- Validadores automaticos nao substituem gates humanos.
- O comando aponta para skills tecnicas em vez de reexplicar todo o dominio.
- Se o comando for empacotado, a mudanca respeita `docs/package-authoring-guardrails.md`.
- A mudanca em command consolidado tem `technical-review` ou `approval`.

## Inputs

- Demanda do usuario.
- Blueprint aprovado.
- Manifesto do pacote local.
- Comandos, skills, agents e templates existentes.
- Pesquisa atual de Claude Code ou Codex quando a superficie da plataforma estiver em duvida.

## Outputs

- Novo comando ou revisao de comando em Markdown.
- Contrato de entradas, saidas, writes, validators e gates.
- Registro no `manifest.yaml` quando aprovado.
- Lista de validacoes de pacote quando o destino for componente consolidado.
- Backlog quando a demanda nao for comando.

## Limits

- Nao instalar automaticamente em `.claude/**` ou `.agents/**`.
- Nao promover aprendizado isolado para command sem fonte, escopo e gate.
- Nao criar comando para substituir uma skill tecnica simples.
- Nao criar comando que permita escrita sensivel sem owner, validator e approval.
- Nao promover aprendizado tecnico de retrospectiva para command core; crie ou atualize skill especializada.

## Required Gates

- `technical-review` para mudanca em comando, skill, agent, template, validator ou doc consolidado.
- `approval` para nova politica duradoura, instalacao, escrita sensivel ou promocao normativa.
- `<human_validation_gate>` quando o comando altera ou valida comportamento em `<consumer_runtime_surfaces>`.
