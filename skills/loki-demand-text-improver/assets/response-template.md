# Demand improvement result

## Status

`{{completed | blocked | partial}}`

## Summary

{{what happened and whether a demand artifact is ready}}

## Artifact

- Target: `{{calculated target | not created}}`
- Input mode: `{{inline | file}}`
- Naming rule: `{{improved-demand.md | <stem>-improved.md}}`

## Preflight and evidence

- Planning evidence: `{{confirmed | unconfirmed | unsupported}}`
- Sources read: {{sources or none}}
- Validators: {{validator results}}
- Semantic coverage: {{pass | blocked | not-run}}
- Provenance: {{pass | blocked | not-run}}

## Handoffs and ownership

- Read handoffs: {{terminal completion records or none}}
- Write owner: {{scoped writer | orchestrator direct-write exception | none}}
- Write completion: {{completion record or not-run}}

## Gates and open context

- Gates: {{resolved and pending gates}}
- Reversible assumptions: {{items or none}}
- Validate later: {{items with owner/moment or none}}

{{#if must_ask_now}}
## One material question

{{exactly one question; do not add another question anywhere in this response}}
{{/if}}

## Risks

{{risks, collision, unresolved conflict, or none}}

## Resume state

```yaml
loki_demand_improvement_state:
  status: "{{completed | blocked | partial}}"
  input_mode: "{{inline | file}}"
  sources_read: []
  planning_evidence: "{{confirmed | unconfirmed | unsupported}}"
  target: "{{path | not-created}}"
  classified_gaps: []
  answered_decisions: []
  blockers: []
  minimum_next_input: "{{none | one material answer | adapter planning state | safe destination action}}"
```

## Next step

{{minimum action to resume, or a separately chosen optional downstream workflow}}

No downstream analysis, planning, execution, or implementation was invoked.
