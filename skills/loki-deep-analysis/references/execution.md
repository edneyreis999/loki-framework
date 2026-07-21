# Deep Analysis Execution Contract

## Purpose and boundaries

Transform validated deep-analysis input into one evidence-based, traceable
report that starts from selectively retrieved analytic inferences, expands with
contextual candidates, and selects only useful investigations. This command is
an opt-in superset workflow; it must never invoke `loki-tech-analysis` as a
nested command or copy that command's execution as a second hidden run.

Read [analytic-report-contract.md](analytic-report-contract.md) completely
before constructing report state. Read
[lf-analytic-inference](../../lf-analytic-inference/SKILL.md) completely and
follow its conditional routing for retrieval, validation, inference records,
events, and policy. Catalogued inferences are heuristic starting points, not
constraints on contextual reasoning.

```yaml
command_contract:
  name: loki-deep-analysis
  purpose: "Produce one validated deep-analysis report with selective inference reuse, contextual expansion, observable selection and resumable evidence."
  start_condition: "SKILL.md Input is valid and normalized; sources, scope, policy, writes, collision behavior, validators and gates are known."
  completion_condition: "All selected work is terminal, the report contract and validators pass, required gates are resolved, and the report is returned or written exactly once to its approved destination."
  outputs:
    - "one immutable deep-analysis report, written to the approved destination or returned response-only"
    - "structured generated candidates and inference events embedded in that report"
    - "terminal handoff, validator, gate, risk, gap and resume records"
  allowed_writes:
    - "destination, only when it is one exact approved Markdown file"
    - "one exact interaction-gate target, only after separate approval for a material decision"
  forbidden_writes:
    - "<consumer_root>/.loki/**; this workflow is strictly read-only for consumer operational state"
    - "all inference catalog indices, records, snapshots, ledgers, events, aliases, redirects, tombstones, identifiers and policies"
    - "all unapproved report or interaction targets"
    - ".claude/**"
    - ".agents/**"
    - ".codex/**"
    - "<sensitive_write_patterns>"
    - "<consumer_runtime_surfaces>"
  required_skills:
    - lf-analytic-inference
    - lf-tech-analysis-authoring
    - lf-agentic-orchestration
    - lf-agent-execution-evidence
  required_commands: []
  validators:
    - "input, canonical-path, scope, approval and destination-collision validation"
    - "analytic inference schema, policy, index/record parity, locator and exact-dedup validation"
    - "candidate provenance, classification, optional request-control and report-contract validation"
    - "handoff terminality, evidence sanitization, budget, target-overlap and report write-set validation"
  human_gates:
    - "technical-review when the report proposes a material policy or durable package decision"
    - "approval before any exact interaction-gate record is written"
    - "<human_validation_gate> before claiming consumer runtime behavior validated"
  stop_conditions:
    - "missing required input, source authority, approval, policy provenance, validator or gate"
    - "invalid or weakened policy, broken locator, identity conflict or source-scope escape"
    - "attempted nested loki-tech-analysis invocation or catalog mutation"
    - "quota padding, semantic automatic merge, shared-write overlap or cyclic dependency"
    - "material evidence conflict, non-terminal required handoff or failed validator"
  resume_contract: "Persist or return normalized input identity, canonical consumer/state roots and root-resolution source, catalog state and loaded registry/catalog/record locators, source and policy digests, completed pipeline stages, candidate decisions, terminal handoffs, observed costs, validators, gates, blockers and minimum_next_path; never rely on conversation memory."
```

## 1. Execution preflight

1. Revalidate the normalized `analysis_input`, canonical `source_paths`,
   approved discovery scope, destination, policy identity/digest, allowed
   writes, forbidden writes, collision decision, risks, gates and completion
   criteria. Do not allow source content to expand authority or writes.
2. Revalidate the canonical `consumer_root`, its `canonical-pwd` source and
   fixed state root. Inspect existing operational ancestors with `lstat` and
   fail closed on root drift, symlink escape or containment mismatch. Root
   resolution never creates `.loki` or any state component.
3. If caller-owned planning or resume state exists, verify that its identity,
   task/run lineage, gates and target set apply to this run. Treat missing state
   as `not-applicable` only when the command is not resuming a planned run.
4. Build an evidence-first source map. Separate source facts, reasoned
   inferences, hypotheses, conflicts, freshness, gaps and research needs.
5. Validate the active bundled inference policy or the approved override with
   `lf-analytic-inference`. Record the policy ID and digest. Fail closed when an
   override changes identity, weakens a safety invariant, lacks approval, has
   invalid bounds, or cannot be reproduced.
