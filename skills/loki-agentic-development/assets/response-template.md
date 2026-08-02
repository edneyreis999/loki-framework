# loki-agentic-development — Resultado

## Status
<completed | blocked>
## Resumo
<resultado integrado>
## Artefatos
<manifest, análise, plano, builds, reports, retrospectivas, digest e backlog>
## Evidências e validators
<comandos, resultados e gates>
## Handoffs, gates e approvals
<estado terminal ou pendência>
## Unified implementation handoff
<demand/analysis locators e digests; implementation_handoff_id unico; plan_directory; loki_run_state locator/digest; validators, completion/evidence, dashboard, status, reason e minimum_next_path. O parent nao cria plano/DAG/ciclo/retry/dashboard paralelo>
## Manual-QA handoff
```yaml
manual_qa_handoff:
  schema_version: 2
  status: "<manual-qa-not-evaluated | ready-for-manual-qa | manual-qa-not-required>"
  run_id: "<loki-run-v2 identity>"
  execution_id: "<loki-execution-v2 identity>"
  plan_directory: "<normalized plan directory>"
  automatic_evidence_refs: ["<exact ordered automatic evidence refs>"]
  manual_qa_result_ref: "<plan_directory>/builds/manual-qa/result.json"
  manual_qa_attestation_ref: "<plan_directory>/interaction/manual-qa/<run_id>/attestation.json"
  task_refs: ["<exact state task order>"]
  acceptance_criterion_refs: ["<exact task order then acceptance-criterion order>"]
  gate_refs: ["<exact state gate order>"]
  changed_target_refs: ["<first-occurrence changed target paths from completed Writer handoffs>"]
  reason: "<null only when ready-for-manual-qa; non-empty otherwise>"
```
<ready-for-manual-qa encaminha esta projeção imutável a loki-manual-qa; manual-qa-not-required não invoca QA manual; manual-qa-not-evaluated mantém o parent blocked. Não adicionar handoff digests nem derivar steps, declaração, atestação ou resultado manual>
<matriz fechada: implementation scheduled|dispatched|running|partial|failed|cancelled => parent blocked + manual-qa-not-evaluated; awaiting-manual-qa => parent completed + ready-for-manual-qa; completed|completed-with-limitations => parent completed + manual-qa-not-required; projeções iguais fora da matriz falham>
## Completion, evidence e execution knowledge
<completion/evidence da implementacao e captures de execution knowledge com IDs/estados proprios; nao reutilizar como materialidade ou resultado do review>
## Riscos ou blockers
<separar blockers reais de input/state/integridade/validator/gate de riscos do pipeline agentic; none quando vazio>
## Próximos passos
<ação e owner>
## Resume state
<fase/task, estado, evidências e condição de retomada; demand/analysis digests, implementation_handoff_id unico, refs do state/dashboard devolvidos e igualdade das treze chaves do manual_qa_handoff v2 relidas do agentic-run-manifest.xml e agentic-run-digest.xml, incluindo ordem exata das quatro listas de escopo; memória de conversa não reconstitui drift; dispatched reconcilia identidade existente, terminal nao reinvoca, degraded inclui reason/minimum_next_path>
