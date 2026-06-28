---
name: loki-knowledge-extraction-analysis
description: Orchestrate the Loki `loki:knowledge-extraction-analysis` command workflow in Codex. Use when analyzing external frameworks, commands, skills, operational rules, instruction documents, examples, or prompt artifacts by first extracting external learnings, then auditing Loki impact, then consolidating traceable recommendations for continuous improvement.
when_to_use:
  - "Use when orchestrating external knowledge extraction, Loki impact audit, and final consolidation."
  - "Use when comparing external commands, skills, frameworks, rules, instructions, examples, or prompt artifacts against Loki artifacts through staged skills."
  - "Use when the output should feed loki:continuous-improvement with detailed, traceable, implementable recommendations or a clear no-learning conclusion."
argument-hint: "[external artifact paths, Loki context, destination]"
arguments:
  required: []
  optional:
    - external_artifacts
    - loki_context
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
  - many external artifacts or long instruction sets
  - incomplete Loki context or missing operational inventory
  - conflicting external patterns and Loki package policy
  - recommendations that could alter durable Loki commands, skills, agents, templates, docs, validators, or manifest
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-knowledge-extraction-analysis/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:knowledge-extraction-analysis
  - loki:continuous-improvement
  - loki-external-knowledge-extraction
  - loki-framework-impact-audit
---

# loki-knowledge-extraction-analysis

## Procedure

1. Read the installed command contract:
   [loki-knowledge-extraction-analysis.md](references/command.md).
2. Read the output contract:
   [output-contract.md](references/output-contract.md).
3. Keep the original full contract available for compatibility checks only:
   [knowledge-extraction-analysis-contract.md](references/knowledge-extraction-analysis-contract.md).
   Do not load it by default unless resolving a conflict or auditing that the
   split still preserves source specificity.
4. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions, and resume
   contract.
5. Load `loki-external-knowledge-extraction` and produce an
   `external_extraction` handoff before auditing Loki impact.
6. Load `loki-framework-impact-audit` with the `external_extraction` handoff.
   That skill uses available Loki inventory or visible package artifacts,
   selects impacted Loki artifacts, audits them individually, and returns
   `impact_audit`.
7. Consolidate `external_extraction` and `impact_audit` into the final report.
8. Apply the mandatory non-forcing principle: only recommend changes that solve
   a real problem, are compatible or consciously rejectable, can become a
   concrete change, have traceable origin, and do not duplicate Loki without a
   specific clarity or economy gain.
9. Use exactly the required output structure from `output-contract.md`,
   including the special structure for cases with no useful learning.
10. Treat this skill as the Codex entrypoint for the command name
   `loki:knowledge-extraction-analysis`.

## Inputs

- External artifacts: frameworks, commands, skills, instruction documents,
  operational rules, examples, prompt artifacts, or documentation.
- `external_extraction` from `loki-external-knowledge-extraction`.
- `impact_audit` from `loki-framework-impact-audit`.
- Optional destination for the generated analysis.

## Outputs

- A detailed Markdown knowledge-extraction analysis for the Loki Framework.
- Consolidated traceable learnings classified as `adotar`, `adaptar`,
  `rejeitar`, `ja contemplado`, `investigar`, or `sem aprendizado util`.
- Concrete recommendations for `loki-continuous-improvement`, or an explicit
  no-useful-learning conclusion.

## Limits

- Do not force recommendations just to populate the analysis.
- Do not apply package, consumer documentation, runtime, or installation changes
  directly from this skill.
- Do not claim Loki coverage unless it is visible in the provided context,
  available Loki inventory, or files actually read.
- Do not use an external plan, blueprint, `.agents/**`, `.claude/**`, or
  workspace-specific path as a normative dependency for this packaged skill.

## Required Gates

- `technical-review` for any later change to a Loki command, skill, agent,
  template, validator, consolidated doc, or `manifest.yaml`.
- `approval` for any later normative promotion, installation, synchronization,
  or sensitive write.
