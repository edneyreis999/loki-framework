---
name: lf-internal-command-workflows
description: Route Loki package-maintenance command bundles from either installation profile. Use for `loki-knowledge-extraction-analysis` or `loki-self-healing`, resolving the primary bundle directly while preserving package-only write boundaries.
when_to_use:
  - "Use for Loki package knowledge extraction or self-healing when the matching bundle is available."
  - "Use as a maintenance catalog; the matching loki-* bundle remains authoritative."
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
hooks: {}
paths:
  package_skill: "skills/lf-internal-command-workflows/SKILL.md"
shell: bash
type: skill
status: draft
used_by: [loki-knowledge-extraction-analysis, loki-self-healing]
---

# lf-internal-command-workflows

## Purpose

Catalog the two package-maintenance command bundles without duplicating their
contracts. The router is installed in both profiles, but availability never
authorizes writes against consumer docs, runtime, configuration, data or assets.

## Routing

Read [references/internal-command-routing.md](references/internal-command-routing.md),
then read the matching primary bundle, its routed references/assets and its
dependencies.

## Limits

- Never read legacy command-contract locations or compatibility projections.
- Do not route public consumer workflows here.
- Do not treat a command bundle as a knowledge skill.
- Require package root, `destination_scope: package`, exact targets, owner,
  validators and gates before mutating any consolidated package artifact.
- A transient analysis report may use only the exact destination allowed by
  its primary bundle and never grants package mutation or consumer/runtime
  authority.
- Without a valid package envelope, return proposal or `blocked` for package
  mutation; any transient report remains governed exclusively by the exact
  write envelope of its primary bundle.
