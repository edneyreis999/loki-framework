# Agent execution evidence contract

## Scope

This is a provider-neutral contract for a terminal agent execution. It records
observable operational evidence; it is not a transcript-export contract and is
not an account of hidden model reasoning.

## Typed identity and lineage

Every manifest has an `identity` object with opaque, non-empty values for
`run_id`, `agent_run_id`, `handoff_id`, and `agent_name`. These are four
different types. Equality of their string values does not make them
interchangeable, and a validator must reject use of one field in another
field's role.

`runtime` is separate from `identity` and contains `adapter`, optional
`adapter_version`, `root_session_id`, `parent_thread_id`, `thread_id`,
`runtime_agent_id`, and terminal status. Each runtime field is a typed locator
for that runtime namespace, never a substitute for a Loki run, agent-run, or
handoff ID. A parent reference must name its type and must not introduce a
lineage cycle.

The executing agent supplies a compact `completion_record` with its
`agent_run_id`, `handoff_id`, terminal status, summary, changed/read files,
validations, material attempts, known errors, decisions, residual risks, and
next destination. It does not author runtime identity, token usage, or private
reasoning claims; the collector correlates those facts.

## Evidence state and completeness

`evidence_status` is exactly one of:

| State | Meaning |
| --- | --- |
| `complete` | Required dimensions are complete, identities correlate, and integrity is verified. Never use as a default. |
| `partial` | Some evidence is available; every degraded dimension has a reason. |
| `pointer-only` | A typed, usable locator exists but no auditably sufficient snapshot exists. |
| `unavailable` | The adapter declares or is expected to have the capability, but it was inaccessible in this execution. |
| `unsupported` | The adapter or dimension has no implemented and evidenced capability. |

The manifest reports these same states independently for `transcript`,
`tool_io`, `errors`, `reasoning_summary`, and `token_usage`. It also includes a
`missing_reasons` entry for every dimension not `complete`; each entry names the
dimension, state, and a non-empty reason. An overall `complete` is valid only
when all required dimensions are `complete`, required lineage is correlated,
and required integrity checks pass. A pointer-only dimension cannot be used to
make the overall manifest complete.

## Locator and snapshot

`locator` contains a typed `kind` (`runtime-pointer`, `local-file`, `export`,
or `unavailable`), `value`, and portability (`same-profile`, `same-machine`,
`portable`, or `none`). A non-`unavailable` status needs a compatible locator;
an unavailable locator has no usable value and a reason.

`snapshot` has `storage_mode` (`pointer-only`,
`pointer-plus-sanitized-snapshot`, `sanitized-snapshot-only`, or `unavailable`),
`payload_path`, `captured_at`, and checksum metadata. The default, when a
payload can be captured, is a sanitized snapshot. Raw, unredacted, or
full-payload storage is forbidden. A snapshot is not evidence of complete
transcript or tool I/O unless its dimension states say so.

## Usage

When usage is available, `usage` must include `metric_kind`, `source`, and
`measured_at`, plus separately nullable `input_tokens`, `cached_input_tokens`,
`output_tokens`, `reasoning_output_tokens`, and `total_tokens`. Valid
`metric_kind` values are `per-turn-delta`, `cumulative`, `account-window`,
`estimated`, and `unknown`.

Only a source whose scope is a verified agent run may be presented as per-agent
consumption. `cumulative` and `account-window` values may be preserved with
their source scope but must never be labelled, allocated, or summed as
per-agent usage. Unavailable usage remains unavailable with a reason; it is
never encoded as zero.

## Reasoning and security

Full/private chain-of-thought is `unavailable` and must not be requested,
stored, or named as an available source. A runtime-provided declared reasoning
summary is `partial`; an auditor's inference from action sequence is also
`partial`, explicitly labelled as inference, and does not prove intent.

The `security` section records the snapshot's classification, structural
redaction result, and the applicable retention metadata. Structural
sanitization is required for a persisted snapshot. Secret/PII hardening,
retention duration, and purge policy may be recorded as deferred; that
deferral does not permit raw persistence.

## Integrity and evidence-first policy

For every persisted payload, record the SHA-256 of its exact sanitized bytes.
The manifest records its canonical-content SHA-256 (excluding its own checksum
field) and an integrity result of `verified`, `unverified`, or `mismatch`.
Checksum mismatch makes `complete` invalid. A pointer-only or unavailable
manifest records why no payload checksum exists.

## Evidence-first boundary

This manifest is observable evidence, not a learning summary. Its closed
`evidence_policy` records `mode` as `evidence-first`, `gap_handling` as
`preserve-gap`, `capture_owner` as `collector-only`, and
`retrospective_dispatch` as `explicit-only`. These positive rules make the
collector the sole session-evidence writer, preserve an evidence gap as a gap,
and require an explicit, separately authorized dispatch for any retrospective.

A later execution-knowledge entry may reference the sanitized path and lineage
but must not copy the snapshot or change evidence status. The orchestrator
persists this evidence first, then may dispatch a non-blocking cataloger.
Cataloger failure, timeout or validation never changes the evidence manifest
and never invalidates an implementation result established by separate
validators.
