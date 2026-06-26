---
name: loki-skill-creator
description: Create or update effective Codex skills in the Loki Framework package. Use when designing a new skill, revising an existing skill, deciding whether a workflow belongs in a skill, or checking skill structure, frontmatter, progressive disclosure, references, scripts, assets, and validation requirements.
---

# loki-skill-creator

## Procedure

1. Confirm the skill's concrete use cases and trigger phrases.
2. Decide whether the need belongs in a `skill`, `command`, `agent`, `template`, `standard`, or backlog.
3. Run package preflight for packaged skills: confirm destination, `loki-` namespace when applicable, installable layout, self-contained references, and required validations.
4. Use the installable skill layout:

```text
skill-name/
├── SKILL.md
└── references/
```

5. Keep `SKILL.md` focused on essential workflow, inputs, outputs, limits, and validation.
6. Put variant-specific detail, long examples, templates, platform notes, or source research in `references/`.
7. Include `name` and `description` as top-level frontmatter fields. Put trigger context in `description`, because the body loads only after the skill is selected.
8. Validate that each skill directory has `SKILL.md`, YAML frontmatter, `name`, and `description`.
9. Update the local package manifest when a skill is added, removed, renamed, or moved.

## References

- Read [core-principles.md](references/core-principles.md) when deciding how much instruction to include, how strict the workflow should be, or how to preserve validation integrity.
- Read [anatomy-and-frontmatter.md](references/anatomy-and-frontmatter.md) when checking folder structure, `SKILL.md`, required metadata, trigger descriptions, or optional UI metadata.
- Read [resources-and-disclosure.md](references/resources-and-disclosure.md) when deciding what belongs in `SKILL.md` versus `references/`, `scripts/`, or `assets/`.
- Read [creation-process.md](references/creation-process.md) when creating a new skill or making a substantial revision.
- Read [validation-and-forward-testing.md](references/validation-and-forward-testing.md) when validating a skill folder or testing a complex skill.
- Read [naming-and-scope.md](references/naming-and-scope.md) when naming a skill or deciding whether the request belongs in a skill.
- Read [loki-package-rules.md](references/loki-package-rules.md) when adapting general skill guidance to this Loki package.

## Limits

- Do not install skills into `.claude/**`, `.codex/**`, or `.agents/**` without explicit approval.
- Do not keep large conditional material in `SKILL.md` when a reference file would preserve context.
- Do not create auxiliary README/changelog files inside a skill unless a platform explicitly requires them.
- Do not leave package validation implicit; packaged skill work must finish with structural and self-containment checks.

## Required Gates

- `technical-review` for changes to packaged skills.
- `approval` for installation, promotion to normative framework behavior, or broad workflow changes.
