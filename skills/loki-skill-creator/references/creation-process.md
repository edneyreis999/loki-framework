# Creation Process

Use this reference when creating a new skill from scratch or making a substantial revision.

## 1. Understand Use Cases

Identify concrete examples:

- What should trigger the skill?
- What should not trigger it?
- What inputs does the user provide?
- What output should exist when the skill succeeds?
- Is this truly a skill, or should it be a command, agent, template, standard, or backlog item?

Skip only when usage patterns are already obvious.

## 2. Plan Reusable Contents

For each example, decide what reusable resources are useful:

- `references/` for domain knowledge or long examples;
- `scripts/` for deterministic repeated operations;
- `assets/` for output resources;
- no extra resources when instruction-only is enough.

Before writing packaged files, confirm the package guardrails:

- installable layout under `skills/<skill-name>/SKILL.md`;
- `loki-` namespace when the skill belongs to the package namespace;
- top-level `description`;
- conditional detail split into `references/`;
- no external normative dependency outside the package root.

## 3. Create the Skill Directory

For an installable skill, use:

```text
skill-name/
└── SKILL.md
```

Use lowercase letters, digits, and hyphens. Prefer short, verb-led names under 64 characters.

For this Loki package, create skills under:

```text
<package-root>/skills/<skill-name>/SKILL.md
```

## 4. Edit `SKILL.md`

Write imperative instructions for another agent.

Keep the body lean and move conditional detail to references. Include:

- purpose;
- procedure;
- inputs;
- outputs;
- limits;
- required gates or validation.

## 5. Update Package Metadata

When adding or moving a skill in this package, update:

- `manifest.yaml`;
- installation/usage docs when path conventions change.

## 6. Validate

Finish with package checks, not only a visual review:

- `SKILL.md`, `name`, `description`, folder/name match;
- no loose Markdown files directly in `skills/`;
- no forbidden project-specific or external normative references;
- manifest entries still point to existing files.
