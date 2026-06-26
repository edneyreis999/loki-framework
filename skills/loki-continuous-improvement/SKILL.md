---
name: loki-continuous-improvement
description: Run the Loki `loki:continuous-improvement` command workflow in Codex. Use when promoting validated learnings into durable project context, Loki package artifacts, standards, commands, skills, agents, templates, validators, docs, manifest updates, or backlog.
when_to_use:
  - "Use when promoting validated learnings into durable project context or Loki package artifacts."
  - "Use when classifying candidates for standards, commands, skills, agents, templates, validators, docs, manifest updates, or backlog."
argument-hint: "[retrospective path, candidate learning, target surface]"
arguments:
  required: []
  optional:
    - retrospective_path
    - candidate_learning
    - target_surface
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
  - durable package policy promotion
  - command, skill, agent, template, validator, or manifest changes
  - broad normative change with cross-adapter impact
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-continuous-improvement/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:continuous-improvement
---

# loki-continuous-improvement

## Procedure

1. Read the installed command contract:
   [loki-continuous-improvement.md](references/command.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions, and resume
   contract.
3. Load the relevant Loki skills named by the command contract, especially
   `loki-retrospectiva-tecnica`, `loki-command-creator`,
   `loki-agent-creator`, and `loki-skill-creator`.
4. Treat this skill as the Codex entrypoint for the command name
   `loki:continuous-improvement`.

## Limits

- Do not promote transient phase evidence into durable rules without the gates
  required by the command contract.
- Do not edit `.agents/**` or `.codex/**` unless the user explicitly asks for
  installation or synchronization.