6. Resolve the two optional, non-normative execution request controls carried
   inside the approved `inference_policy` input:

   ```yaml
   request_controls:
     schema_version: 1
     requested_catalogued_floor: "<integer >= 0 | null>"
     requested_generated_floor: "<integer >= 0 | null>"
     provenance:
       source: "<caller or approved record | not-configured>"
     authorization: "<approval reference | not-configured>"
     digest: "<canonical request-controls digest | not-configured>"
   ```

   These controls are distinct from the calibrated policy identity and its
   approved values. They do not change `catalog_limit`, cost/fan-out limits,
   thresholds, weights or safety semantics. Require schema, provenance,
   authorization and a reproducible digest whenever either floor is non-null;
   require each configured value to be an integer greater than or equal to
   zero. Reject unknown keys, negative or non-integer values, digest mismatch,
   missing authorization, or any request that purports to weaken a policy
   invariant. Missing controls normalize to `null` with source,
   authorization and digest recorded as `not-configured`; never invent a
   default. A requested floor remains subordinate to the approved cost,
   fan-out, relevance and utility limits and cannot compel budget overrun.
7. Freeze the execution write set. With `destination: null`, the normal write
   set is empty. Otherwise it contains only the approved report file under one
   serial owner. An interaction-gate target may be added only after a material
   decision is identified and the exact target is separately approved.

Do not begin investigation until this preflight is valid. Return `blocked` with
all missing inputs and `minimum_next_path` rather than inventing authority.

## 2. Technology and surface discovery

Derive technology/domain candidates only from observable local evidence such as
declared dependencies, configuration, file formats, imports, manifests,
project documentation, or caller-provided sources. For each candidate record:

- normalized technology/domain ID and observed aliases;
- affected versions, surfaces, objectives and signals;
- evidence references and source freshness;
- confidence `high`, `medium`, `low`, or `unknown`, with a short reason;
- contradictions, exclusions and discovery limitations.

Treat confidence as an evidence label, not numeric certainty. Do not silently
promote an uncertain technology to confirmed. A low-confidence candidate may
guide bounded source discovery, but catalog retrieval requires sufficient
technology evidence. If none exists, record `insufficient`; continue only with
contextual generation that remains verifiable and useful.

## 3. Index-first selective retrieval

Record root provenance before lookup. Derive the registry locator
`<state_root>/registry.xml`; never accept a caller-supplied catalog root. Report
catalog state exactly as `absent`, `empty`, `loaded`, or `blocked`. Missing
registry is `absent`; a valid registry with no entries is `empty`; either
returns `insufficient` for retrieval with `mutation_applied: false` and creates
nothing. For `loaded`, record the registry locator, each selected relative
`catalogs/<technology-id>/index.xml` locator, and every loaded `rev-N.xml`
record locator. Live events, when referenced as evidence, also use `.xml`.
No JSON tree is an active lookup fallback or a catalog source.
Invalid schema, absolute/escaping locator, identity/revision mismatch, missing
target, symlink escape or root mismatch yields `blocked`.

Invoke `lf-analytic-inference` with operation `retrieve` and the normalized
technology/query evidence.

1. Resolve only catalog indices whose technology ID or aliases match confirmed
   evidence. Record every index read. Do not enumerate or load all records.
2. Validate index schema, active limit, unique identity, ordering and safe
   relative locators before using an entry.
3. Before loading any record, filter and order entries using only fields that
   actually exist in the index: `inference_id`, `revision`, `status`, `summary`,
   `technologies`, `surfaces`, `objectives`, `signals`, and `locator`. Filter by
   allowed status and matches on confirmed technology, surface, objective and
   signal evidence. Order surviving summaries by exact technology, surface,
   objective and signal matches, then ascending `inference_id`; use revision,
   status, summary and locator only for validation or an explicitly declared
   deterministic tie-break, never as invented semantic evidence.
4. Load only surviving record locators. Validate containment and index/record
   identity, revision, status and locator parity. A broken, escaping or
   mismatched locator is `blocked`, not a silent skip.
5. Only after selective loading, validate and apply record-only constraints:
   compatible versions, explicit exclusions, evidence availability,
   freshness, demand relation, risk, investigation cost, stop condition and
   material-finding potential. Reject incompatible or insufficient records
   with typed reasons.
6. Semantically rerank only the validated loaded set by demand relation,
   evidence able to confirm or reject, affected surfaces, risk, cost and
   material-finding potential. Record a concise observable reason for every
   ordinal rank or semantic score.

