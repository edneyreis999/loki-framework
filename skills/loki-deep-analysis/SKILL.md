---
name: loki-deep-analysis
description: Run the public Loki deep-analysis workflow. Use when a demand needs evidence-first technology discovery, selective analytic-inference retrieval, contextual candidate expansion, useful independent investigations, and one traceable report without mutating the inference catalog.
when_to_use:
  - "Use when a brief, specification, feedback item, runtime question, or direct request needs deeper multi-source investigation than an ordinary answer."
  - "Use when analysis should reuse catalogued analytic inferences while remaining free to generate contextual candidates beyond the catalog."
argument-hint: "[analysis_input, optional source_paths, destination, inference_policy]"
arguments:
  required:
    - analysis_input
  optional:
    - source_paths
    - destination
    - inference_policy
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
  - uncertain technology or conflicting evidence
  - independent investigation fan-out near policy limits
  - missing specialist capability or non-terminal handoff
  - report destination or interaction-gate target ambiguity
context: standard
agent: main
hooks: {}
paths:
  package_bundle: "skills/loki-deep-analysis/"
  execution: "references/execution.md"
  response: "references/response.md"
  response_template: "assets/response-template.md"
  analytic_report_contract: "references/analytic-report-contract.md"
shell: bash
type: command
serialization: skill-bundle
domain: analysis
required_skills:
  - lf-analytic-inference-preparation
  - lf-analytic-inference
  - lf-tech-analysis-authoring
  - lf-agentic-orchestration
  - lf-agent-execution-evidence
required_commands: []
status: draft
used_by:
  - loki-deep-analysis
---

# loki-deep-analysis

## Input

Entre no modo Plan e peça os parâmetros de entrada para o workflow.

```yaml
parameters:
  - key: analysis_input
    input_type: string | path
    requirement: required
    description: "Brief, PRD, NSD, feedback, specification, runtime question, or direct request that defines the analysis object."
  - key: source_paths
    input_type: list[path]
    requirement: optional
    default: []
    description: "Caller-provided readable local sources; an empty list requires explicit discovery limits and evidence gaps."
  - key: destination
    input_type: path
    requirement: optional
    default: null
    description: "Exact approved Markdown report file; null produces a response-only report and authorizes no file write."
  - key: inference_policy
    input_type: object | path
    requirement: optional
    default: null
    description: "Approved policy override; null uses the versioned active policy bundled with lf-analytic-inference."
```

Require `analysis_input`. Accept a non-empty string or a readable regular file;
when its shape could be either, resolve the caller's intent without silently
changing it. Validate `source_paths` as a list of readable files or approved
directories, canonicalize each path, reject traversal or scope escape, and
record an empty list as a discovery constraint rather than evidence of absence.

When `destination` is present, require an exact `.md` file path, an existing
writable parent, explicit write approval, canonical containment in the caller's
allowed scope, and a collision decision before Execution. Canonical containment
is a public Input precondition: validate it against the one `consumer_root`
returned by the mandatory preparation invocation, never through a second root
resolution. Do not create a directory or overwrite an existing file during
Input. When it is null, normalize `allowed_writes: []` unless a later human
decision creates one exact interaction-gate target with its own approval.

Validate `inference_policy` as a mapping or a readable JSON file. An override
must declare schema, provenance, authorization and digest; reject invalid,
unapproved, negative, identity-changing, or invariant-weakening values. Never
infer approval from the presence of the object. Absence selects the active
policy bundled with `lf-analytic-inference`.

Do not accept a root parameter or infer/override a root from adapter metadata,
Git, environment, source/report paths, documentation or `.loki` presence. The
mandatory preparation invocation resolves the internal `consumer_root` exactly
once from canonical `pwd`, records `canonical-pwd` provenance, and derives the
fixed state root `<consumer_root>/.loki/analytic-inference/v2`. That XML v2
layout is the only active layout; v1/JSON is legacy read-only and never a
lookup fallback.

Identify every missing or invalid required input and request it before
continuing. Do not invent sources, technologies, destination, policy,
specialist capability, approval, validator, gate, cost, or evidence. Normalize
the objective, parameters, canonical sources, discovery limits, destination,
policy identity/digest, allowed and forbidden writes, risks, validators, gates,
known gaps, completion criteria, and exact interaction target if independently
approved. The preparation result adds the canonical consumer/state roots and
root source; callers must reuse it rather than resolve them again.

During Input do not inspect the catalog, conduct the analysis, invoke
`loki-tech-analysis`, delegate investigations, write a report or interaction
record, mutate any catalog surface, or declare success.

## Execution

Read [references/execution.md](references/execution.md) completely before
acting and follow every reference it conditionally routes. Preserve its write,
catalog, handoff, evidence, validation, gate, stop and resume boundaries.

## Response

Read [references/response.md](references/response.md) completely and fill
[assets/response-template.md](assets/response-template.md) for the terminal
response. The primary consumer is `both`; preserve the actual status,
artifacts, evidence, validators, handoffs, gates, approvals, risks, gaps,
resume state and next steps.
