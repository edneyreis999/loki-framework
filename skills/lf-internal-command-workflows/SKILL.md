---
name: lf-internal-command-workflows
description: Route internal-only Loki package command workflows in Codex. Use only inside the Loki Framework package when invoking maintenance, knowledge extraction, continuous improvement, or self-healing commands that are not installed for consumer projects.
when_to_use:
  - "Use inside the Loki Framework package when routing loki:continuous-improvement, loki:knowledge-extraction-analysis, or loki:self-healing."
  - "Use when an internal package workflow must load internal-only Loki skills."
argument-hint: "[internal loki command name, command arguments]"
arguments:
  required: []
  optional:
    - command_name
    - command_arguments
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - internal package maintenance
  - self-healing or continuous-improvement workflow
  - command contract requires internal-only skills
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/lf-internal-command-workflows/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:continuous-improvement
  - loki:knowledge-extraction-analysis
  - loki:self-healing
---

# lf-internal-command-workflows

## Purpose

Route Loki command workflows that maintain or audit the Loki Framework package
itself. This skill is `internal-only` and must not be installed by the
`consumer` profile.

## Command Map

- `loki:continuous-improvement`: read `commands/loki-continuous-improvement.md`,
  then load the skills named by that command contract.
- `loki:knowledge-extraction-analysis`: read
  `commands/loki-knowledge-extraction-analysis.md`, then load
  `loki-knowledge-extraction-analysis`.
- `loki:self-healing`: read `commands/loki-self-healing.md`, then load
  `loki-self-healing`.

## Procedure

1. Match the request to one command in the command map.
2. Read the matching command contract from `commands/`.
3. Load only the required skills named by that command contract.
4. Follow the command's inputs, outputs, write boundaries, validators, gates,
   stop conditions, and resume contract.
5. Keep all writes inside the approved package task or maintenance scope.

## Limits

- Do not route consumer-facing commands from this skill.
- Do not install this skill into consumer projects.
- Do not treat generated installation targets as package source material.
