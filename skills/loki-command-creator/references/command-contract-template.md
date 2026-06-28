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
    - ".claude/**"
    - ".agents/**"
    - ".codex/**"
    - "<sensitive_write_patterns>"
  required_skills:
    - "<technology_required_skills>"
  execution_profile:
    model_class: "frontier_reasoning | coding | generalist | long_context | fast_low_cost | specialist_generalist_human_like"
    default_effort: "low | medium | high"
    max_effort: "medium | high | xhigh"
    escalation_signals:
      - "durable package policy"
      - "conflicting evidence"
      - "high-risk implementation"
    handoff_effort:
      research: "medium | high"
      coding: "medium | high"
      documentation_transient: "low | medium"
      documentation_durable: "high"
      validator: "low | medium"
    adapter_projection:
      codex: "Advisory unless projected through config, profile or custom agent."
      claude_code: "May map to model/effort frontmatter where supported."
  handoffs: []
  validators:
    - "<validators_for_consumer_runtime_surfaces>"
  human_gates:
    - "<interview | approval | human-validation | technical-review>"
  stop_conditions: []
  resume_contract: ""
```

## Execution Profile Rules

Command contracts should declare model and effort intent with provider-neutral
classes. Do not make concrete provider model IDs mandatory in command
templates. When running inside the package source, `docs/model-effort-guidance.md`
may be used as an optional central reference, not as an installed-skill runtime
dependency.

Use `default_effort` for the normal command path and `max_effort` for explicit
escalation. Typical command orchestration starts at `medium` or `high`;
transient bookkeeping handoffs can be `low`, while durable package policy,
technical analysis, action-plan generation and complex multi-source decisions
should be `high`.

`handoff_effort` should describe the effort expected from read-only or
proposal-only agents. It does not override a later task, technology skill or
human gate.

`adapter_projection` must state whether the active adapter can enforce the
metadata. For Codex, treat this guidance as advisory unless it is projected into
a profile, command invocation or custom agent. For Claude Code, project only to
supported frontmatter/settings surfaces.

## Research Basis

- Claude Code skills/custom commands: `https://code.claude.com/docs/en/skills`
- Claude Code hooks for command expansion enforcement: `https://code.claude.com/docs/en/hooks`
- Codex skills and progressive disclosure: `https://developers.openai.com/codex/skills`
- Codex customization and AGENTS.md layering: `https://developers.openai.com/codex/concepts/customization`
- Codex slash commands: `https://developers.openai.com/codex/cli/slash-commands`
