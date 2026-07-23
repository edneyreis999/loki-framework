---
name: lf-agent-execution-evidence
description: Define provider-neutral agent execution evidence and its boundary from derived execution knowledge and run metrics, including typed identity, sanitized snapshots, completeness, runtime locators, exact-token provenance, explicit estimates, and liveness probes without private reasoning.
doc_id: "lf-agent-execution-evidence"
version: "2.0.0"
status: active
last_updated: "2026-07-23"
scope: "Provider-neutral agent execution evidence, metrics provenance, and liveness observation"
not_scope: "Private reasoning, provider account allocation, cost control, or functional status authority"
authority: "Approved Loki package policy and the invoking workflow's validated run envelope"
canonical_source: "skills/lf-agent-execution-evidence/SKILL.md"
intended_llm_task: "routing"
source_priority:
  - "approved human decisions and invoking workflow envelope"
  - "this skill and its current references"
  - "verified adapter observations for the correlated run"
  - "completion data and non-normative examples"
confidence: high
known_conflicts: []
replaced_by: null
when_to_use:
  - "Use when defining, collecting, reviewing, or validating execution evidence for an agent run."
  - "Use when an adapter must degrade evidence capability explicitly instead of fabricating IDs, transcripts, or token usage."
argument-hint: "[agent run, adapter capability, or evidence artifact]"
arguments:
  required: []
  optional:
    - agent_run
    - adapter_capability
    - evidence_artifact
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
  - unvalidated adapter capability presented as complete
  - raw or private-reasoning payload proposed for persistence
  - identity correlation cannot be verified
context: standard
agent: main
hooks: {}
paths:
  package_skill: "skills/lf-agent-execution-evidence/SKILL.md"
shell: bash
type: skill
---

# lf-agent-execution-evidence

## Purpose

Use this skill to keep machine-generated evidence for an agent execution
auditable without turning a runtime pointer, an inferred action sequence, or
private reasoning into a stronger claim than it is.

## Procedure

1. Keep the compact completion record separate from runtime identity and usage;
   the collector, not the executing agent, owns technical correlation.
2. Apply the typed identity, evidence, completeness, usage, and security rules
   in [evidence-contract.md](references/evidence-contract.md).
3. Persist evidence before any execution-knowledge cataloger runs. Knowledge
   may cite this manifest but never replace it or duplicate its snapshot.
4. Apply the collector's narrow write envelope, sanitization, atomic-write, and
   integrity rules in [collector-contract.md](references/collector-contract.md).
5. Select only capability states supported by the adapter record in
   [adapter-capability-matrix.md](references/adapter-capability-matrix.md).
6. Validate all dimensions independently. Do not promote an overall state to
   `complete` when any required dimension is degraded or its integrity fails.
7. Keep `agent_session_evidence` XML schema/shape `1` unchanged. Publish
   hierarchical run metrics separately as orchestrator-owned
   `builds/metrics/execution-metrics.json` schema `1`; the evidence collector
   may supply proven facts but never owns or rewrites that aggregate.
8. Immediately before a silence-based abort, interrupt, or cancel, require the
   adapter-observed liveness probe defined by the selected adapter record.

## Inputs

- A terminal completion record and the orchestrator's run/handoff context.
- Adapter capability, maturity, and version information when available.
- A runtime locator and an optional candidate snapshot.

## Outputs

- A provider-neutral evidence manifest or an explicit, typed gap.
- A sanitized snapshot only when the collector can produce one safely.
- Exact provenanced usage, or an explicit estimate/unavailability reason in
  the separate execution-metrics artifact.
- A typed liveness-probe observation before any silence-based policy stop.

## Limits

- Never persist raw or unredacted runtime payloads through this protocol.
- Never treat `run_id`, `agent_run_id`, `handoff_id`, agent identity, and
  runtime locators as interchangeable strings.
- Full or private chain-of-thought is unavailable. A declared reasoning summary
  and an inference from operational sequence are partial evidence only.
- Do not derive per-agent consumption from cumulative or account-window usage.
- Do not mix exact, estimated, cumulative, or account-window quantities.
- Do not introduce token/cost budgets or automatic cost stops; metrics are
  measurement and reporting only.
- Do not use a missing adapter capability as permission to invent an ID,
  transcript, token counter, or snapshot.

## Validation

- The entrypoint has exactly the three references listed above.
- Evidence uses only the five evidence states and reports every dimension.
- Payload-bearing manifests and snapshots have verified checksums and were
  atomically written.
- Adapter maturity and degradation are explicit.
- Exact tokens come only from a verified run-scoped adapter counter; estimates
  use only `utf8-byte-estimate-v1` and unavailable values carry a reason.

## Required Gates

- Changes to this package contract, collector, template, or validator are
  routed only through `loki-continuous-improvement` with
  `destination_scope: package`; the confirmed branch applies its scoped Writer,
  deterministic checks, independent Auditor, and any applicable approval.
- `<human_validation_gate>` before declaring behavior on
  `<consumer_runtime_surfaces>` validated.
