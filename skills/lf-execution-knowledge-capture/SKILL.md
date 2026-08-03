---
name: lf-execution-knowledge-capture
description: Capture provider-neutral execution knowledge from persisted sanitized completion and evidence artifacts without blocking implementation or promoting durable policy.
when_to_use:
  - "Use when loki-implement-feature reaches a checkpoint with material attempts, errors, recovery, validation, environment, handoff, liveness or state friction."
  - "Use when an orchestrator must reconcile captured, partial, failed, unsupported or skipped-nonmaterial knowledge state without waiting at final completion."
argument-hint: "[calling_workflow, run_directory, capture_id, persisted_source_refs, target_entry]"
arguments:
  required: [calling_workflow, run_directory, capture_id, persisted_source_refs, target_entry]
  optional: [agent_run_id, handoff_id, task_id, phase]
disable-model-invocation: false
user-invocable: false
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Use with execution-knowledge-cataloger when subagents are available; otherwise preserve the same synchronous and degraded-state contract."
  claude_code: "Use with execution-knowledge-cataloger as a background/scoped handoff when supported."
escalation_signals:
  - missing persisted completion or evidence source
  - target entry outside the approved run directory
  - raw payload or private reasoning in a source
context: standard
agent: main
hooks: {}
paths:
  package_skill: "skills/lf-execution-knowledge-capture/SKILL.md"
  capture_contract: "references/capture-contract.md"
shell: bash
type: skill
status: draft
used_by: [loki-implement-feature, execution-knowledge-cataloger]
---

# lf-execution-knowledge-capture

## Purpose

Preserve reusable operational knowledge while implementation is still fresh,
without making enrichment a prerequisite for task, phase or run completion.
Evidence and execution knowledge remain distinct: knowledge cites sanitized
completion/evidence records and never copies their snapshots.

## Procedure

1. At the normal task/agent checkpoint, persist the minimal sanitized
   completion/evidence envelope before any knowledge handoff.
2. Evaluate materiality using the shared contract. Record a reason when the
   work is intentionally `skipped-nonmaterial`.
3. When supported, invoke `execution-knowledge-cataloger` in parallel with an
   exact, unique target under
   `<run_directory>/execution-knowledge/entries/<capture-id>.xml`.
4. Continue implementation without waiting for enrichment. Reconcile its
   reference and state serially only at an existing checkpoint.
5. At the final checkpoint, do not wait for a non-terminal cataloger. Interrupt
   or cancel it and record `partial`, reason and `minimum_next_path`.
6. Validate an entry when present. Validation failure degrades the knowledge
   capture; it does not invalidate implementation already validated by its own
   controls.
7. Leave every entry unpromoted. Only `loki-continuous-improvement` may
   deduplicate, review and promote a candidate.

The only accepted workflow caller is `loki-implement-feature`.

Read [capture-contract.md](references/capture-contract.md) completely before
creating, reconciling or validating an entry.

## Outputs

- A unique immutable execution-knowledge entry when capture succeeds.
- A reconciled state: `captured`, `partial`, `failed`, `unsupported` or
  `skipped-nonmaterial`.
- Explicit reason and `minimum_next_path` for degraded states.

## Limits

- Do not use conversation memory as the required source.
- Do not store raw payload, transcript, secrets, personal data, hidden prompts
  or private/full chain-of-thought.
- Do not write a shared manifest, digest, backlog, plan, run state, runtime or
  normative package surface from the cataloger handoff.
- Permit only `target_entry` and the sibling `.<capture-id>.tmp`; validate the
  temporary with validator staged mode, publish it by atomic rename and remove
  it on failure.
- Do not block implementation completion on enrichment availability, latency,
  failure or validation.
- Do not promote or mark knowledge as applied.

## Validation

Run `python3 scripts/validate-execution-knowledge.py <entry-or-run-directory>`
when that validator is available in the active installation. An unsupported
validator is recorded as a capability gap, never fabricated as pass.
