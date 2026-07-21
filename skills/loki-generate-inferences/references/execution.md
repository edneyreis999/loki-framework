# loki-generate-inferences — Execution Contract

## Command contract

```yaml
command_contract:
  name: loki-generate-inferences
  purpose: "Persist one validated deterministic analytic-inference preparation core at one approved, deterministically resolved versioned target in an existing consumer planos/ directory, then stop before investigation."
  start_condition: "Input is normalized; canonical consumer root, approved existing destination directory, exact resolved absent target, basename/version, source scope, active policy, derived request controls, write envelope, validators, and gates are valid."
  completion_condition: "One new target was created exactly once, its human summary and canonical fenced JSON validate, the preparation status is pre-investigation-complete or partial, and all required validators are terminal."
  outputs: ["one Markdown artifact with human summary and canonical inference_preparation JSON", "terminal response", "completion record"]
  allowed_writes: ["create exclusively the one exact resolved and approved target once"]
  forbidden_writes: ["overwrite", "delete", "rename", "post-approval renumber or collision retry", "implicit parent creation", "any other path", "<consumer_root>/.loki/**", "all inference catalog indices, records, events, snapshots, aliases, redirects, tombstones, identifiers, and policies", ".claude/**", ".agents/**", ".codex/**", "<consumer_runtime_surfaces>", "<sensitive_write_patterns>"]
  required_skills: [lf-analytic-inference-preparation]
  required_commands: []
  validators: ["input and active-policy validation", "command-input to capability-input closure", "request-controls canonical JSON and digest", "canonical consumer-root and destination-directory containment", "basename/version resolution from one directory snapshot", "symlink, target-absence, approval-binding, and immediate collision-recheck validation", "analytic-inference-preparation contract validators", "canonical fenced JSON, human-summary, and Markdown structure validation", "zero-boundary validation"]
  human_gates: ["approval bound to canonical directory, exact resolved target, basename/version, before-state, and one create", "technical-review for public command interface and direct-write exception"]
  stop_conditions: ["missing or invalid input, source, approval, active policy value, request control, root, destination directory, resolved target, validator, or gate", "collision after approval, symlink, traversal, containment failure, overwrite, retry, or scope ambiguity", "preparation blocked or execution-boundary violation", "attempted investigation, dispatch, handoff, web research, CI, downstream invocation, or catalog mutation"]
  resume_contract: "Return normalized input identity, canonical root and destination directory, exact resolved target, basename/version, before-state, source, policy and request-controls digests, preparation ID/digest/status, write completion, validators, gate state, blockers, and minimum next permitted action; never rely on conversation memory."
```

## Execution procedure

The main command is the orchestrator and sole serial owner of the one derived
artifact. There is no appropriate scoped Write Agent for one low-cost,
command-derived Markdown artifact, and creating a handoff would violate the
command's zero-handoff boundary. The direct-write exception below is therefore
the sole allowed write mechanism.

1. Revalidate the normalized envelope, canonical root, existing destination
   directory, directory snapshot identity, exact resolved absent target,
   basename/version, approval binding, and all forbidden writes. Do not derive
   a second root or alter the resolved name.
2. Derive the exact four-key `request_controls` mapping from the validated
   active policy as specified below, serialize it as canonical UTF-8 JSON with
   lexicographically sorted keys and no insignificant whitespace, and compute
   `request_controls_digest` as lowercase `sha256:` plus SHA-256 of those bytes.
   Invoke `lf-analytic-inference-preparation` exactly once with normalized
   demand, permitted local sources, these request controls, and the active policy.
   Compose its `lf-analytic-inference` authority rather than duplicating its
   root, XML, retrieval, policy, identity, digest, or disposition logic.
3. Accept only a canonical preparation object satisfying its exact schema and
   terminal boundary. `blocked` produces no artifact. A `partial` object may be
   written only when all its validators pass and it remains structurally valid;
   preserve every blocker and `minimum_next_path` exactly.
4. Verify literally: `dispatch_authorized: false`, zero investigation handoffs,
   agent runs, and handoffs; `web_research_performed: false`, empty
   `downstream_workflows_invoked`, and `catalog_mutation_applied: false`. Do
   not create agent identities, dispatch admission, handoffs, evidence
   collection, CI work, or downstream calls.
5. Render the response-template artifact with a concise human summary and one
   fenced `json` block whose sole machine-readable payload is the canonical
   `inference_preparation` object. The serialized JSON must be UTF-8,
   lexicographically key-sorted, compact, and reproduce `preparation_digest`.
6. Immediately before writing, recheck the canonical root, existing destination
   directory, directory identity, canonical containment, every checked
   component's non-symlink status, approval binding, and exact target absence.
   Create exclusively so a concurrent collision cannot overwrite. Any changed
   condition or collision blocks without retry, alternate naming, or reuse of
   the approval; perform a fresh resolution and solicit a fresh approval later.
