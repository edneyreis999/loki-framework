# Loki Self-Healing Contract

Use this reference when auditing and correcting internal Loki package artifacts.

## Objective

Detect and correct internal inconsistencies, missing metadata, structural drift,
unclear instructions, duplicated noise, incomplete routing, weak validators, and
package integration gaps in Loki artifacts.

This skill does not learn from external artifacts. It adapts the analysis lenses
used by `loki:knowledge-extraction-analysis` to internal package conformance:
instruction clarity, prompt economy, Loki essence preservation, taxonomy,
output formats, rejection criteria, conflicts, traceability, separation between
observation and recommendation, compatibility, uncertainty handling,
prioritization, noise prevention, principles, validation tests, workflow delta,
and recurring patterns.

## Scope Resolution

Accept these input shapes:

- file path: audit that file and required package metadata related to it;
- directory path: enumerate package files under the directory and audit them;
- workflow name: map command, wrapper skill, helper skills, references,
  templates, docs, manifest, inventory, command router, and installer entries;
- staged files: run `git diff --cached --name-only --diff-filter=ACMR` to select
  files, then apply corrections to working-tree files only.

If no explicit scope is provided and there are no staged files, stop and ask for
scope.

## Global Context

Before individual file analysis, read enough package context to understand the
whole:

- `docs/operational-inventory.md`;
- `manifest.yaml`;
- `docs/package-authoring-guardrails.md`;
- `docs/model-effort-guidance.md` when model, effort, execution profile, or
  adapter projection appears in scope;
- command contracts in `commands/`;
- wrapper skills and references in `skills/`;
- `skills/loki-command-workflows/SKILL.md` for invocable commands;
- `scripts/install-loki-symlinks.py` when skills, commands, agents, templates,
  or Codex installation surfaces are affected.

## Audit Lenses

For each selected file, check:

- clear purpose, triggers, inputs, outputs, limits, validators, gates, and
  resume behavior where appropriate;
- consistency with command/skill/agent/template conventions;
- required frontmatter and provider-neutral model/effort metadata;
- references are internal to package root and loaded through progressive
  disclosure;
- command wrappers, manifest entries, inventory entries, command router entries,
  installer requirements, symlinks, and references are synchronized;
- no forbidden normative dependency on plans, blueprints, `.agents/**`,
  `.claude/**`, `.codex/**`, absolute user paths, or consumer runtime files;
- no over-broad autonomy, missing validation, missing stop condition, or hidden
  write permission;
- no duplicate instruction that adds noise without improving behavior;
- no instruction that makes staged files, commits, approvals, or installation
  ambiguous;
- output formats are actionable and testable;
- uncertainty is explicit and does not block clear low-risk correction.

## Finding Classification

Classify findings as:

- `corrigir agora`: clear, scoped, verifiable, and compatible with package
  rules;
- `nao alterar`: already compliant or change would add noise;
- `investigar`: promising but insufficient evidence or too broad for current
  scope;
- `fora de escopo`: outside requested scope and not required metadata
  consistency;
- `bloqueado`: requires human decision, external research, or forbidden write.

Apply only `corrigir agora`.

## Correction Rules

- Write serially after all independent analyses are consolidated.
- Prefer the smallest coherent patch.
- Preserve existing package style and ASCII unless the file already requires
  non-ASCII content.
- Update related metadata when required: `manifest.yaml`,
  `docs/operational-inventory.md`, `skills/loki-command-workflows/SKILL.md`,
  `scripts/install-loki-symlinks.py`, command references, and wrapper skill
  references.
- Never stage or commit.
- When input is staged files, leave corrections as unstaged working-tree changes
  for user review.
- If a correction would alter installation targets under `.claude/**`,
  `.codex/**`, or `.agents/**`, stop instead.

## Parallel Analysis Shape

When parallel read-only analysis is available, split by file or independent
artifact group. Each analysis returns:

```yaml
self_healing_file_audit:
  file: ""
  artifact_type: ""
  role_in_package: ""
  related_artifacts: []
  findings:
    - classification: "corrigir agora | nao alterar | investigar | fora de escopo | bloqueado"
      observation: ""
      rule_or_standard: ""
      impact: ""
      proposed_fix: ""
      validation: ""
```

If parallel analysis is unavailable, keep the same structure in separate
subsections.

## Final Report Shape

Return:

```markdown
# Loki Self-Healing Report

## Escopo

## Contexto global lido

## Arquivos analisados

## Correcoes aplicadas

## Itens nao alterados

## Itens para investigar

## Validadores executados

## Falhas ou riscos residuais

## Arquivos alterados

## Proximo passo humano
Revisar o diff e stagear manualmente os arquivos que devem entrar no proximo commit.
```
