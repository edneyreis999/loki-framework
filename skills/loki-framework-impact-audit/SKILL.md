---
name: loki-framework-impact-audit
description: Audit how extracted external learnings may impact concrete Loki Framework artifacts, workflows, commands, skills, templates, docs, validators, or manifest entries. Use after loki-external-knowledge-extraction or when comparing candidate learnings against available Loki inventory, visible package artifacts, or docs/operational-inventory.md when present.
when_to_use:
  - "Use after extracting external learnings to identify impacted Loki artifacts and workflows."
  - "Use when auditing Loki deltas, gaps, redundancies, conflicts, and concrete change opportunities."
  - "Use when the analysis must inspect available Loki inventory or visible package artifacts before recommending Loki changes."
argument-hint: "[external_extraction, Loki package root, scope]"
arguments:
  required: []
  optional:
    - external_extraction
    - loki_package_root
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
  - incomplete operational inventory
  - candidate changes affect durable package artifacts
  - conflicting evidence across Loki artifacts
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-framework-impact-audit/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:knowledge-extraction-analysis
---

# loki-framework-impact-audit

## Procedure

1. Read the impact audit contract:
   [framework-impact-audit-contract.md](references/framework-impact-audit-contract.md).
2. Inspect the available Loki inventory before selecting artifacts to audit.
   Prefer `docs/operational-inventory.md` when running inside the package
   source and it is available. If installed in a consumer project without
   package docs, use visible commands, skills, templates, manifest data or
   provided context, and state the limitation.
3. Use the `external_extraction` handoff as input. Do not re-extract external
   artifacts unless evidence is missing or contradictory.
4. Select Loki artifacts with potential impact `alto`, `medio`, or `incerto`
   for individual audit. Mention `baixo` only when useful; exclude `nenhum
   impacto relevante` with a brief reason.
5. Audit each selected artifact independently. Use parallel read-only handoffs
   when available; otherwise keep separate subsections.
6. Produce an `impact_audit` handoff with workflow impacts, individual reports,
   deltas, gaps, redundancies, conflicts, concrete opportunities, risks, and
   validation tests.

## Outputs

- Loki artifacts considered and impact level.
- Workflow impact analysis.
- Individual impact reports per selected artifact.
- Consolidated deltas, gaps, redundancies, conflicts, and opportunities.
- Recommended classification per artifact: `adotar`, `adaptar`, `rejeitar`,
  `ja contemplado`, `investigar`, or `nao alterar`.

## Limits

- Do not promote or apply changes directly.
- Do not invent files, workflows, or relationships not visible in the inventory
  or files actually read.
- Do not treat external popularity or recurrence as proof of Loki fitness.
- Do not collapse conclusions from different artifacts without traceability.
