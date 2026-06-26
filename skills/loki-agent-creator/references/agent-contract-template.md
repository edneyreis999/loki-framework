# Agent Contract Template

Use this reference when drafting a new agent contract or auditing an existing agent.

Replace angle-bracket placeholders with consumer-specific values. Do not encode project,
engine, or framework rules in this base contract; route those rules through specialized
skills listed in `<technology_required_skills>`.

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

- Claude Code subagents: `https://code.claude.com/docs/en/sub-agents`
- Claude Code skills and subagent execution: `https://code.claude.com/docs/en/skills`
- Codex subagents and custom agents: `https://developers.openai.com/codex/subagents`
- Codex customization layers: `https://developers.openai.com/codex/concepts/customization`
- OpenAI Agents SDK agents, handoffs, guardrails and tracing: `https://openai.github.io/openai-agents-python/agents/`
