# Command Contract Template

Use this reference when drafting a new command contract or auditing an existing command.

Replace angle-bracket placeholders with consumer-specific values. Keep this contract
engine/framework-agnostic; put technology rules in specialized skills generated from
technical retrospectives.

```yaml
command_contract:
  name: "loki:example"
  purpose: ""
  inputs:
    required: []
    optional: []
  outputs: []
  affected_runtime_surfaces:
    - "<consumer_runtime_surfaces>"
  affected_domain_ids:
    - "<domain_ids>"
  allowed_writes: []
  forbidden_writes:
    - ".agents/**"
    - "<sensitive_write_patterns>"
  required_skills:
    - "<technology_required_skills>"
  handoffs: []
  validators:
    - "<validators_for_consumer_runtime_surfaces>"
  human_gates:
    - "<human_validation_gate>"
  stop_conditions: []
  resume_contract: ""
```

## Research Basis

- Claude Code skills/custom commands: `https://code.claude.com/docs/en/skills`
- Claude Code hooks for command expansion enforcement: `https://code.claude.com/docs/en/hooks`
- Codex skills and progressive disclosure: `https://developers.openai.com/codex/skills`
- Codex customization and AGENTS.md layering: `https://developers.openai.com/codex/concepts/customization`
- Codex slash commands: `https://developers.openai.com/codex/cli/slash-commands`
