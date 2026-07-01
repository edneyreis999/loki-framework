# Naming and Scope

Use this reference when naming a skill or deciding whether the requested artifact should be a skill.

## Naming

- Use lowercase letters, digits, and hyphens only.
- Keep names under 64 characters.
- Prefer short, verb-led names.
- Namespace by tool or domain when it improves triggering.
- Match the folder name to the skill name.

## Loki Package Namespace

- Reserve `loki-*` under `skills/` for command wrapper skills backed by a
  matching `commands/loki-*.md` file.
- Use `lf-*` for internal Loki Framework helper skills that must remain
  installable for consumers but should not appear under the `$loki-` command
  filter.
- Use a domain or technology namespace for optional technology skills, such as
  `rpg-maker-mz-*`, instead of `loki-*`.
- Keep the folder name and top-level `name` equal after every rename.

## Skill Versus Other Artifacts

Create a skill when the reusable unit is procedural knowledge, domain expertise, or a workflow fragment that can be loaded on demand.

Do not create a skill when:

- the unit is a full invocable flow with state, gates, and outputs: create a command;
- the unit is a specialist role with independent judgment or isolated context: create an agent;
- the unit is only output shape: create a template;
- the unit is a durable rule: create a standard;
- evidence is insufficient: create a backlog item.

## Scope

Keep each skill focused on one job. If one skill starts covering multiple unrelated variants, split it or move variant detail into references.
