# Repository Guidelines

## Project Structure & Module Organization

This repository is a self-contained Loki Framework package, not an application runtime. `manifest.yaml` is the operational inventory for artifact paths, status, install targets, and guardrails. `commands/` contains invokable Loki workflows, `skills/` contains installable skill folders with `SKILL.md`, `agents/` contains specialist role definitions, `templates/` contains reusable contract templates, and `docs/` contains package policy, workflows, and usage guidance. `README.md` documents local installation and staging expectations.

## Build, Test, and Development Commands

There is no root package manager, build script, or automated test suite. Use shell checks for package integrity:

- `find . -maxdepth 4 -type f | sort` lists the package contents for review.
- `find skills -maxdepth 2 -name SKILL.md | sort` verifies skill entrypoints.
- `find skills -maxdepth 1 -type f -name '*.md'` should return nothing; skills must live in folders.
- Use the forbidden-reference scan documented in `docs/package-authoring-guardrails.md` before completing package policy or artifact changes.

## Coding Style & Naming Conventions

Write Markdown with concise YAML frontmatter where existing artifacts use it. Commands use the `loki:` namespace and should declare purpose, inputs, outputs, write boundaries, validators, human gates, stop conditions, and resume contract. Skills live at `skills/<skill-name>/SKILL.md`; Loki package skills use the `loki-` prefix and require frontmatter `name` and trigger-focused `description`. Put long examples or conditional guidance in `references/`, not in the main `SKILL.md`. Keep agents narrow and read-only or proposal-only unless a package decision changes that model.

## Testing Guidelines

For documentation-only changes, review rendered Markdown structure and run the integrity commands above. When adding, renaming, or removing commands, skills, agents, templates, or docs, update `manifest.yaml` in the same change. For package policy changes, also check `docs/package-authoring-guardrails.md` for required validation and approval gates.

## Commit & Pull Request Guidelines

The Git history currently only shows `first commit`, so no detailed convention is established. Use concise imperative commit subjects with an artifact scope when helpful, such as `Add loki skill validation notes`. Pull requests should include a summary, affected paths, validation commands run, linked issue or plan when available, and any required human approval or runtime-validation gate.

## Security & Configuration Tips

Do not copy artifacts into `.claude/**`, `.codex/**`, or `.agents/**` without explicit approval. Do not treat consumer project docs, runtime files, or generated staging folders as normative package sources.