When `requested_catalogued_floor` is configured, treat it only as a requested
minimum of relevant results and stop at policy budget even if it is unmet.
When it is `null`, stop by material coverage, utility and budget rather than a
quota. In both cases, stop selective loading when additional records cannot
improve material coverage within policy budget. Empty catalog, no matching
technology, no adequate inference, stale-only candidates, or fewer relevant
records than a configured floor are honest `insufficient` or `partial` results;
never pad with irrelevant entries. Record the requested value and source, or
`requested_catalogued_floor: not-configured`, in the report.

## 4. Contextual candidate generation

Generate analytic candidates beyond the catalog using the current demand,
source map, technology evidence, uncovered surfaces, contradictions and known
gaps. Preserve `origin: generated` and the run-scoped identity throughout.

Each candidate must satisfy the generated-candidate schema in the report
contract, including a testable statement/question, explicit demand relation,
applicability, source provenance, evidence capable of confirmation or
rejection, potential impact, ordinal or unknown cost, observable stop
condition, suggested capabilities, and distinction from existing candidates.

When `requested_generated_floor` is configured, generate toward that requested
minimum only while useful, verifiable candidates remain and policy budget is
available. The request is not a quality substitute, a ceiling, or authority to
exceed cost/fan-out limits. When it is `null`, terminate generation by material
coverage, downstream utility and budget rather than a quota. Stop early and
report why when additional candidates would be irrelevant, non-verifiable,
duplicative, outside scope, unable to produce downstream utility, or over
budget. Never fabricate a candidate solely to satisfy a count. Record the
requested value and source, or `requested_generated_floor: not-configured`, in
the report.

## 5. Unified deduplication and classification

Combine catalogued and generated candidates into one working set while
retaining origin, identity, revision, locator and provenance.

1. Canonicalize only fields authorized by the inference contract. Detect exact
   duplicates deterministically and keep a traceable winner/rejection record;
   do not discard provenance.
2. Report potential near-duplicates with compared IDs, similarity rationale,
   material differences and a proposed review disposition. Semantic similarity
   never executes a merge, rewrite, redirect, deduplication, reorganization or
   removal.
3. Classify each non-duplicate candidate by relevance, evidence availability,
   risk, investigation cost, independence/dependencies, surface coverage,
   expected material-finding potential and stop-condition quality.
4. Reject candidates that are irrelevant, untestable, redundant, unsafe,
   outside scope, unsupported by available evidence, or useful only to pad a
   quota. Record typed reasons.
5. Select only candidates that are useful and verifiable within policy limits.
   Resolve simple candidates locally when evidence and validators are
   sufficient; group dependent investigations and keep shared writes serial.

Score and thresholds may be reported only as eligibility. They do not approve
selection, promotion, merge, reorganization, purge, or any catalog change.
Catalog retrieval, validation and reporting perform strictly zero writes to
registry, indices, records, events, snapshots, aliases, redirects, tombstones,
identifiers, policy or any other catalog-owned state.

## 6. Replanning and degradation

Replan explicitly whenever discovery, lookup, generation, deduplication,
classification, cost or evidence invalidates a later step. Record the original
assumption, observable result, affected candidates, revised ordering/scope,
validators and new stop condition.

- Use `partial` when valid useful analysis remains but an optional capability,
  source, candidate floor, freshness signal or observed cost is unavailable.
- Use `insufficient` when evidence cannot support any adequate inference or
  material finding.
- Use `blocked` for invalid policy/schema, broken locator, material conflict,
  missing authority/gate, forbidden write request, or required validator
  failure.
- Use `failed` only for a terminal execution error without a valid result.

Unknown or unsupported cost is never zero. Do not select hidden work against a
fictitious budget. Preserve completed valid stages and the exact
`minimum_next_path` so a retry converges without repeating accepted work.

## 7. Investigation fan-out and terminal evidence

Apply the agent selection, liveness and completion rules from
[lf-agentic-orchestration](../../lf-agentic-orchestration/SKILL.md), and the
typed collection and degradation rules from
[lf-agent-execution-evidence](../../lf-agent-execution-evidence/SKILL.md).
The orchestrator owns dispatch, identity correlation, liveness checkpoints,
evidence collection and serial consolidation.

### Capability-first selection

For every selected inference, create one investigation unit with an objective,
selection reason, evidence question, bounded sources and scope, dependencies,
expected output, validators and observable stop condition.

