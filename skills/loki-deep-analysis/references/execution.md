# Deep Analysis Execution Contract

## Purpose and boundaries

Transform validated deep-analysis input into one evidence-based, traceable
report that starts from selectively retrieved analytic inferences, expands with
contextual candidates, and selects only useful investigations. This command is
an opt-in superset workflow; it must never invoke `loki-tech-analysis` as a
nested command or copy that command's execution as a second hidden run.

Read [analytic-report-contract.md](analytic-report-contract.md) completely
before constructing report state. Read
[lf-analytic-inference-preparation](../../lf-analytic-inference-preparation/SKILL.md)
and its preparation contract completely before the one mandatory preparation
invocation. The preparation skill composes
[lf-analytic-inference](../../lf-analytic-inference/SKILL.md) for root,
catalog, XML, retrieval, and policy authority. Catalogued inferences are
heuristic starting points, not constraints on contextual reasoning.

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
    - lf-analytic-inference-preparation
    - lf-analytic-inference
    - lf-tech-analysis-authoring
    - lf-agentic-orchestration
    - lf-agent-execution-evidence
  required_commands: []
  validators:
    - "input, canonical-path, scope, approval and destination-collision validation"
    - "preparation schema v2, root provenance, policy, index/record parity, locator and exact-dedup validation"
    - "preparation identity, candidate provenance, command-specific matching, request-control and report-contract validation"
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
2. If caller-owned planning or resume state exists, verify that its identity,
   task/run lineage, gates and target set apply to this run. Treat missing state
   as `not-applicable` only when the command is not resuming a planned run.
3. Build the approved preparation envelope from normalized demand facts and
   digest, ordered permitted local-source locators, digests and facts, the
   optional approved policy, and one required `request_controls` mapping with
   exactly the sole preparation-contract key:

   ```yaml
   request_controls:
     discovery_limit: "<validated active_policy.values.catalog_limit>"
   ```

   Preserve the active-policy provenance, authorization, and canonical
   request-controls digest with the envelope. The invocation passes the exact
   one-key mapping as `request_controls`; it does not add a command-defined
   control, derive a second digest, or reinterpret a normalized control. The
   preparation skill alone validates and normalizes these controls against the
   active policy. They do not grant root, candidate, dispatch, or write
   authority to this command.
4. Freeze the execution write set. With `destination: null`, the normal write
   set is empty. Otherwise it contains only the approved report file under one
   serial owner. An interaction-gate target may be added only after a material
   decision is identified and the exact target is separately approved.

Do not begin investigation until this preflight is valid. Return `blocked` with
all missing inputs and `minimum_next_path` rather than inventing authority.

## 2. Mandatory preparation boundary

Build one approved preparation envelope from normalized demand facts and digest,
ordered permitted local-source locators, digests and facts, request controls,
and the optional approved policy. The envelope grants only its exact read scope;
it contains no caller-selected root, destination, run identity, agent, handoff,
writer, or dispatch admission.

Invoke `lf-analytic-inference-preparation` exactly once with that envelope.
Do not invoke `lf-analytic-inference` directly for a second root, catalog, XML,
retrieval, policy, candidate-generation, deduplication, classification,
selection, or disposition pass. The shared preparation owns the normative
discovery through candidate classification procedure.

Record the exact preparation object, its `preparation_id`, `input_fingerprint`,
`preparation_digest`, policy identity/digest, catalog observation, validators,
blockers, and `minimum_next_path` in the command report and resume state. A
`blocked` preparation result stops with its exact `minimum_next_path`; it is
never retried or repaired locally.

Accept only preparation schema v2. Reject a schema-v1 preparation before
candidate interpretation and require regeneration to a new separately approved
versioned artifact. Existing v1 artifacts remain immutable; do not rewrite,
migrate, convert, or use a fallback reader.

## 3. Core validation and local routing

For a `pre-investigation-complete` or usable `partial` result, validate the
exact output keys, reproduced identities/digest, `root.root_provenance:
canonical-pwd`, and the literal zero/false/empty execution boundary. Reuse the
returned root and derived state context verbatim; never recalculate,
reclassify, reidentify, or silently amend the core.

After that one root result is valid, satisfy the public destination precondition
by validating canonical containment, existing-parent safety, symlink
resistance, collision behavior, and the frozen report write set against
`root.consumer_root`. No second root resolution is permitted. This command
creates no state root or catalog component.

Preserve every schema-v2 preparation candidate, duplicate relation, disposition, and
observable reason in the report. Start capability matching only from the
validated `selected_for_investigation` list and corresponding immutable
preparation candidates. A selection is eligibility for command-specific
matching only: it is not dispatch admission, a handoff, an agent run, an
investigation, or catalog mutation.

Cost and impact are absent from the preparation candidate schema and never
change preparation disposition. For each selected candidate, decide whether
bounded local resolution is sufficient or construct an investigation unit for
Section 7. Local resolution is permitted only when it is trivial, bounded,
read-only, low-risk, and cheaper than a handoff; record its exception, accepted
risk, scope, validators, and validation owner. Agent matching, handoff identity,
budget admission, dispatch, liveness, evidence, events, consolidation, and
report materialization remain exclusively command responsibilities.

## 4. Command-specific replanning and degradation

Replan only command-owned post-preparation work when matching, local
resolution, cost, capability, evidence, a gate, or a report validator changes
what can continue. Record the original assumption, observable result, affected
candidate IDs, revised ordering or scope, validators, and new stop condition.
Do not modify the preparation core to make a later command decision fit.

- Use `partial` when a valid core exists but an optional capability, local
  resolution, source, observed cost, or later evidence is unavailable.
- Use `insufficient` when the valid core and later evidence support no adequate
  material finding.
- Use `blocked` for a preparation boundary failure, material conflict, missing
  authority/gate, forbidden write request, or required validator failure.
- Use `failed` only for a terminal command execution error without a valid
  result.

Unknown or unsupported command-stage cost is never zero. This rule begins only
after the immutable preparation boundary. Do not dispatch hidden
work against a fictitious budget. Preserve the valid preparation result and
completed command stages with the exact `minimum_next_path` so a retry
converges without repeating accepted work.

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
these values. The preparation `discovery_limit` never changes them.

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
