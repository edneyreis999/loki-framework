# Anatomy and Frontmatter

Use this reference when checking skill folder structure, `SKILL.md`, frontmatter, and trigger behavior.

## Required Layout

```text
skill-name/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

Only `SKILL.md` is required. Other directories are optional and should exist only when they directly support the skill.

## Required Frontmatter

```yaml
---
name: skill-name
description: Explain what this skill does and when to use it.
---
```

`name` and `description` are the core metadata. The `description` is the primary trigger surface: include what the skill does and the concrete contexts where it should be used.

Put "when to use" information in `description`, not only in the body. The body loads only after the skill is selected.

## Multi-Adapter Metadata

Generate new Loki skills with the union of known Codex and Claude Code
metadata. The active runtime can use the fields it supports and ignore the rest.

`SKILL.md` frontmatter superset:

- `name`
- `description`
- `when_to_use`
- `argument-hint`
- `arguments`
- `disable-model-invocation`
- `user-invocable`
- `allowed-tools`
- `disallowed-tools`
- `model`
- `effort`
- `model_class`
- `adapter_projection`
- `escalation_signals`
- `context`
- `agent`
- `hooks`
- `paths`
- `shell`

Codex app/plugin metadata belongs in `agents/openai.yaml`:

- `interface.display_name`
- `interface.short_description`
- `interface.icon_small`
- `interface.icon_large`
- `interface.brand_color`
- `interface.default_prompt`
- `policy.allow_implicit_invocation`
- `dependencies.tools[].type`
- `dependencies.tools[].value`
- `dependencies.tools[].description`
- `dependencies.tools[].transport`
- `dependencies.tools[].url`

### Model and Effort Metadata

Use provider-neutral intent metadata for model/effort semantics in Loki package
sources. When running inside the package source, `docs/model-effort-guidance.md`
may be used as an optional central reference, not as an installed-skill runtime
dependency:

```yaml
model: inherit
effort: medium
model_class: generalist
context: standard
agent: main
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
```

Use `model: inherit` when the skill should follow the orchestrator or when the
adapter does not enforce model selection from `SKILL.md`. Omit a concrete model
unless the package is intentionally creating an adapter-specific projection.

Use `effort: medium` for normal reusable skills. Use `effort: high` for durable
documentation policy, technical analysis, action-plan authoring, command/agent
creation, multi-source research or high-risk package decisions. Use `effort:
low` only for lookup, triage, local routing or transient bookkeeping.

Claude Code can apply supported frontmatter in skills or subagents according to
its runtime rules. Codex should treat `model` and `effort` in `SKILL.md` as
advisory unless projected into a profile, command invocation or custom agent
TOML.

## Body

Use the body for instructions after activation:

- workflow;
- inputs;
- outputs;
- limits;
- references to load conditionally;
- validation requirements.

## Optional UI Metadata

`agents/openai.yaml` can add UI metadata, default prompts, invocation policy, and dependencies. Generate or update it only when the package intends to support that UI surface.

Do not add optional interface fields such as icons or brand colors unless they are explicitly provided.
