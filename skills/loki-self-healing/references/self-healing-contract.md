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

Before individual file analysis, read enough available package context to
understand the whole. Prefer these sources when running inside the package
source, but do not require package docs when the skill is installed in a
consumer project:

- `manifest.yaml`, when available;
- package docs such as `docs/operational-inventory.md`,
  `docs/package-authoring-guardrails.md`, and `docs/model-effort-guidance.md`,
  when available;
- command contracts in `commands/`;
- wrapper skills and references in `skills/`;
- `skills/loki-command-workflows/SKILL.md` for invocable commands;
- `scripts/install-loki-symlinks.py` when skills, commands, agents, templates,
  or Codex installation surfaces are affected.

If package docs are unavailable, use visible package artifacts, bundled skill
references, command references, manifest data, and provided context; declare the
limitation instead of blocking clear low-risk corrections.

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

## Internal Instruction Quality Checklist

Apply this checklist after the global context pass and before finding
classification. Treat a failed check as a candidate finding, not automatic
permission to edit. Use `nao alterar` when the package already covers the
behavior clearly, and use `investigar` or `bloqueado` when the right correction
depends on a broader workflow decision.

This checklist is only for internal Loki artifacts. Do not use self-healing to
learn directly from external artifacts; when external material is relevant, rely
on the output of `loki:knowledge-extraction-analysis` or
`loki-framework-impact-audit` and then classify whether the internal package
should adopt, adapt, reject, or recognize the behavior as already covered.

Check each applicable artifact for:

- Instruction clarity: purpose, trigger, action, and stop condition are direct;
  success or failure can be judged with binary criteria; ambiguous words are
  narrowed; modal terms are precise: `deve` for required behavior, `nao deve`
  for prohibitions, `prefira` for defaults, `evite` for risk reduction, and
  `somente se` for preconditions.
- Prompt economy: repeated wording is removed or consolidated; long guidance is
  replaced by a shorter verifiable rule when possible; examples remain only
  when they prevent likely misuse.
- Loki essence preservation: corrections preserve package boundaries,
  source-of-truth rules, human gates, serial writes, validation discipline, and
  conservative autonomy; reject imported behavior that creates excessive
  autonomy, excessive rigidity, consumer-specific policy, or package drift.
- Knowledge transfer: specific observations are converted into reusable
  principles only when they generalize; general principles are adapted to the
  smallest correct surface: command, skill, agent, template, doc, validator, or
  backlog item; do not copy external instructions verbatim into Loki.
- Taxonomy and organization: the artifact exposes the sections its type needs,
  such as objective, triggers, inputs, outputs, preconditions, limits, process,
  validators, human gates, expected output, failure modes, completion criteria,
  resume contract, and when not to use.
- Redundancy and noise: useful instructions already covered elsewhere are
  referenced, consolidated, or left unchanged; duplicates that add conflict,
  cognitive cost, or token cost are removed.
- Output actionability: reports and diagnostics identify source, observation,
  reason, proposed adaptation or fix, risk, priority, and validation or test;
  observation stays separate from recommendation.
- Conflict detection: explicit and subtle conflicts across artifacts are
  surfaced, including tensions between autonomy, validation, safety, scope,
  precision, adapter behavior, and package philosophy.
- Command quality: command contracts control ambiguity, scope, allowed writes,
  forbidden writes, validation before changes, handoffs, human gates, stop
  conditions, output shape, and resume behavior; overly broad behavior is
  narrowed.
- Skill quality: skills define trigger context, preconditions when needed,
  limits, common failure modes when useful, completion criteria, and when not to
  use; detailed conditional guidance lives in `references/`, not in a bloated
  `SKILL.md`.
- Internal documentation quality: docs explain purpose, use, limits, and
  artifact relationships without turning consumer context into package policy;
  examples reduce ambiguity instead of increasing surface area.
- Uncertainty handling: assumptions are explicit; recommendations are
  conservative; unknown facts are not invented; questions are asked only when
  local evidence cannot resolve a material risk.

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
- Update related metadata when required and available: `manifest.yaml`,
  package inventory docs, `skills/loki-command-workflows/SKILL.md`,
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