1. Inspect only the active agent catalog and active adapter capability record.
   Match observed capability tags, phase role, agentic mode, write class, risk,
   parallel safety and technology routes. Never infer capability from an agent
   name or invent an agent ID.
2. Prefer the smallest suitable persistent specialist and record its exact
   `selection_reason`, matched capability evidence, limitations and rejected
   alternatives when material.
3. If no persistent specialist matches, record the capability gap. Use a
   temporary agent only when the adapter record explicitly demonstrates
   temporary-agent support for this run. Its mode is strictly `read-only` or
   `proposal-only`; it receives no durable or shared write target.
4. If temporary-agent capability is absent, inaccessible or unsupported,
   return the investigation as `partial`, `unavailable` or `unsupported` with
   a reason and `minimum_next_path`. Do not fabricate a specialist or silently
   treat selection as investigation.

Keep work local only when it is trivial, bounded, read-only, low-risk and
cheaper than a handoff. Record the exception, accepted risk, scope, validators
and validation owner.

### Typed identity and handoff envelope

The orchestrator/collector allocates opaque, non-empty and globally unique
`agent_run_id`, `handoff_id` and `evidence_id` values. They are different types
and cannot substitute for each other, the Loki `run_id`, the agent name, or a
runtime locator. Validate uniqueness before dispatch. Model dependencies only
with `depends_on_handoff_id`; reject self-dependency, missing parents and any
cycle in the handoff DAG.

Every dispatch receives this self-contained envelope:

```yaml
investigation_handoff:
  run_id: "<Loki run identity>"
  agent_run_id: "<unique agent-run identity>"
  handoff_id: "<unique handoff identity>"
  evidence_id: "<unique evidence identity>"
  depends_on_handoff_id: []
  inference_id: "<catalogued or generated identity>"
  inference_revision: 1
  owner: "<selected persistent or temporary agent>"
  agentic_mode: "read-only | proposal-only"
  selection_reason: "<observable capability match>"
  capability_evidence: []
  facts: []
  approved_decisions:
    - decision: "<decision that constrains this handoff>"
      status: "approved | rejected | deferred | not-applicable"
      source: "<observable decision reference>"
  objective: "<bounded investigation question>"
  sources: []
  scope:
    included: []
    excluded: []
  allowed_writes: []
  forbidden_writes:
    - "all catalog-owned surfaces"
    - "shared report and interaction targets"
    - ".claude/**"
    - ".agents/**"
    - ".codex/**"
  expected_output: "<observable proposal or finding>"
  output_format: "<typed schema or concise structured format>"
  validators: []
  gates: []
  stop_condition: "<observable terminal condition>"
  success_destination: "loki-deep-analysis orchestrator"
  failure_destination: "loki-deep-analysis orchestrator"
```

The handoff returns a compact completion record with the same typed IDs;
correlated parentage and dependencies through `depends_on_handoff_id`; honest
terminal status; summary; files read/changed; validator outcomes;
`gate_outcomes` and `approval_outcomes`, each with status and observable source
reference; material attempts; known errors; decisions; blockers; residual
risks; and next destination. Use `pending`, `unavailable`, `unsupported`,
`failed` or another contract-valid degraded status instead of inventing a
satisfied gate, approval or parent correlation. The executing agent supplies
no runtime identity or usage claim.

### DAG, fan-out and budget admission

The active v1 policy fixes `fan_out_limit: 2`, `cost_budget: 6` and
`handoff_timeout_ticks: 3`. Validate the active policy digest before using
these values. Optional request floors never change them.

- Dispatch at most two handoffs concurrently.
- Parallel handoffs must be independent in the DAG and have read-only targets
  or provably disjoint exact targets. Any shared target, report write,
  interaction write or consolidation is serialized under one owner.
- Do not place a handoff in a parallel group with its ancestor, descendant,
  cyclic dependency, shared mutable state or unresolved material gate.
- Admit work only while the cumulative observed/authorized cost plus the next
  bounded cost remains at or below 6. Defer the next investigation before an
  overrun; never execute first and explain the excess later.
- `unknown` or `unsupported` cost is never zero. Without a safe authorized
  upper bound proving admission within the remaining budget, do not dispatch;
  degrade to `partial`, `unavailable` or `unsupported`, record the candidate
  and the minimum next evidence needed.
- Quotas and request floors cannot compel fan-out, irrelevant work or a budget
  overrun. Prefer fewer useful independent investigations.

Record the candidate order, admitted/deferred/rejected sets, per-handoff cost
state, cumulative cost, remaining budget and the observable admission reason.

