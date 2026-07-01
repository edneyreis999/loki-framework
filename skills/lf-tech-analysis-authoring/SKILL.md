---
name: lf-tech-analysis-authoring
description: Create or review evidence-based Loki technical analyses from briefs, feedback, specs, source paths, or runtime questions. Use when producing or improving `loki:tech-analysis` outputs, source maps, fact/hypothesis separation, decision matrices, external research gates, validators, human gates, and handoff to `loki:generate-action-plan`.
when_to_use:
  - "Use when creating or reviewing evidence-based Loki technical analyses."
  - "Use when producing source maps, fact/hypothesis separation, decision matrices, research gates, validators, or planning handoff."
  - "Use when improving outputs from loki:tech-analysis."
argument-hint: "[brief, source paths, scope, forbidden writes, destination]"
arguments:
  required: []
  optional:
    - brief
    - source_paths
    - scope
    - forbidden_writes
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
  - conflicting evidence
  - architecture or security decision
  - irreversible or high-impact recommendation
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/lf-tech-analysis-authoring/SKILL.md"
shell: {}
---

# lf-tech-analysis-authoring

## Procedure

1. Confirm the analysis input: brief, PRD, NSD, feedback, direct request,
   source paths, in-scope surfaces, out-of-scope surfaces, forbidden writes and
   expected artifact destination.
2. Load only the context needed for safe analysis. Read consumer `AGENTS.md` or
   `CLAUDE.md` when entering a project root, and use `lf-index-navigator`
   when durable consumer docs in `/docs` are relevant.
3. Read local primary sources before interpretive docs: target files, runtime
   configuration, schemas, IDs, contracts, generated data or integration
   surfaces. Then read specs, notes or prior artifacts needed to explain intent.
4. Build a source map while reading. Separate facts, inferences, hypotheses and
   open questions before recommending any approach.
5. For each material hypothesis, run one or two targeted local reads/searches
   that can confirm or reject it. Discard rejected hypotheses; keep unresolved
   ones as risks or questions.
6. Apply the research gate from
   [technical-analysis-contract.md](references/technical-analysis-contract.md)
   after local context is mapped, not before.
7. Compare approaches with a decision matrix: local/native behavior,
   dependency/plugin/framework behavior, custom implementation, and defer or
   block when applicable.
8. Declare affected runtime surfaces, integration points, state contracts,
   validators, human gates, risks, affected docs and recommendation.
9. Use `templates/technical-analysis-template.md` when writing the artifact.
10. Run the contract validators before declaring the analysis ready.

## Non-Negotiables

- Do not invent file names, line numbers, APIs, IDs, methods, approvals or
  documentation references.
- Do not make a technical recommendation without evidence or a clearly labeled
  inference.
- Do not let external research override local consumer sources. External
  sources explain technologies; local files define the current project state.
- Do not write runtime, engine, framework, generated data or sensitive consumer
  surfaces during analysis.
- Do not declare behavior, integration, persistence, generated output or runtime
  state validated without the required automated validator or human gate.
- Stop and ask when minimum sources are insufficient for an executable
  handoff.

## Required Contract

Read [technical-analysis-contract.md](references/technical-analysis-contract.md)
when creating or reviewing a Loki technical analysis. It defines the evidence
model, output fields, research gate, validators, stop conditions and handoff
expectations.

Use this package-root template when writing the artifact:

- `templates/technical-analysis-template.md`

## Output Standard

The analysis must be useful as direct input to `loki:generate-action-plan`.
Another agent should be able to inspect the sources, understand the chosen
approach, see unresolved questions, and convert the recommendation into
executable tasks without relying on conversation memory.
