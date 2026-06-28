# Loki Package Rules

Use this reference when adapting general skill creation guidance to the Loki Framework local package.

## Package Location

Create packaged skills under:

```text
<package-root>/skills/<skill-name>/SKILL.md
```

This package is an auditable source, not an automatic installation target.

For Loki-packaged skills:

- use `skills/<skill-name>/SKILL.md`;
- keep the folder name equal to top-level `name`;
- use `loki-` prefix when the skill belongs to the Loki package namespace;
- keep conditional detail in `references/`, not in a monolithic `SKILL.md`;
- do not leave loose `.md` files directly under `skills/`.

## Engine/Framework Agnosticism

Core Loki package rules, commands, agents, templates, and base skills must stay
engine/framework-agnostic. Do not bake consumer project rules into core artifacts.

Use placeholders until a consumer-specific layer resolves them:

- `<consumer_runtime_surfaces>` for runtime files, generated artifacts, or other external surfaces;
- `<sensitive_write_patterns>` for paths requiring approval, ownership, or serialization;
- `<technology_required_skills>` for specialized skills that carry technology rules;
- `<domain_ids>` for consumer-domain identifiers;
- `<human_validation_gate>` for manual validation required by a consumer runtime.

Technology learnings from technical retrospectives should become specialized skills,
not base package rules. The only packaged skills allowed to retain consumer-specific
engine rules are `loki-rpg-maker-mz-data-json` and `loki-rpg-maker-mz-plugin-workflow`.

## Installation Boundaries

Do not copy or install into these paths without explicit approval:

- `.claude/**`;
- `.codex/**`;
- `.agents/**`.

`.agents/**` is local-only and deny-by-default. Never treat it as a normative source for the package.

## Self-Containment Rules

Never make a packaged skill depend on:

- blueprint or plan files outside the package root;
- a project-specific path such as a game name or workspace path;
- `.agents/**` or `.claude/**` as normative source material.
- package `docs/*.md` files as an operational runtime dependency after the
  skill is installed in a consumer project.

Packaged skills must be installable and self-contained. Any package-doc rule
that is required for the skill to execute must be summarized inside `SKILL.md`
or a bundled `references/` file. Package docs such as
`docs/operational-inventory.md`, `docs/model-effort-guidance.md` or
`docs/package-authoring-guardrails.md` may be optional context when running
inside the package source, but a missing package doc must not block an
installed skill in a consumer project.

Classify external references before keeping them:

- installation targets such as `.claude/**`, `.codex/**`, `.agents/**` are allowed as destinations;
- consumer runtime surfaces must be represented as `<consumer_runtime_surfaces>` until a specialized skill defines them;
- sensitive write paths must be represented as `<sensitive_write_patterns>` until a specialized skill defines them;
- normative package sources must remain inside the package root.

## Manifest

Register packaged skills in:

```text
<package-root>/manifest.yaml
```

Use paths like:

```yaml
file: "skills/example-skill/SKILL.md"
```

## Gates

Use:

- `technical-review` for packaged command, skill, agent, template, validator, or consolidated doc changes;
- `approval` for installation, policy changes, or normative promotion;
- `<human_validation_gate>` when behavior in `<consumer_runtime_surfaces>` requires manual validation.

## Minimum Validation

Packaged skill work should end with objective checks:

- `SKILL.md` exists;
- frontmatter parses;
- top-level `name` and `description` exist;
- folder name matches `name`;
- no loose `.md` files remain under `skills/`;
- `manifest.yaml` points to existing files;
- no forbidden external normative paths were introduced.
