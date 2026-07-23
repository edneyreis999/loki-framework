---
doc_id: "lf-agent-execution-evidence-adapter-capability-matrix"
version: "2.0.0"
status: active
last_updated: "2026-07-23"
scope: "Minimum evidenced adapter claims for evidence, token usage, and liveness"
not_scope: "Provider promises, untested integrations, or fabricated fallback capability"
authority: "skills/lf-agent-execution-evidence/SKILL.md and current adapter records"
canonical_source: "skills/lf-agent-execution-evidence/references/adapter-capability-matrix.md"
intended_llm_task: "routing"
source_priority: ["approved run envelope", "parent skill and evidence contract", "validated adapter record", "provider proposal"]
confidence: high
known_conflicts: []
replaced_by: null
---

# Adapter capability matrix and degradation

## How to use this matrix

This matrix fixes the minimum claim allowed before adapter-specific forward
validation. A provider integration must record adapter name, version when
known, capability source, validation date, and maturity before it can improve a
state. Absence of a record is not support.

| Adapter | Baseline maturity | Capability claim allowed now | Required degradation |
| --- | --- | --- | --- |
| Codex | `experimental` | Structured input through the provider-neutral collector; App Server remains opt-in and closed by default. | Use `partial`, `pointer-only`, `unavailable`, or `unsupported` per dimension unless a run-scoped forward export supports more. |
| Claude Code | `unvalidated` | Agent source/projection surfaces exist; hooks or transcripts are only candidates, not validated evidence sources. | Use `partial`, `unavailable`, or `unsupported` with missing reasons. Do not claim parity with Codex. |
| Other/generic | `unsupported` | No concrete adapter capability is inventory-backed. | Default every unimplemented dimension to `unsupported`; use `unavailable` only for an otherwise declared capability that was inaccessible in the run. |

## Capability record

An adapter-specific record must state, per dimension, the supported evidence
state, locator kind, snapshot transform, usage metric kinds/source scope,
runtime version, maturity (`unvalidated`, `experimental`, or `validated`), and
the validation evidence. It must distinguish observed behavior from proposal.
Experimental APIs require opt-in, tested version, and a closed fallback before
they are used as a dependency for `complete`.

## Dimension rules

| Dimension | `complete` requires | Closed degradation |
| --- | --- | --- |
| transcript | Sanitized, integrity-verified coverage sufficient for the declared execution. | Pointer with no audit snapshot is `pointer-only`; inaccessible declared capture is `unavailable`; absent capability is `unsupported`. |
| tool I/O | Sanitized, correlated tool inputs/outputs and terminal failures for the declared coverage. | Missing or truncated material is `partial`; do not infer tool I/O from a completion summary. |
| errors | Correlated terminal and material runtime errors, including non-success status when present. | Unknown/inaccessible errors are `partial` or `unavailable`, never silently empty. |
| reasoning summary | A declared, sanitized runtime summary with provenance; never hidden reasoning. | It is normally `partial`; hidden/private reasoning is always `unavailable`. |
| token usage | Exact requires a run-scoped, sourced, timed adapter counter with verified semantics. | A sanitized observable-byte estimate is separate `partial` execution metrics; cumulative/account-window remains non-agent; unavailable carries a reason and is never zero. |
| liveness probe | An adapter-observed, timestamped `running`, `progress`, or `terminal` outcome with source. | `unsupported` or `unavailable` with reason; never invent a heartbeat. |

An adapter cannot make the overall manifest `complete` unless each required
dimension meets its own `complete` condition, identity correlation is valid,
and manifest/snapshot integrity is verified. Provider-specific details belong
in later adapter records, not in this neutral contract.

Every adapter record must state whether a synchronous liveness probe is
supported. The orchestrator invokes it immediately before any silence-based
abort, interrupt, or cancel. An observed `running` or `progress` result forbids
that stop. This rule does not apply to an independently authorized explicit
user cancellation.
