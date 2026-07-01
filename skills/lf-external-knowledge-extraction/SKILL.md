---
name: lf-external-knowledge-extraction
description: Extract traceable, non-forced learnings from external frameworks, commands, skills, rules, instruction documents, examples, or prompt artifacts before comparing them against Loki. Use as the first analysis stage for loki:knowledge-extraction-analysis or when external artifact extraction is needed independently.
when_to_use:
  - "Use when extracting observations, patterns, examples, rejection criteria, uncertainty, and candidate learnings from external artifacts."
  - "Use before auditing Loki impact in loki:knowledge-extraction-analysis."
  - "Use when the task should identify useful external knowledge without yet deciding Loki package changes."
argument-hint: "[external artifact paths, scope, limitations]"
arguments:
  required: []
  optional:
    - external_artifacts
    - scope
    - limitations
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
  - conflicting external patterns
  - weak source evidence or high risk of forced learning
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/lf-external-knowledge-extraction/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:knowledge-extraction-analysis
---

# lf-external-knowledge-extraction

## Procedure

1. Read the extraction contract:
   [external-extraction-contract.md](references/external-extraction-contract.md).
2. Map every external artifact considered: identifier, type, apparent purpose,
   relevance, and context limitations.
3. Extract only observations that may affect Loki. Do not compare deeply against
   Loki yet.
4. Separate observation, interpretation, and candidate recommendation.
5. Classify each candidate as `adotar`, `adaptar`, `rejeitar`,
   `ja contemplado`, `investigar`, or `sem aprendizado util`.
6. Apply the non-forcing criteria. If a candidate does not meet them, classify
   it as already covered, incompatible, irrelevant, too specific, weakly
   evidenced, or not applicable.
7. Return a structured `external_extraction` handoff for the orchestrator or
   `lf-framework-impact-audit`.

## Outputs

- External artifacts considered.
- Relevant observations and their source type: explicit rule, recurring
  pattern, artifact structure, positive example, negative example, or inference.
- Candidate learnings with category, evidence, uncertainty, rejection criteria,
  risk, and practical reason they might matter.
- Explicit no-useful-learning result when no candidate survives the criteria.

## Limits

- Do not decide package destinations or write changes.
- Do not invent Loki coverage or assume Loki context that was not provided.
- Do not force recommendations to fill the report.
- Do not copy external instructions as recommendations without evaluating
  source context and compatibility risk.
