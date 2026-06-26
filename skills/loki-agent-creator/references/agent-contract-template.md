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
    - "<sensitive_write_patterns>"
  tools: []
  required_skills:
    - "<technology_required_skills>"
  response_format: ""
  required_gates:
    - "<human_validation_gate>"
```

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
