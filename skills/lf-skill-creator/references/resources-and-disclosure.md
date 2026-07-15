# Resources and Progressive Disclosure

Use this reference when deciding what belongs in `SKILL.md` versus `references/`, `scripts/`, or `assets/`.

## Progressive Disclosure

Skills use three loading levels:

1. Metadata: `name` and `description`.
2. `SKILL.md`: loaded when the skill triggers.
3. Bundled resources: loaded or executed only when needed.

Keep `SKILL.md` focused. Split conditional detail into references when the file grows large or supports multiple variants.

## References

Use `references/` for documentation loaded only in specific situations:

- schemas;
- policies;
- detailed examples;
- platform-specific notes;
- templates too long for `SKILL.md`;
- source research.

Keep reference files one level from `SKILL.md`. In `SKILL.md`, describe exactly when to read each reference.

Avoid duplication between `SKILL.md` and references.

## Scripts

Use `scripts/` when deterministic behavior matters or the same code would be rewritten repeatedly.

Test added scripts by running them. If there are many similar scripts, test a representative sample and state the coverage.

## Assets

Use `assets/` for files consumed by output, not for instructions to read into context:

- templates;
- starter projects;
- fonts;
- icons;
- images;
- boilerplate files.

For a Loki command bundle, `assets/response-template.md` is the required
materialization of the Response contract. Keep response instructions in
`references/response.md`; keep the reusable output skeleton in the asset.

## Loki Command Bundle Disclosure

Keep `SKILL.md` short and restricted to metadata, Input and explicit loading
instructions. Put the full Execution contract in
`references/execution.md` (split only when every split is explicitly routed)
and the Response contract in `references/response.md`. A clean-context LLM
must be told to read each required reference completely before acting.

## What Not To Include

Do not add auxiliary documentation that is not required for execution:

- README;
- installation guide;
- quick reference;
- changelog;
- process notes.