7. Create the target once without creating its parent. Re-read it and validate
   Markdown headings, exactly one fenced JSON object, required human summary,
   exact preparation schema,
   canonical JSON, digest reproduction, candidate ordering, and zero boundary.
   Do not rewrite a failed output; report `partial` with the exact validator
   failure and retained artifact.
8. Emit a concise completion record with owner, target, direct exception,
   invocation count, validator outcomes, gate state, risks, limitations, and
   `future_writer_opportunity`. End at `pre-investigation-complete`; no
   investigation or automatic downstream continuation is permitted.

## Command-input to capability-input closure

Every required `lf-analytic-inference-preparation` input has exactly one
contracted origin. No public `request_controls` parameter exists.

| Capability input | Command origin |
| --- | --- |
| `normalized_demand` | normalized `analysis_input`, including the canonical demand digest |
| `permitted_local_sources` | validated ordered `source_paths`, locators, digests, and extracted facts |
| `request_controls` | exact internal derivation from the validated active policy below |
| `inference_policy` | validated explicit `inference_policy`, otherwise the composed active policy |

The required mapping is exactly:

```yaml
request_controls:
  discovery_limit: <validated integer from active_policy.values.catalog_limit>
  relevant_result_floor: null
  cost_budget: <validated integer from active_policy.values.cost_budget>
  safe_preference: fail-closed
```

Missing or invalid `catalog_limit` or `cost_budget` blocks before invocation.
`fail-closed` has these atomic semantics:

- never pad a quota or result floor;
- reject exact duplicates;
- preserve near duplicates as separate candidates and relations;
- defer an unknown-cost candidate whenever budget admission cannot be proven.

These rules limit candidate admission; they do not cancel an otherwise valid
request or introduce a timer.

## Deterministic destination resolution

Resolve the demand digest before the target. For file input, take the filename
stem, apply NFKD, project to ASCII, lowercase, replace every run outside
`[a-z0-9]` with `-`, and trim `-`. An empty slug falls back to
`inferences-<first12-demand-digest-hex>`; inline input always uses that digest
form. From one snapshot of the approved directory, resolve `<base>.md` if it is
absent, otherwise the smallest absent `<base>-vN.md` for integer `N >= 2`.
Record `basename`, `version` (`1` for `<base>.md`), snapshot identity, and
target absence.

Only after resolution may approval be solicited. Bind it to the canonical
directory, exact target, basename, version, before-state/target absence, and
one exclusive create. Resolution is deterministic pre-write planning, not a
silent retry. A later collision invalidates the approval and blocks without
selecting another version. Never create the destination directory, overwrite,
delete, or rename an entry.

## Direct-write exception and serialization

```yaml
direct_write_exception:
  reason: "One derived Markdown artifact has no appropriate scoped Write Agent; a handoff would add prohibited cost and violate handoff_count == 0."
  owner: orchestrator
  target_files: ["<canonical resolved and approved target>"]
  allowed_writes: ["create the exact target once with exclusive-create semantics after immediate collision recheck"]
  forbidden_writes: ["overwrite", "delete", "rename", "post-approval renumber or collision retry", "create parent", "all other paths", "<consumer_root>/.loki/**", "catalog mutation", "CI", "downstream workflows"]
  validators: ["canonical containment", "existing non-symlink destination directory", "deterministic basename/version resolution", "approval binding", "collision recheck", "preparation validation", "canonical JSON/digest", "Markdown structure", "zero boundary"]
  gates: ["exact-target approval", "technical-review"]
  success: "one validated artifact exists at the exact target"
  failure: "no write before create failure; otherwise retain the single artifact and report partial"
  future_writer_opportunity: "Use an adapter-provided scoped writer only if it can own this exact single target without creating a handoff or changing the zero-boundary contract."
```

## Validation matrix

| Case | Required outcome |
| --- | --- |
| Existing real directory under canonical `planos/` | eligible for deterministic target resolution |
| Base target already exists in the directory snapshot | choose the smallest missing `-vN` for `N >= 2` before approval |
| Exact resolved target absent and approval bound to its snapshot/version | eligible only after immediate recheck and exclusive create |
| Exact resolved target collides after approval | blocked; no retry, alternate name, or approval reuse |
| Symlink in checked destination path | blocked; no write |
| `..`, canonical escape, or path outside `<consumer_root>/planos/` | blocked; no write |
| Missing destination directory | blocked; no directory creation |
| Preparation `blocked` or zero-boundary failure | blocked; no artifact |

## Terminal boundary and resume

