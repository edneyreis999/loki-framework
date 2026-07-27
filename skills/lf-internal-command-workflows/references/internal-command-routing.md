# Internal Loki command routing

## Catalog

| Identity | Primary bundle |
| --- | --- |
| `loki-knowledge-extraction-analysis` | `skills/loki-knowledge-extraction-analysis/SKILL.md` |
| `loki-self-healing` | `skills/loki-self-healing/SKILL.md` |

## Procedure

1. Confirm the active installation exposes the requested bundle.
2. Before mutating a consolidated package artifact, resolve the package root
   from the approved task envelope and require `destination_scope: package`;
   installation alone grants no authority. A transient analysis report remains
   bound to the exact target and prohibitions of its primary bundle.
3. Match the exact `loki-*` identity; never translate a legacy namespace.
4. Read the primary bundle and every routed reference/asset.
5. Resolve `required_skills` and `required_commands` independently.
6. Stop if the workflow is general-purpose, absent or outside the approved
   package-maintenance scope.
