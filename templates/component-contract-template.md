---
name: "<component-name>"
type: "<agent | skill | dependency | template>"
status: draft
---

# <component-name>

## Purpose

<Responsabilidade do componente.>

## When To Use

<Gatilhos para usar o componente.>

## Inputs

- <Entrada exigida>

## Outputs

- <Saida esperada>

## Operational Contract

- Operational role: <domain investigator | domain task writer | package writer | consumer-doc cataloger | other>
- Consumer installation and category: <installed_in_consumer true|false; Write Agent | other>
- Capabilities and active mode: <read-only | proposal-only | scoped-writer | write-test>
- Init role: <init_inventory_domain_investigator read-only/proposal-only | init_support_only | init_serial_cataloger | not-applicable>
- Init investigator output: <structured research packet refs, continuation cursor and compact completion record to the orchestrator; never consumer-doc writes>
- Calling workflow and write class: <caller identity; none | task-artifact | consumer-docs | package-documentation>
- Resolved roots: <consumer project root; package root; declared durable_context_root or not-applicable>
- Durable context/preflight: <required iff installed_in_consumer AND category == Write Agent AND task_write_mode includes task_scoped_writer AND durable_context_root is declared AND agent is a domain agent; active_mode may be scoped-writer and is not the task-mode key; include status, selected refs, current-source precedence and gap handoff>
- Success destination: <owner>
- Failure destination: <owner>
- Stop conditions: <missing scope, permission, validator, gate or handoff>
- Completion evidence: <observable validator or human gate>

## Allowed Writes

- <Se nao puder escrever, declarar `none` ou `proposal-only`; para task_scoped_writer, listar exact targets recebidos do caller.>

## Forbidden Writes

- <Superficies proibidas, incluindo consumer docs por non-catalogador, init fallback e package docs por papel nao-interno.>

## Gates

- <Gates obrigatorios.>

## Dependencies

- <Skills, commands, agents, docs ou templates relacionados.>

## Packaging Checks

- <Se o componente fizer parte do pacote, declarar path final, impacto no manifest, docs afetados e validacoes objetivas.>

## Response Format

```yaml
component_response:
  summary: ""
  operational_role: ""
  installed_in_consumer: false
  category: ""
  calling_workflow: ""
  write_class: "none | task-artifact | consumer-docs | package-documentation"
  resolved_root: ""
  durable_context_root: ""
  active_mode: "read-only | proposal-only | scoped-writer | write-test"
  task_write_mode: "task_scoped_writer | not-applicable"
  init_investigation:
    role: "init_inventory_domain_investigator | not-applicable"
    research_packet_refs: []
    continuation_status: "continue | complete | blocked | not-applicable"
    continuation_cursor: ""
  domain_context_preflight:
    required: false
    status: "ready | ready-with-gaps | blocked | not-applicable"
    durable_context_refs: []
    current_source_refs: []
    gap_handoff: ""
  exact_task_writes: []
  evidence: []
  completion_record: {}
  execution_evidence: "orchestrator-owned; separate from completion_record"
  risks: []
  recommended_next_step: ""
```
