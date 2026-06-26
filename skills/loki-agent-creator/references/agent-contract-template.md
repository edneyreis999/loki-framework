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
  mode: "read-only | proposal-only"
  purpose: ""
  when_to_trigger: []
  inputs: []
  outputs: []
  allowed_writes: []
  forbidden_writes:
    - ".agents/**"
    - ".claude/**"
    - ".codex/**"
    - "<sensitive_write_patterns>"
  tools: []
  required_skills:
    - "<technology_required_skills>"
  model_class: "frontier_reasoning | coding | generalist | long_context | fast_low_cost | specialist_generalist_human_like"
  effort: "low | medium | high | xhigh"
  escalation_signals: []
  isolation: "read-only | proposal-only | delegated-write-after-approval"
  adapter_projection:
    claude_code: "Project to subagent frontmatter/settings only when supported."
    codex: "Project to codex/agents/*.toml or profile for strong enforcement."
  response_format: ""
  required_gates:
    - "<interview | approval | runtime-validation | technical-review>"
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
  mode: "read-only | proposal-only"
  summary: ""
  affected_files: []
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

## Research Basis

- Claude Code subagents: `https://docs.anthropic.com/en/docs/claude-code/sub-agents`
- Claude Code skills and subagent execution: `https://docs.anthropic.com/en/docs/claude-code/skills`
- Claude Code model configuration: `https://docs.anthropic.com/en/docs/claude-code/model-config`
- Codex subagents and custom agents: `https://developers.openai.com/codex/subagents`
- Codex basic configuration: `https://developers.openai.com/codex/config-basic`
- Codex advanced configuration: `https://developers.openai.com/codex/config-advanced`
- OpenAI Agents SDK agents, handoffs, guardrails and tracing: `https://openai.github.io/openai-agents-python/agents/`
