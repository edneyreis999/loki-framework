# loki-retrospectiva-tecnica — Resultado

## Status
<completed | partial | blocked | stopped>

## Resumo
<objetivo, resultado e criterio de conclusao ou pausa>

## Artefatos
<criados, alterados, consultados ou descartados>

## Evidencias e validadores
<validacoes feitas, pendentes, bloqueadas e resultados>

## Decisoes humanas
<decisoes, correcoes e mudancas de escopo; use none>

## Rastro operacional material
<ferramentas, comandos, scripts, buscas e resultados relevantes>

## Atritos de execucao
<registros pela taxonomia e formato contratados; use none>

## Caminho minimo recomendado
<sequencia futura com menos tentativas>

## Aprendizados e candidatos
<validado, hipotese, falha operacional, preferencia humana e handoff sem promocao>

### Candidatos especializados de inferencia

```yaml
analytic_inference_candidates:
  - schema_version: 1
    candidate_id: "<stable candidate ID>"
    candidate_type: analytic-inference
    observation_type: "<inference-good | inference-bad | inference-missing>"
    status: unreviewed
    capture_id: "<observed stable capture ID>"
    source:
      retrospective_locator: "<exact persisted retrospective locator>"
      consumer_root:
        canonical: "<observed canonical consumer root | unavailable>"
        resolution_source: "<canonical-pwd | unavailable>"
        state_root: "<derived fixed state root | unavailable>"
    lineage:
      run_id: "<observed | unavailable>"
      phase: "<observed | unavailable>"
      task_id: "<observed | unavailable>"
      agent_run_id: "<observed | unavailable>"
      handoff_id: "<observed | unavailable>"
      evidence_id: "<observed | unavailable>"
    statement_or_testable_question: "<statement or question>"
    observation:
      expected: "<expected | not-applicable>"
      actual: "<actual | not-applicable>"
      missing_opportunity: "<opportunity | not-applicable>"
    applicability:
      technologies: []
      versions: []
      surfaces: []
      objectives: []
      signals: []
      exclusions: []
    provenance:
      source_refs: []
      evidence_refs: []
      freshness: "<current | stale | unknown>"
    evidence_classification:
      facts: []
      inferences: []
      hypotheses: []
    validation:
      state: "<validated | partial | unvalidated | conflicting | unsupported>"
      validator_refs: []
      reason: "<non-empty reason>"
    investigation:
      confirm_or_reject_evidence: []
      potential_impact: "<impact>"
      cost: "<low | medium | high | unknown | unsupported>"
      stop_condition: "<observable condition>"
      suggested_capabilities: []
    distinction:
      exact_duplicate_hints: []
      near_duplicate_hints: []
      distinction_reason: "<observable difference or lookup gap>"
    guidance:
      reuse: "<guidance | none>"
      avoid: "<guidance | none>"
    downstream:
      owner: loki-continuous-improvement
      eligible_for_ci_evaluation: true
      durable_mutation_authorized: false
```

Quando vazio:

```yaml
analytic_inference_candidates: []
analytic_inference_candidates_empty_reason: "<no material observation | missing capture_id/locator | other evidence-based reason>"
```

- Validacao dos candidatos: <check + resultado | none>
- Lineage indisponivel: <campo + motivo | none>
- Consumer/state root provenance: <canonical roots + resolution source | unavailable + reason>
- Gates para avaliacao downstream: <gate/status/source | none>
- Catalogo escrito/promovido/pontuado/reorganizado/purgado: false
- Route permitido: loki-continuous-improvement para avaliacao; nenhuma promocao automatica

## Handoffs, gates e approvals
<concluidos e pendentes>

## Riscos ou blockers
<riscos residuais e evidencias contraditorias>

## Proximos passos
<acao e owner esperado>

## Resume state
<estado suficiente para continuar sem memoria da conversa>
