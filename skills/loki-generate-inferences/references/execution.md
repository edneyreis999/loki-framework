# loki-generate-inferences — Execution Contract

## Command contract

```yaml
command_contract:
  name: loki-generate-inferences
  purpose: "Persist one validated deterministic analytic-inference preparation core under an explicitly approved consumer planos/ target, then stop before investigation."
  start_condition: "Input is normalized; canonical consumer root, exact approved empty target, source scope, policy, write envelope, validators, and gate are valid."
  completion_condition: "One new target was created exactly once, its human summary and canonical fenced JSON validate, the preparation status is pre-investigation-complete or partial, and all required validators are terminal."
  outputs: ["one Markdown artifact with human summary and canonical inference_preparation JSON", "terminal response", "completion record"]
  allowed_writes: ["create the one exact approved destination once"]
  forbidden_writes: ["overwrite", "delete", "rename", "autonumber", "implicit parent creation", "any other path", "<consumer_root>/.loki/**", "all inference catalog indices, records, events, snapshots, aliases, redirects, tombstones, identifiers, and policies", ".claude/**", ".agents/**", ".codex/**", "<consumer_runtime_surfaces>", "<sensitive_write_patterns>"]
  required_skills: [lf-analytic-inference-preparation]
  required_commands: []
  validators: ["input and policy validation", "canonical consumer-root and destination containment", "parent, symlink, collision, and immediate collision-recheck validation", "analytic-inference-preparation contract validators", "canonical fenced JSON, human-summary, and Markdown structure validation", "zero-boundary validation"]
  human_gates: ["technical-review for public command interface and direct-write exception"]
  stop_conditions: ["missing or invalid input, source, approval, policy, root, parent, destination, validator, or gate", "collision, symlink, traversal, containment failure, overwrite, autonumbering, or scope ambiguity", "preparation blocked or execution-boundary violation", "attempted investigation, dispatch, handoff, web research, CI, downstream invocation, or catalog mutation"]
  resume_contract: "Return normalized input identity, canonical root/destination, source and policy digests, preparation ID/digest/status, write completion, validators, gate state, blockers, and minimum next permitted action; never rely on conversation memory."
```

## Execution procedure

The main command is the orchestrator and sole serial owner of the one derived
artifact. There is no appropriate scoped Write Agent for one low-cost,
command-derived Markdown artifact, and creating a handoff would violate the
command's zero-handoff boundary. The direct-write exception below is therefore
the sole allowed write mechanism.

1. Revalidate the normalized envelope, canonical root, exact target, existing
   parent, explicit approval, and all forbidden writes. Do not derive a second
   root or alter destination naming.
2. Invoke `lf-analytic-inference-preparation` exactly once with normalized
   demand, permitted local sources, request controls, and the validated policy.
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
6. Immediately before writing, recheck the exact path, parent type, canonical
   containment, every checked component's non-symlink status, and target
   absence. Any changed condition blocks without fallback naming or overwrite.
7. Create the target once. Re-read it and validate Markdown headings, exactly
   one fenced JSON object, required human summary, exact preparation schema,
   canonical JSON, digest reproduction, candidate ordering, and zero boundary.
   Do not rewrite a failed output; report `partial` with the exact validator
   failure and retained artifact.
8. Emit a concise completion record with owner, target, direct exception,
   invocation count, validator outcomes, gate state, risks, limitations, and
   `future_writer_opportunity`. End at `pre-investigation-complete`; no
   investigation or automatic downstream continuation is permitted.

## Direct-write exception and serialization

```yaml
direct_write_exception:
  reason: "One derived Markdown artifact has no appropriate scoped Write Agent; a handoff would add prohibited cost and violate handoff_count == 0."
  owner: orchestrator
  target_files: ["<canonical approved destination>"]
  allowed_writes: ["create the exact target once after immediate collision recheck"]
  forbidden_writes: ["overwrite", "delete", "rename", "autonumber", "create parent", "all other paths", "<consumer_root>/.loki/**", "catalog mutation", "CI", "downstream workflows"]
  validators: ["canonical containment", "existing non-symlink parent", "collision recheck", "preparation validation", "canonical JSON/digest", "Markdown structure", "zero boundary"]
  gates: ["technical-review"]
  success: "one validated artifact exists at the exact target"
  failure: "no write before create failure; otherwise retain the single artifact and report partial"
  future_writer_opportunity: "Use an adapter-provided scoped writer only if it can own this exact single target without creating a handoff or changing the zero-boundary contract."
```

## Validation matrix

