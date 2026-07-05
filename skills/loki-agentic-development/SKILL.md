---
name: loki-agentic-development
description: Run the Loki `loki:agentic-development` integrated workflow in Codex. Use when turning a simple demand into agentic analysis, material decision gates, action planning, autonomous phase execution, evidence, retrospectives, digest, and backlog while preserving `loki:run-plan` for manual execution.
when_to_use:
  - "Use when running loki:agentic-development from Codex."
  - "Use when a demand should go through agentic analysis, plan generation, autonomous execution, evidence, retrospectives, digest, and backlog."
argument-hint: "[demand path or text, run directory, optional scope]"
arguments:
  required: []
  optional:
    - demand
    - run_directory
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
  - multi-agent analysis with material conflicts
  - autonomous execution across multiple planned phases
  - unresolved decision gates before action planning
  - target file conflicts between agent runs
  - high-risk runtime or integration work delegated by a generated plan
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-agentic-development/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:agentic-development
---

# loki-agentic-development

## Procedure

1. Read the installed command contract:
   [loki-agentic-development.md](references/command.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions, and resume
   contract.
3. Load `lf-agentic-orchestration` before selecting agents, writing XML state,
   running fan-out, processing decision gates, or producing digest/backlog.
4. Use `loki-human-decision-preflight`, `loki-generate-action-plan`,
   `loki-run-plan`, and `loki-retrospectiva-tecnica` only as directed by the
   command contract and active run state.
5. Treat this skill as the Codex entrypoint for the command name
   `loki:agentic-development`.

## Limits

- Do not replace or mutate `loki:run-plan`; use it as the manual and autonomous
  phase executor.
- Do not continue if `lf-agentic-orchestration` is unavailable in the active
  skill set.
- Do not ask new human questions during autonomous plan execution. Record
  blockers or post-execution backlog items instead.
- Do not install or write into `.agents/**`, `.codex/**`, or `.claude/**`
  without explicit approval.
- Do not declare runtime, integration, persisted state, perceptible behavior or
  generated output validated without the required validator and human gate.
