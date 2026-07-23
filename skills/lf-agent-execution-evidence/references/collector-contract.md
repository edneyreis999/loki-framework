---
doc_id: "lf-agent-execution-evidence-collector-contract"
version: "2.0.0"
status: active
last_updated: "2026-07-23"
scope: "Deterministic collection, sanitization, publication, usage provenance, and liveness observation"
not_scope: "Domain writes, aggregate metrics ownership, private reasoning, or cost control"
authority: "skills/lf-agent-execution-evidence/SKILL.md and this current contract"
canonical_source: "skills/lf-agent-execution-evidence/references/collector-contract.md"
intended_llm_task: "validation"
source_priority: ["approved run envelope", "parent skill and evidence contract", "verified adapter input", "completion data"]
confidence: high
known_conflicts: []
replaced_by: null
---

# Execution evidence collector contract

## Responsibility boundary

The collector is a deterministic orchestrator component. At agent spawn it
correlates typed run, agent-run, handoff, parentage, agent, and runtime locator
facts. At terminal completion it combines those facts with the compact
completion record, adapter capability record, and optional sanitized snapshot.
The executing agent does not discover its own technical identifiers or claim
usage it cannot verify.

The collector may write only the exact evidence manifest and its exact optional
sanitized snapshot in the approved run-evidence destination. It may not write
domain artifacts, plans, agent contracts, learning-policy artifacts, raw
exports, or an arbitrary runtime directory. One serialized owner is responsible
for each `agent_run_id` evidence destination. Its closed `evidence_policy` is
positive: `evidence-first`, `preserve-gap`, `collector-only`, and
`explicit-only`. Consequently, a missing dimension remains explicit evidence
state, the collector is the only session-evidence writer, and a retrospective
can occur only through a separately authorized explicit dispatch.

## Lifecycle

1. Read the adapter capability record and initialize each dimension with an
   explicit state; unsupported capability starts `unsupported`, not `complete`.
2. Capture typed identity and runtime locator facts available at spawn. Preserve
   unknown or inaccessible facts as explicit dimension gaps.
3. On terminal completion, validate completion-record identity correlation and
   terminal status before collecting optional runtime evidence.
4. Sanitize the candidate payload structurally before it is eligible for
   storage. Reject raw/unredacted payloads rather than downgrading their label.
5. Derive per-dimension completeness, reasons, usage provenance, and the
   overall evidence state without silently promoting degraded data.
6. Write snapshot and manifest atomically, verify checksums after publication,
   and report a closed failure state if any operation fails.

The collector rejects input, manifest children, and attributes outside the
closed evidence shape. It also rejects historical policy shapes rather than
silently translating them.

## Sanitized snapshot rules

The stored snapshot is sanitized by default. Its normalization must remove or
replace raw prompt/content fields, credentials and authorization material,
environment values, connector payloads, and any field designated sensitive by
the adapter policy. Preserve only the minimum structured operational fields
needed for the declared dimensions. Mark the sanitization transform and result
in the manifest. Do not persist a raw sidecar, backup, or fallback payload.

Full/private chain-of-thought is neither a collection target nor an allowed
payload field. If a runtime exposes a declared summary, preserve it only under
the `reasoning_summary` dimension as partial evidence, subject to
sanitization.

## Atomic write and checksum protocol

For each file that is written, serialize deterministic content to a temporary
file in the target directory, flush and fsync it, calculate SHA-256 over the
exact finalized bytes, atomically replace the destination, then fsync the
directory where supported. Never write in place or publish a manifest before
the referenced snapshot is published.

When a snapshot exists, the manifest contains its path and SHA-256. The
manifest also contains a canonical-content SHA-256 calculated with the
manifest-checksum field omitted, avoiding a self-reference. Re-read published
files and verify both hashes. A failure before publication leaves no final
artifact; a failure after publication is reported as integrity `mismatch` or
`unverified` and cannot be `complete`.

## Degradation and failure handling

The collector records `partial`, `pointer-only`, `unavailable`, or
`unsupported` according to the evidence contract. `unavailable` means a
declared/expected capability could not be accessed in this execution;
`unsupported` means no implementation or evidenced capability exists. It never
fabricates a locator, snapshot, token count, or identifier to avoid either
state.

Complete usage collection accepts only explicit counters from a verified
run-scoped adapter source. It retains `metric_kind: per-turn-delta`, `source`,
`source_scope: verified-agent-run`, `measured_at`, and every separate counter;
it has no silent-zero default. Missing counters degrade usage and state why.
Cumulative and account-window metrics remain non-per-agent facts and must not
be apportioned by the collector. Estimates are emitted only into the separate
orchestrator-owned execution-metrics artifact with `utf8-byte-estimate-v1`; the
collector does not enlarge the fixed session-evidence XML shape.

The collector or adapter also exposes a read-only liveness probe. It records
only observed outcomes and never fabricates a heartbeat. A probe is mandatory
immediately before a silence-based abort/interrupt/cancel, but it is not a
budget, a background monitor, or authority to override explicit user
cancellation.