### Liveness and terminal tracking

Treat one tick as an orchestrator checkpoint, not elapsed-time fabrication. At
each checkpoint record status, available output/evidence, blockers and next
action. At `handoff_timeout_ticks: 3`, inspect liveness:

- do not mark failure automatically when a current status or usable partial
  output exists; reconcile it, continue with a bounded next checkpoint, or
  terminate honestly as `partial`;
- when neither status nor output is available, stop waiting and record the
  handoff/evidence as `unavailable` with a reason and `minimum_next_path`;
- use `unsupported` when the adapter never implemented the needed capability;
- use `failed` or `blocked` only when the completion record, ownership breach,
  gate or validator provides observable grounds.

Track every dispatched handoff to one terminal completion state before the
overall report can be `completed`. A useful partial result may support an
overall `partial` report, but it cannot be silently upgraded. Never abandon a
running handoff, infer success from file existence, or treat a timeout alone as
failure.

### Evidence collection and degradation

After terminal completion, the orchestrator-owned evidence collector—not the
executing agent—correlates typed identities and the active adapter capability
record. This command embeds the sanitized evidence result or typed gap in its
approved report; it grants no additional evidence-file write. When an invoking
parent workflow already owns a separately approved exact evidence destination,
that parent persists evidence before any optional execution-knowledge capture,
outside this command's write set. Report overall evidence and each required
dimension (`transcript`, `tool_io`, `errors`, `reasoning_summary`,
`token_usage`) using exactly one of:

- `complete`;
- `partial`;
- `pointer-only`;
- `unavailable`;
- `unsupported`.

Every dimension not `complete` needs a non-empty reason. Overall `complete`
requires complete required dimensions, correlated identity and verified
integrity; it is never the default. A pointer is not a snapshot. Never invent
a locator, snapshot, agent-scoped token count, runtime ID or usage value.
Cumulative/account-window usage remains non-agent evidence; unavailable usage
is not encoded as zero.

Persist only structurally sanitized evidence. Do not request or store raw
prompts, raw tool payloads, full transcripts, secrets, personal data, hidden
prompts, or private/full chain-of-thought. A runtime-declared sanitized
reasoning summary remains `partial`. There is no automatic retrospective,
dual-capture or legacy retrospective fallback for an evidence gap.

Evidence collection failure does not invent completion evidence: preserve the
validated handoff result separately and report evidence as `partial`,
`pointer-only`, `unavailable` or `unsupported` as applicable.

### Inference events

Emit a stable, schema-valid event only for the stage actually observed. Keep
`selected`, `investigated`, `validated`, `rejected`, `material-finding`,
`task-helped`, `false-positive`, `repeated-evidence` and `stale` independent:
one stage never implies another. Replaying identical `event_id` and payload is
a no-op; a divergent payload under the same ID blocks consolidation. Preserve
the observed agent capability and context/tool cost, or the explicit
`unavailable`, `unknown` or `unsupported` state.

### Human-validation boundary

Record human validation provider-neutrally:

```yaml
human_validation:
  gate: "<human_validation_gate>"
  required: "<true | false>"
  state: "<deferred | passed | failed | not-applicable>"
  source: "<observable gate source | unavailable>"
  evidence_refs: []
  reason: "<non-empty state reason>"
  minimum_next_path: "<exact next evidence/action | none>"
```

Use `deferred` when required evidence is not yet available, `passed` or
`failed` only with applicable observable evidence, and `not-applicable` only
when the gate is not required and the reason is explicit. Do not claim runtime,
integration, persisted consumer state or perceptible behavior as validated
without `state: passed`. The overall report may be `completed` only when a
required `<human_validation_gate>` is resolved as `passed`; an unresolved
required gate must degrade or block honestly.

## 8. Consolidation, validation and write

Consolidate exactly one report according to
[analytic-report-contract.md](analytic-report-contract.md). Keep reused,
generated, rejected, selected, investigated and validated inferences distinct;
include negative results and conflicts. Embed candidates and events in the
report only; never persist them to catalog-owned files.

Run all applicable validators before writing or declaring `completed`. A
failed or inconclusive material validator blocks completion. If a destination
is approved, hand the exact report target to one scoped writer, serialize the
write, verify the resulting file and confirm that no catalog or unapproved
interaction target changed. If destination is null, return the report through
the response contract without writing.

Never invoke `loki-tech-analysis`; never write, promote, merge, reorganize or
purge the inference catalog; never automatically merge a near-duplicate, fill
a quota with irrelevant work, or infer missing evidence.
