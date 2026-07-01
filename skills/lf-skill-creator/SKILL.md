---
name: lf-skill-creator
description: Create or update effective multi-adapter skills in the Loki Framework package for Codex and Claude Code. Use when designing a new skill, revising an existing skill, deciding whether a workflow belongs in a skill, or checking skill structure, frontmatter metadata, progressive disclosure, references, scripts, assets, and validation requirements.
when_to_use:
  - "Use when designing a new skill or revising an existing Loki skill."
  - "Use when checking skill structure, frontmatter metadata, progressive disclosure, references, scripts, assets, or validation requirements."
  - "Use when deciding whether reusable behavior belongs in a skill, command, agent, template, standard, or backlog item."
argument-hint: "[skill goal, trigger context, target adapters, validation needs]"
arguments:
  required: []
  optional:
    - skill_goal
    - trigger_context
    - target_adapters
    - validation_needs
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - durable package policy
  - cross-adapter metadata design
  - skill changes affect command workflows
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/lf-skill-creator/SKILL.md"
shell: {}
---

# lf-skill-creator

## Procedure

1. Confirm the skill's concrete use cases and trigger phrases.
2. Decide whether the need belongs in a `skill`, `command`, `agent`, `template`, `standard`, or backlog.
3. Run package preflight for packaged skills: confirm destination, namespace (`loki-` only for command wrappers with matching `commands/loki-*.md`, `lf-*` for internal helpers, domain prefixes for optional technology skills), installable layout, self-contained references, and required validations.
4. Use the installable skill layout:

```text
skill-name/
├── SKILL.md
└── references/
```

5. Gere skills multi-adapter por padrao. Nao ramifique o contrato pelo executor atual; some os metadados conhecidos de Claude Code e Codex, usando valores neutros validos quando um campo nao se aplicar.
6. Preencha o frontmatter superset de `SKILL.md`: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell`.
7. Quando houver suporte Codex app/plugin, inclua `agents/openai.yaml` com `interface.display_name`, `interface.short_description`, `interface.icon_small`, `interface.icon_large`, `interface.brand_color`, `interface.default_prompt`, `policy.allow_implicit_invocation` e `dependencies.tools[].type/value/description/transport/url`.
8. Keep `SKILL.md` focused on essential workflow, inputs, outputs, limits, and validation.
9. Put variant-specific detail, long examples, templates, platform notes, or source research in `references/`.
10. Validate that each skill directory has `SKILL.md`, YAML frontmatter, `name`, and `description`.
11. Update the local package manifest when a skill is added, removed, renamed, or moved.

## References

- Read [core-principles.md](references/core-principles.md) when deciding how much instruction to include, how strict the workflow should be, or how to preserve validation integrity.
- Read [anatomy-and-frontmatter.md](references/anatomy-and-frontmatter.md) when checking folder structure, `SKILL.md`, required metadata, trigger descriptions, multi-adapter frontmatter, or Codex `agents/openai.yaml` metadata.
- Read [resources-and-disclosure.md](references/resources-and-disclosure.md) when deciding what belongs in `SKILL.md` versus `references/`, `scripts/`, or `assets/`.
- Read [creation-process.md](references/creation-process.md) when creating a new skill or making a substantial revision.
- Read [validation-and-forward-testing.md](references/validation-and-forward-testing.md) when validating a skill folder or testing a complex skill.
- Read [naming-and-scope.md](references/naming-and-scope.md) when naming a skill or deciding whether the request belongs in a skill.
- Read [loki-package-rules.md](references/loki-package-rules.md) when adapting general skill guidance to this Loki package.

## Limits

- Do not install skills into `.claude/**`, `.codex/**`, or `.agents/**` without explicit approval.
- Do not keep large conditional material in `SKILL.md` when a reference file would preserve context.
- Do not branch the generated skill by the current executor; generate the multi-adapter metadata superset.
- Do not create auxiliary README/changelog files inside a skill unless a platform explicitly requires them.
- Do not leave package validation implicit; packaged skill work must finish with structural and self-containment checks.

## Required Gates

- `technical-review` for changes to packaged skills.
- `approval` for installation, promotion to normative framework behavior, or broad workflow changes.
