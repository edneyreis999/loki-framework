# Agent Contract Template

Use this reference when drafting a new agent contract or auditing an existing agent.

Replace angle-bracket placeholders with consumer-specific values. Do not encode project,
engine, or framework rules in this base contract; route those rules through specialized
skills listed in `<technology_required_skills>`.

## Multi-Adapter Metadata Superset

Use one Loki source contract and include the union of known metadata. Generate
runtime projections only when the platform requires a different file format.

```yaml
metadata_superset:
  loki_common:
    - name
    - description
    - type
    - status
    - mode
    - purpose
    - when_to_trigger
    - inputs
    - outputs
    - allowed_writes
    - forbidden_writes
    - response_format
    - confidence
    - risks
    - required_gates
    - model_class
    - effort
    - escalation_signals
    - adapter_projection
    - isolation
  claude_code_subagent:
    - name
    - description
    - tools
    - disallowedTools
    - model
    - permissionMode
    - maxTurns
    - skills
    - mcpServers
    - hooks
    - memory
    - background
    - effort
    - isolation
    - color
    - initialPrompt
  codex_custom_agent_toml:
    - name
    - description
    - developer_instructions
    - nickname_candidates
    - model
    - model_reasoning_effort
    - sandbox_mode
    - approval_policy
    - mcp_servers
    - skills.config
```

For Claude Code, the Markdown file with YAML frontmatter is the runtime
subagent definition. For Codex, emit a TOML projection in `codex/agents/`
because Codex custom agents are TOML files.

```yaml
agent_contract:
  name: "example-agent"
  installed_in_consumer: false
  category: "Write Agent | Read Agent | Review Agent | other"
  operational_role: "domain-investigator | domain-task-writer | package-writer | consumer-doc-cataloger | other"
  capabilities:
    - "read-only-analysis | proposal | scoped-write | write-test"
  active_mode: "read-only | proposal-only | scoped-writer | write-test"
  purpose: ""
  when_to_trigger: []
  inputs: []
  outputs: []
  allowed_writes: []
  init_role: "init_inventory_domain_investigator | init_support_only | init_serial_cataloger | not-applicable"
  init_execution_modes:
    - "read-only"
    - "proposal-only"
  init_investigator_output:
    research_packet_schema: "loki_init_research_packet v1"
    packet_batch: "1..N structured research packets returned to orchestrator"
    continuation: "continue | complete | blocked plus logical cursor"
    completion_record: "compact result separate from orchestrator-owned execution evidence"
    success_destination: "loki-init packet intake"
    failure_destination: "loki-init blocker intake"
  calling_workflow: "<caller-provided workflow identity>"
  write_class: "none | task-artifact | consumer-docs | package-documentation"
  write_class_constraints:
    consumer_docs: "catalogador only; no fallback"
    package_documentation: "approved internal package-writer role only"
    domain_agent_init: "none"
  resolved_roots:
    consumer_project_root: "<caller-resolved root>"
    package_root: "<caller-resolved root or not-applicable>"
    durable_context_root: "<declared consumer domain-context root or not-applicable>"
  scoped_write_modes:
    - "task_scoped_writer"
  task_write_mode: "task_scoped_writer"
  task_allowed_writes:
    - "<task_allowed_files>"
  scoped_write_domains:
    - "<domain-artifact-type>"
  domain_context_preflight:
    required_when: "installed_in_consumer AND category == Write Agent AND task_write_mode includes task_scoped_writer AND durable_context_root is declared AND agent is a domain agent"
    skill: "lf-domain-context-preflight"
    execution_owner: "this agent before ordinary task write"
    accepted_states: ["ready", "ready-with-gaps"]
    blocking_state: "blocked"
    source_precedence: "current local source prevails over durable snapshot"
    gap_handoff: "caller-provided documentation handoff destination"
    self_fix_consumer_docs: false
  forbidden_writes:
    - ".agents/**"
    - ".claude/**"
    - ".codex/**"
    - "<sensitive_write_patterns> outside approved task envelope"
    - "consumer docs by any non-catalogador agent, including init fallback"
    - "package documentation unless operational_role is the approved internal package writer"
  tools:
    - Read
  required_skills:
    - "<technology_required_skills>"
  model_class: "frontier_reasoning | coding | generalist | long_context | fast_low_cost | specialist_generalist_human_like"
  effort: "low | medium | high | xhigh"
  escalation_signals: []
  isolation: "read-only | proposal-only | scoped-writer | delegated-write-after-approval"
  adapter_projection:
    claude_code: "Project to subagent frontmatter/settings only when supported."
    codex: "Project to codex/agents/*.toml or profile for strong enforcement."
  response_format: ""
  required_gates:
    - "<interview | approval | human-validation>"
  success_destination: "<orchestrator or named next owner>"
  failure_destination: "<orchestrator or correcting owner>"
  stop_conditions:
    - "<missing envelope, scope, permission, validator, gate or handoff destination>"
  completion_criteria: "<observable result and validation evidence>"
```

## Model and Effort Rules

Use `docs/model-effort-guidance.md` as the source for provider-neutral
classification. Prefer `model_class` and `effort` over concrete provider model
IDs in the Markdown contract.

Use `model: inherit` or omit a concrete `model` when the runtime cannot enforce
that field or when the agent should follow the orchestrator. Use `effort:
medium` for normal proposal-only work, code review or bounded synthesis. Use
`effort: high` for durable package policy, multi-source research, conflicting
evidence, complex architecture, high-risk implementation proposals or agents
that influence future command/skill/template behavior.

