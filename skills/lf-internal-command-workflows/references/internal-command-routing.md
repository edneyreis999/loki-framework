# Internal Loki command routing

## Catalog

| Identity | Primary bundle |
| --- | --- |
| `loki-knowledge-extraction-analysis` | `skills/loki-knowledge-extraction-analysis/SKILL.md` |
| `loki-self-healing` | `skills/loki-self-healing/SKILL.md` |

## Procedure

1. Confirm execution is inside the Loki package and the package-source/all
   profile exposes the bundle.
2. Match the exact `loki-*` identity; never translate a legacy namespace.
3. Read the primary bundle and every routed reference/asset.
4. Resolve `required_skills` and `required_commands` independently.
5. Stop if the workflow is public-only, absent or outside the approved scope.
