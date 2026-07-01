---
name: loki-tech-analysis
description: Run the Loki `loki:tech-analysis` command workflow in Codex. Use when producing evidence-based technical analyses from briefs, feedback, specs, source paths, runtime questions, source maps, decision matrices, validators, gates, and handoff to action planning.
when_to_use:
  - "Use when running loki:tech-analysis to produce evidence-based technical analysis."
  - "Use when the output needs source maps, fact/hypothesis separation, decision matrices, validators, gates, and action-plan handoff."
argument-hint: "[brief, source paths, scope, destination]"
arguments:
  required: []
  optional:
    - brief
    - source_paths
    - scope
    - destination
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
  - architecture or security risk
  - conflicting multi-source evidence
  - irreversible or high-impact recommendation
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-tech-analysis/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:tech-analysis
---

# loki-tech-analysis

## Procedure

1. Read the installed command contract:
   [loki-tech-analysis.md](references/command.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions, and resume
   contract.
3. Load `lf-tech-analysis-authoring` before creating or reviewing the
   analysis artifact.
4. Use `lf-template-library` when writing a technical analysis file.
5. Treat this skill as the Codex entrypoint for the command name
   `loki:tech-analysis`.

## Limits

- Do not write runtime, engine, framework, generated data, or sensitive
  consumer surfaces during analysis.
- Do not make recommendations without evidence or clearly labeled inference.