Claude Code can apply model and effort through supported subagent or skill
frontmatter and configuration precedence. Codex does not get strong enforcement
from Markdown alone; project enforceable settings into `codex/agents/*.toml`,
configuration profiles or explicit runtime selection.

## Response Format

```yaml
parallel_agent_response:
  agent: ""
  mode: "read-only | proposal-only | scoped-writer"
  summary: ""
  affected_files: []
  write_scope:
    mode: "none | task_scoped_writer"
    calling_workflow: ""
    write_class: "none | task-artifact | consumer-docs | package-documentation"
    resolved_root: ""
    target_files: []
    allowed_writes: []
    scoped_write_domains: []
    validators: []
    human_gates: []
  init_investigation:
    role: "init_inventory_domain_investigator | not-applicable"
    research_packet_refs: []
    continuation_status: "continue | complete | blocked | not-applicable"
    continuation_cursor: ""
  domain_context_preflight:
    required: false
    status: "ready | ready-with-gaps | blocked | not-applicable"
    durable_context_refs: []
    current_source_refs: []
    gap_handoff: ""
  affected_runtime_surfaces:
    - "<consumer_runtime_surfaces>"
  affected_domain_ids:
    - "<domain_ids>"
  evidence: []
  findings: []
  risks: []
  confidence: "low | medium | high"
  model_class: ""
  effort: "low | medium | high | xhigh"
  required_validations: []
  proposed_next_step: ""
  completion_record:
    result: ""
    files: []
    validators: []
    gates: []
    next_destination: ""
  execution_evidence: "orchestrator-owned reference or explicit partial | unavailable | unsupported"
```

## Operational modes and 24/24 evidence

Capabilities may coexist, but the caller selects one `active_mode` per handoff.
`read-only`/`proposal-only` never create persistent files. `scoped-writer`
receives exact targets, owner, allowed/forbidden writes, validators, gates,
success/failure destinations and removes temporary validation artifacts unless
the approved envelope preserves plan evidence. `write-test` writes only the
approved deterministic test surface; it never changes production.

For init, a domain agent is an `init_inventory_domain_investigator` in
`read-only` or `proposal-only`. It returns structured research packets and a
continuation cursor to the orchestrator and has no consumer-doc authority.
Only `catalogador` authors consumer docs, with no domain-agent fallback.

Before an ordinary exact-target task write outside consumer docs, a domain
Write Agent runs its own `lf-domain-context-preflight` when the canonical
metadata formula above applies. `active_mode` may be `scoped-writer`; preflight
applicability reads `task_write_mode`, not `active_mode`. Support-only agents,
`catalogador`, internal package writers and agents without a declared durable
context root do not satisfy the formula. Current local sources prevail over durable snapshots; gaps are
handed to the caller-provided documentation route and never self-fixed in docs.
Classify `consumer-docs` versus `package-documentation` from the resolved root;
only the approved internal package-writer role may maintain package docs.

## Conditional LLM-Facing Quality Gate

Before delivery, classify the created or revised agent with
[lf-documentation-writing](../../lf-documentation-writing/SKILL.md). When the
classification is positively LLM-facing, require a complete
`llm_artifact_profile`, application of the
[canonical LLM artifact quality contract](../../lf-documentation-writing/references/llm-artifact-quality-validation.md),
and an independent `llm_consumption_quality` result in which every applicable
fixture passes. Do not copy the canonical rubric, schemas, or fixture
definitions into this creator contract.

Use these terminal semantics:

- positive LLM-facing classification without the complete profile, canonical
  contract, independent result, or with any non-passing applicable fixture:
  mark the existing validation/gate item `não` and block delivery;
- positive LLM-facing classification with the complete profile and independent
  result approved: the conditional gate is `sim`, and completion remains
  subject to every existing gate in this checklist;
- exclusively human-facing: record `not-applicable` with a concrete human-only
  reason and do not run irrelevant fixtures.

Before handoff record `sim|não`, file and heading for: (1) capability/mode
contract; (2) narrow responsibility; (3) mode bounded by capability/envelope;
(4) triggers/inputs/outputs/completion; (5) scoped allowed writes; (6)
forbidden writes; (7–8) known success/failure destinations; (9) deterministic
validation distinct from human gate, including the conditional LLM-facing gate
above when applicable; (10) stop conditions; (11) structured
response; (12) minimum tools/permissions/gates; (13–19) scoped-writer envelope,
validation, temporary isolation/removal, deterministic-test specification,
human-test route and honest completion record; (20) relevant preflight docs;
(21–22) write-test restriction and handoffs; (23–24) no-write proposal mode and
structured recommendation. Any `não` blocks delivery.

## Research Basis

- Claude Code subagents: `https://docs.anthropic.com/en/docs/claude-code/sub-agents`
- Claude Code skills and subagent execution: `https://docs.anthropic.com/en/docs/claude-code/skills`
- Claude Code model configuration: `https://docs.anthropic.com/en/docs/claude-code/model-config`
- Codex subagents and custom agents: `https://developers.openai.com/codex/subagents`
- Codex basic configuration: `https://developers.openai.com/codex/config-basic`
- Codex advanced configuration: `https://developers.openai.com/codex/config-advanced`
- OpenAI Agents SDK agents, handoffs, guardrails and tracing: `https://openai.github.io/openai-agents-python/agents/`
