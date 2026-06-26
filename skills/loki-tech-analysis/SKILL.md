---
name: loki-tech-analysis
description: Run the Loki `loki:tech-analysis` command workflow in Codex. Use when producing evidence-based technical analyses from briefs, feedback, specs, source paths, runtime questions, source maps, decision matrices, validators, gates, and handoff to action planning.
type: skill
status: draft
used_by:
  - loki:tech-analysis
---

# loki-tech-analysis

## Procedure

1. Read the installed command contract:
   [loki-tech-analysis.md](references/command.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions, and resume
   contract.
3. Load `loki-tech-analysis-authoring` before creating or reviewing the
   analysis artifact.
4. Use `loki-template-library` when writing a technical analysis file.
5. Treat this skill as the Codex entrypoint for the command name
   `loki:tech-analysis`.

## Limits

- Do not write runtime, engine, framework, generated data, or sensitive
  consumer surfaces during analysis.
- Do not make recommendations without evidence or clearly labeled inference.
