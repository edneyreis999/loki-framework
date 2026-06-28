# Loki Framework Impact Audit Contract

Use this reference after external knowledge has been extracted and before final
recommendations are consolidated.

## Inventory Requirement

Use the available Loki inventory as the primary source for existing Loki
artifacts, their function, relationships, and likely impact surfaces. Prefer
`docs/operational-inventory.md` when running inside the package source and it is
available. If the skill is installed in a consumer project without package docs,
use visible commands, skills, templates, manifest data or provided context.

If the inventory is unavailable, incomplete, or insufficient, declare that
limitation explicitly. Do not invent Loki files, workflows, or relationships.

## Select Potentially Affected Artifacts

For every potentially affected artifact, identify:

- name or path;
- artifact type;
- function inside Loki;
- why it may be impacted by the external learning;
- impacted aspect: objective, triggers, constraints, operational flow, output
  format, validation criteria, uncertainty handling, autonomy limits,
  documentation, noise prevention, consistency with other artifacts, or another
  relevant aspect;
- potential impact: `alto`, `medio`, `baixo`, `incerto`, or `nenhum impacto
  relevante`.

Audit individually only artifacts with `alto`, `medio`, or `incerto` impact.
Low-impact artifacts may be mentioned generally. Exclude artifacts with no
relevant impact and justify briefly.

## Workflow Impact Analysis

For each affected workflow, identify:

- workflow name or description;
- Loki artifacts involved;
- current expected behavior if visible;
- behavior suggested or influenced by the external artifact;
- practical difference between current and external behavior;
- alteration risks;
- expected gain;
- whether the influence should be adopted, adapted, rejected, or investigated.

Pay special attention to autonomy, validation before changes, scope control,
completion criteria, output format, command interpretation, skill consistency,
undesired behavior prevention, noise, and cognitive cost.

## Individual Artifact Audit

For each selected artifact, compare the extracted external learning with the
Loki artifact and answer:

- what the external artifact directly or indirectly suggests;
- which Loki section, rule, behavior, or decision is impacted;
- whether Loki already covers the instruction or principle;
- whether there is a real gap;
- whether there is redundancy;
- whether there is conflict;
- whether simplification is possible;
- whether the instruction can be made more verifiable;
- whether there is risk of importing incompatible behavior;
- which concrete change is recommended, if any.

Do not merge conclusions across artifacts unless each source is traceable.

## Required Report Shape

For each audited artifact, produce:

```markdown
### Relatorio de impacto: `[arquivo ou artefato do Loki]`

**Artefato do Loki analisado:**

**Tipo:**
Skill | comando | workflow | documentacao | template | regra global | outro

**Funcao no Loki:**

**Artefatos externos comparados:**

**Motivo da auditoria:**

**Impacto potencial:**
alto | medio | baixo | incerto

**Partes impactadas:**

**Observacoes extraidas dos artefatos externos:**

**Interpretacoes relevantes para o Loki:**

**Delta identificado:**

**Lacunas encontradas:**

**Redundancias encontradas:**

**Conflitos encontrados:**

**Oportunidades de melhoria:**

**Recomendacao para este artefato:**
adotar | adaptar | rejeitar | ja contemplado | investigar | nao alterar

**Mudanca sugerida:**

**Texto sugerido:**

**Risco da mudanca:**

**Prioridade:**
obrigatoria | recomendada | experimental | baixa | rejeitada

**Teste de validacao:**
```

## Required Handoff Shape

Return:

```yaml
impact_audit:
  inventory_status: "read | unavailable | incomplete | insufficient"
  loki_artifacts_considered:
    - path: ""
      type: ""
      included_in_audit: true
      impact_level: "alto | medio | baixo | incerto | nenhum impacto relevante"
      reason: ""
  workflow_impacts:
    - workflow: ""
      loki_artifacts: []
      current_behavior: ""
      external_influence: ""
      practical_delta: ""
      risks: ""
      expected_gain: ""
      recommendation: "adotar | adaptar | rejeitar | investigar | nao alterar"
  individual_reports: []
  consolidated_findings:
    gaps: []
    redundancies: []
    conflicts: []
    opportunities: []
    no_change_reasons: []
```
