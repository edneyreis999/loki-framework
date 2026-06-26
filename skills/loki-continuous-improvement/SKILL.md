---
name: loki-continuous-improvement
description: Run the Loki `loki:continuous-improvement` command workflow in Codex. Use when promoting validated learnings into durable project context, technical skills, Loki package artifacts, standards, commands, agents, templates, validators, docs, manifest updates, or backlog; classify whether evidence belongs in consumer `/docs`, a reusable skill, another durable artifact, or should be discarded/recorded only.
when_to_use:
  - "Use when promoting validated learnings into durable project context or Loki package artifacts."
  - "Use when classifying candidates for standards, commands, skills, agents, templates, validators, docs, manifest updates, or backlog."
  - "Use when deciding whether a retrospective learning belongs in consumer docs, a technical skill, or record-only/backlog."
argument-hint: "[retrospective path, candidate learning, target surface]"
arguments:
  required: []
  optional:
    - retrospective_path
    - retrospective_dir
    - candidate_learning
    - target_surface
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: high
model_class: frontier_reasoning
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - durable package policy promotion
  - command, skill, agent, template, validator, or manifest changes
  - broad normative change with cross-adapter impact
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-continuous-improvement/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:continuous-improvement
---

# loki-continuous-improvement

## Procedure

1. Read the installed command contract:
   [loki-continuous-improvement.md](references/command.md).
2. Follow the command's inputs, outputs, allowed writes, forbidden writes,
   required skills, handoffs, validators, gates, stop conditions, and resume
   contract.
3. Load the relevant Loki skills named by the command contract, especially
   `loki-retrospectiva-tecnica`, `loki-command-creator`,
   `loki-agent-creator`, and `loki-skill-creator`.
4. If the input is a retrospective directory or multiple retrospective files,
   fan out read-only digestion with `retrospective-digester` by file when the
   runtime allows it. If fan-out is unavailable, process files serially using
   the same `retrospective_digest` schema.
5. Consolidate digests in the main context before classification. Do not load
   all raw retrospectives into the main context unless resolving conflict or
   weak evidence requires it.
6. Classify every candidate with the shortcut below before proposing a patch.
7. When reading retrospectives, preserve execution friction fields such as
   useful and bad inferences, scripts, unexpected outputs, environment
   mismatches, failed lookups, waste impact, and minimum next path.
8. Treat this skill as the Codex entrypoint for the command name
   `loki:continuous-improvement`.

## Classification Shortcut

- Put project-specific facts in consumer `docs/**/*.md` plus `docs/index.xml`:
  business rules, lore, product behavior, domain terms, feature flows,
  project conventions, architecture facts, source-of-truth paths, and decisions
  that should survive across plans for that consumer project.
- Put reusable technical procedures in `skills/`: repeatable workflows,
  technology handling, validators, preflights, debugging recipes, file format
  rules, tool usage, engine/framework operations, or execution heuristics that
  apply beyond one task.
- Put project-wide routing in `AGENTS.md` only when all LLMs in the consumer
  project need a short pointer to the durable source. Keep detailed rules in
  `/docs` or a skill.
- Put adapter-specific routing in `CLAUDE.md` or equivalent only when the rule
  applies to one execution surface.
- Put command orchestration in `commands/` when the learning requires an
  invokable workflow with inputs, outputs, gates, writes, handoffs, validators,
  stop conditions, and resume state.
- Put repeatable output shape in `templates/`.
- Put package policy, validators, or manifest inventory in the matching Loki
  package artifact only after `technical-review` and required approval.
- Use `record-only` or backlog when evidence is weak, isolated, still
  hypothetical, purely transient, already covered by an existing durable source,
  or would add noise without preventing a repeatable failure.

## Classification Checks

- Identify the source evidence, scope, target file or artifact type, validation,
  and required gate before writing.
- Prefer the surface that would have prevented the repeated error with the least
  durable text.
- Do not promote execution friction directly; convert it into a durable rule,
  skill procedure, validator, preflight, doc update, or backlog item only when it
  is reusable and evidenced.
- When using multiple retrospectives, deduplicate by source evidence,
  destination surface, repeated failure, and minimum next path before proposing
  any durable update.
- If the destination is consumer docs, update `docs/index.xml` in the same
  promotion and use `catalogador` when appropriate.
- If the destination is a skill, load `loki-skill-creator` and keep
  technology-specific rules out of core package skills unless they belong to a
  specialized skill.

## Limits

- Do not promote transient phase evidence into durable rules without the gates
  required by the command contract.
- Do not edit `.agents/**` or `.codex/**` unless the user explicitly asks for
  installation or synchronization.
- Do not put consumer business rules, lore, product behavior, or project facts
  into the Loki package.
- Do not discard validated learning without recording why it is already covered,
  too weak, too local, or not worth durable context.
