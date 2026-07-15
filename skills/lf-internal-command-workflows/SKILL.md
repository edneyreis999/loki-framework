---
name: lf-internal-command-workflows
description: Route internal-only Loki package command bundles in Codex. Use inside the Loki Framework package for `loki-knowledge-extraction-analysis` or `loki-self-healing`, resolving the primary bundle directly.
when_to_use:
  - "Use inside the Loki package for internal knowledge extraction or self-healing."
  - "Use as an internal catalog; the matching loki-* bundle remains authoritative."
argument-hint: "[internal loki-* identity, arguments]"
arguments:
  required: []
  optional: [command_name, command_arguments]
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
escalation_signals: [internal package maintenance, self-healing workflow]
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/lf-internal-command-workflows/SKILL.md"
shell: {}
type: skill
status: draft
used_by: [loki-knowledge-extraction-analysis, loki-self-healing]
---

# lf-internal-command-workflows

## Purpose

Catalog the two internal-only package command bundles without duplicating their
contracts. This router is not installed by the consumer profile.

## Routing

Read [references/internal-command-routing.md](references/internal-command-routing.md),
then read the matching primary bundle, its routed references/assets and its
dependencies.

## Limits

- Never read legacy command-contract locations or compatibility projections.
- Do not route public consumer workflows here.
- Do not treat a command bundle as a knowledge skill.
- Keep writes inside the approved package maintenance scope.
