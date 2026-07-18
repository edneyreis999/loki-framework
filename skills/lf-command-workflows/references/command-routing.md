# Public Loki command routing

## Catalog

| Identity | Primary bundle |
| --- | --- |
| `loki-init` | `skills/loki-init/SKILL.md` |
| `loki-catalogar-docs` | `skills/loki-catalogar-docs/SKILL.md` |
| `loki-criar-branch` | `skills/loki-criar-branch/SKILL.md` |
| `loki-commit` | `skills/loki-commit/SKILL.md` |
| `loki-abrir-pr` | `skills/loki-abrir-pr/SKILL.md` |
| `loki-continuous-improvement` | `skills/loki-continuous-improvement/SKILL.md` |
| `loki-enrich-tasks` | `skills/loki-enrich-tasks/SKILL.md` |
| `loki-feedback` | `skills/loki-feedback/SKILL.md` |
| `loki-generate-action-plan` | `skills/loki-generate-action-plan/SKILL.md` |
| `loki-human-decision-preflight` | `skills/loki-human-decision-preflight/SKILL.md` |
| `loki-agentic-development` | `skills/loki-agentic-development/SKILL.md` |
| `loki-deep-research` | `skills/loki-deep-research/SKILL.md` |
| `loki-retrospectiva-tecnica` | `skills/loki-retrospectiva-tecnica/SKILL.md` |
| `loki-run-plan` | `skills/loki-run-plan/SKILL.md` |
| `loki-demand-text-improver` | `skills/loki-demand-text-improver/SKILL.md` |
| `loki-tech-analysis` | `skills/loki-tech-analysis/SKILL.md` |

## Procedure

1. Match the exact identity; do not translate a legacy namespace.
2. Read the primary bundle entrypoint and every reference/asset it routes.
3. Validate inputs, then execute the bundle's Input → Execution → Response.
4. Resolve dependencies by their canonical `loki-*` or `lf-*` identity.
5. Stop when the identity is absent from this catalog or unavailable in the
   active installation profile.