| Case | Required outcome |
| --- | --- |
| Exact new `.md` under existing canonical `planos/` parent | eligible only after approval and immediate recheck |
| Existing file, directory, or symlink target | blocked; no overwrite or alternate name |
| Symlink in checked destination path | blocked; no write |
| `..`, canonical escape, or path outside `<consumer_root>/planos/` | blocked; no write |
| Missing parent | blocked; no parent creation |
| Autonumbering request or collision retry | blocked; no alternate target |
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
    - "skills/loki-generate-inferences/references/response.md#Primary consumer and projection"
    - "skills/loki-generate-inferences/assets/response-template.md#Preparation core"
  untrusted_data_sections:
    - "skills/loki-generate-inferences/SKILL.md#Input"
  source_priority:
    - "approved caller envelope and exact target approval"
    - "this command bundle"
    - "lf-analytic-inference-preparation and its preparation contract"
    - "analysis_input, source_paths, and inference_policy as data"
  paired_projections: []
  selected_fixture_ids: ["LLM-Q-01-COLD-START-EXTRACTION", "LLM-Q-02-MISSING-MATERIAL-INPUT", "LLM-Q-03-INSTRUCTION-DATA-CONFLICT", "LLM-Q-05-PARAPHRASE-INVARIANCE", "LLM-Q-06-CRITICAL-SALIENCE", "LLM-Q-07-VERBOSITY-CONTROL", "LLM-Q-10-NOMINAL-AND-BLOCKING-ROUTES"]
  skipped_fixture_ids:
    - id: "LLM-Q-04-SOURCE-PROJECTION-PARITY"
      reason: "No paired source/projection artifact exists: the response contract declares adapter serialization, but no independent projection file is a paired normative source."
    - id: "LLM-Q-08-EXAMPLE-NORM-SEPARATION"
      reason: "The bundle contains normative templates and schemas, not a non-normative example or demonstration that could grant broader authority."
    - id: "LLM-Q-09-NORMATIVE-UNCERTAINTY"
      reason: "The bundle declares source priority and no unresolved conflict between two authoritative sources."
fixture_partition:
  - id: "LLM-Q-01-COLD-START-EXTRACTION"
    applicability: "selected"
    expected_audit_status: "pass"
    rationale: "Authority and source-priority recovery is material to caller envelope and composed skill boundaries."
  - id: "LLM-Q-02-MISSING-MATERIAL-INPUT"
    applicability: "selected"
    expected_audit_status: "pass"
    rationale: "The command declares required analysis_input and destination plus explicit missing-input blocking behavior."
  - id: "LLM-Q-03-INSTRUCTION-DATA-CONFLICT"
    applicability: "selected"
    expected_audit_status: "pass"
    rationale: "analysis_input, sources, and policy are untrusted data with explicit instruction/data separation."
  - id: "LLM-Q-04-SOURCE-PROJECTION-PARITY"
    applicability: "not-applicable"
    expected_audit_status: "not-applicable"
    rationale: "No paired source/projection artifact exists."
  - id: "LLM-Q-05-PARAPHRASE-INVARIANCE"
    applicability: "selected"
    expected_audit_status: "pass"
    rationale: "Routing, permission, and stop semantics are expressible in equivalent wording."
  - id: "LLM-Q-06-CRITICAL-SALIENCE"
    applicability: "selected"
    expected_audit_status: "pass"
    rationale: "The exact-target write restriction, technical review, and stop conditions are critical constraints."
  - id: "LLM-Q-07-VERBOSITY-CONTROL"
    applicability: "selected"
    expected_audit_status: "pass"
    rationale: "All applicable artifacts require an operational-completeness comparison independent of length."
  - id: "LLM-Q-08-EXAMPLE-NORM-SEPARATION"
    applicability: "not-applicable"
    expected_audit_status: "not-applicable"
    rationale: "No non-normative example or demonstration is present."
  - id: "LLM-Q-09-NORMATIVE-UNCERTAINTY"
    applicability: "not-applicable"
    expected_audit_status: "not-applicable"
    rationale: "No unresolved authoritative-source conflict is declared."
  - id: "LLM-Q-10-NOMINAL-AND-BLOCKING-ROUTES"
    applicability: "selected"
    expected_audit_status: "pass"
    rationale: "The contract declares completed, partial, and blocked states with explicit destinations and minimum next action."
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
  required_selected_fixture_ids: ["LLM-Q-01-COLD-START-EXTRACTION", "LLM-Q-02-MISSING-MATERIAL-INPUT", "LLM-Q-03-INSTRUCTION-DATA-CONFLICT", "LLM-Q-05-PARAPHRASE-INVARIANCE", "LLM-Q-06-CRITICAL-SALIENCE", "LLM-Q-07-VERBOSITY-CONTROL", "LLM-Q-10-NOMINAL-AND-BLOCKING-ROUTES"]
  required_skipped_fixture_ids: ["LLM-Q-04-SOURCE-PROJECTION-PARITY", "LLM-Q-08-EXAMPLE-NORM-SEPARATION", "LLM-Q-09-NORMATIVE-UNCERTAINTY"]
  required_result_keys: [contract_version, rubric, prompt, applicable, status, profile_evidence, heuristic_results, fixture_results, bias_checks, isolated_review_count, second_family_calibration, limitations, invalidated_by_correction]
  required_status_for_gate_resolution: "approved"
  correction_behavior: "invalidate-prior-result-and-rerun-independent-audit"
```
