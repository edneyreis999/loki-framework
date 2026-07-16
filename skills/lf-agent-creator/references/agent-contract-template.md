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
  capabilities:
    - "read-only-analysis | proposal | scoped-write | write-test"
  active_mode: "read-only | proposal-only | scoped-writer | write-test"
  purpose: ""
  when_to_trigger: []
  inputs: []
  outputs: []
  allowed_writes: []
  init_write_mode: "init_context_scoped_writer"
  scoped_write_modes:
    - "init_context_scoped_writer"
    - "task_scoped_writer"
  task_write_mode: "task_scoped_writer"
  task_allowed_writes:
    - "<task_allowed_files>"
  scoped_write_domains:
    - "<domain-artifact-type>"
  forbidden_writes:
    - ".agents/**"
    - ".claude/**"
    - ".codex/**"
    - "<sensitive_write_patterns> outside approved task envelope"
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
    - "<interview | approval | human-validation | technical-review>"
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
    mode: "none | init_context_scoped_writer | task_scoped_writer"
    target_files: []
    allowed_writes: []
    scoped_write_domains: []
    validators: []
    human_gates: []
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
```

## Operational modes and 24/24 evidence

Capabilities may coexist, but the caller selects one `active_mode` per handoff.
`read-only`/`proposal-only` never create persistent files. `scoped-writer`
receives exact targets, owner, allowed/forbidden writes, validators, gates,
success/failure destinations and removes temporary validation artifacts unless
the approved envelope preserves plan evidence. `write-test` writes only the
approved deterministic test surface; it never changes production.

Before handoff record `sim|não`, file and heading for: (1) capability/mode
contract; (2) narrow responsibility; (3) mode bounded by capability/envelope;
(4) triggers/inputs/outputs/completion; (5) scoped allowed writes; (6)
forbidden writes; (7–8) known success/failure destinations; (9) deterministic
validation distinct from human gate; (10) stop conditions; (11) structured
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