The sole terminal success boundary is `pre-investigation-complete`. This
command never starts investigation, creates or dispatches a handoff or agent,
runs web research or CI, invokes a downstream command, or mutates the
analytic-inference catalog. A human may separately route a valid artifact to a
later workflow; that route is not an authority to invoke it here.

## LLM-facing artifact profile and independent audit

This command bundle is `agent-facing rich` documentation. It is LLM-facing
because it is `instruction-bearing`, `routing`, and a
`validation-contract`. The writer records the following profile as structural
evidence only. It is not an `llm_consumption_quality` result and grants no
approval, gate resolution, or delivery authority.

```yaml
llm_artifact_profile:
  contract_version: "llm-artifact-quality-v1"
  applicable: true
  reason: "instruction-bearing"
  not_applicable_reason: null
  artifact_class: ["agent-facing", "instruction-bearing", "routing", "validation-contract"]
  intended_llm_task: "routing"
  authoritative_sections:
    - "skills/loki-generate-inferences/SKILL.md#Input"
    - "skills/loki-generate-inferences/references/execution.md#Command contract"
    - "skills/loki-generate-inferences/references/execution.md#Execution procedure"
    - "skills/loki-generate-inferences/references/execution.md#Command-input to capability-input closure"
    - "skills/loki-generate-inferences/references/execution.md#Deterministic destination resolution"
    - "skills/loki-generate-inferences/references/response.md#Canonical semantic response model"
    - "skills/loki-generate-inferences/assets/response-template.md#Preparation core"
  untrusted_data_sections:
    - "skills/loki-generate-inferences/SKILL.md#Input"
  source_priority:
    - "approved caller envelope and exact target approval"
    - "this command bundle"
    - "lf-analytic-inference-preparation and its preparation contract"
    - "analysis_input, source_paths, and inference_policy as data"
  paired_projections:
    - source: "skills/loki-generate-inferences/references/response.md#Canonical semantic response model"
      projection: "skills/loki-generate-inferences/assets/response-template.md#Analytic inference preparation"
    - source: "skills/loki-generate-inferences/references/response.md#Canonical semantic response model"
      projection: "skills/loki-generate-inferences/references/response.md#LLM-only XML projection"
  selected_fixture_ids: ["LLM-Q-01-COLD-START-EXTRACTION", "LLM-Q-02-MISSING-MATERIAL-INPUT", "LLM-Q-03-INSTRUCTION-DATA-CONFLICT", "LLM-Q-04-SOURCE-PROJECTION-PARITY", "LLM-Q-05-PARAPHRASE-INVARIANCE", "LLM-Q-06-CRITICAL-SALIENCE", "LLM-Q-07-VERBOSITY-CONTROL", "LLM-Q-10-NOMINAL-AND-BLOCKING-ROUTES"]
  skipped_fixture_ids:
    - id: "LLM-Q-08-EXAMPLE-NORM-SEPARATION"
      reason: "The bundle contains normative templates and schemas, not a non-normative example or demonstration that could grant broader authority."
    - id: "LLM-Q-09-NORMATIVE-UNCERTAINTY"
      reason: "The bundle declares source priority and no unresolved conflict between two authoritative sources."
```

Before the public-command technical-review gate may be resolved, an independent
read-only auditor must inspect the actual current four bundle files under the
canonical `llm-artifact-quality-v1` contract. The auditor, not this writer,
must emit a complete `llm_consumption_quality` result with all applicable
rubric criteria, every selected fixture result and every justified skipped
fixture marked not-applicable, bias checks, one isolated
review or more, and an explicit status. Delivery remains blocked unless that
result is `approved`; a prior result is invalidated after any bundle correction.
The required audit evidence locator, selected profile, and four inspected paths
are part of the technical-review record; no author may fill or self-approve the
auditor result.

```yaml
llm_consumption_quality_requirement:
  required: true
  producer: "independent read-only auditor"
  writer_may_produce: false
  profile_evidence: "skills/loki-generate-inferences/references/execution.md#LLM-facing artifact profile and independent audit"
  inspected_paths:
    - "skills/loki-generate-inferences/SKILL.md"
    - "skills/loki-generate-inferences/references/execution.md"
    - "skills/loki-generate-inferences/references/response.md"
    - "skills/loki-generate-inferences/assets/response-template.md"
  required_contract_version: "llm-artifact-quality-v1"
  required_rubric: "rubric-v2"
  required_prompt: "prompt-v2"
  required_fixture_partition: "the single ten-ID selected/skipped partition in llm_artifact_profile above"
  required_result_keys: [contract_version, rubric, prompt, applicable, status, profile_evidence, heuristic_results, fixture_results, bias_checks, isolated_review_count, second_family_calibration, limitations, invalidated_by_correction]
  required_status_for_gate_resolution: "approved"
  correction_behavior: "invalidate-prior-result-and-rerun-independent-audit"
```
