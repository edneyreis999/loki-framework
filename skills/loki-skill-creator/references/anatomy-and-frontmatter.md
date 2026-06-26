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
