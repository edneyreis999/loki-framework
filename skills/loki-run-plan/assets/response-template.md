# loki-run-plan — Resultado

## Status

<completed | partial | blocked | stopped | pending-human-validation | pending-approval | interview>

## Resumo

<resultado ou estado atual da execução>

## Fase, task e DAG

<FASE_ATUAL, TASK_TARGET quando houver, tasks concluídas/bloqueadas/puladas e dependências>

## Execution Brief

<objetivo, fontes, superfícies, riscos, validators, gates e próximo passo definidos antes da escrita>

## Artefatos

<arquivos criados, alterados ou analisados; use none quando não aplicável>

## Evidências e validators

<checks, comandos ou checklists, resultados, builds e justificativas de não aplicabilidade>

## Handoffs, gates e approvals

<origem, destino, estado e evidência dos handoffs; gates e approvals concluídos ou pendentes>

## Domain Context Preflight

<por task/agent aplicavel: durable_context_root; README/docs read; freshness current | stale | absent | unavailable | uncertain; current source locators; conflicts e current-source-prevails; gaps/materiality/substitutes; cross-domain lookup e durable-gap handoff; result ready | ready-with-gaps | blocked; result reason; minimum_next_input. Confirmar que docs/brief do orquestrador nao substituiu o preflight pessoal; use none quando a formula canonica nao se aplicar>

## Consumer docs ownership

<targets consumer docs; owner catalogador; calling_workflow loki-run-plan; write_mode task_scoped_writer; disponibilidade; success/failure destinations; blocker/resume condition. Declarar no-fallback; use none quando nao aplicavel>

## Write Test review consultivo

<policy: requested_frequency, effective_frequency, source, terminal_scope, selected reviewer/reason e policy_digest; checkpoints: checkpoint_id, boundary, coverage_digest/handoffs, status, review_agent_raw_status, execution_status_effect sempre none, evidence, findings, risk/backlog refs, reason e next_action. Para zero material, registrar skipped-no-material-write e zero invocacoes. Raw blocked/findings/degradacao nunca substituem o Status externo, validators, gates, approvals ou human gates>

## Retrospectiva técnica

<iniciada | recomendada | não aplicável, com destino ou próximo owner>

## Riscos ou blockers

<falhas, lacunas, stop conditions, riscos consultivos WTR e riscos residuais; diferenciar blockers reais de findings do reviewer; use none>

## Próximos passos

<ação e owner esperado>

## LokiRunState

<plano, fase, task, status, brief, DAG, fontes, handoffs, owners, writes, arquivos, validations, human loop, blockers e condição de retomada; incluir policy/checkpoints WTR, coverage, state errors, riscos e reconciliacao sem reinvocacao; por preflight incluir durable root/docs, freshness, current sources, conflicts, gaps/materiality/substitutes, precedence, handoffs, result e minimum next input; para consumer docs incluir catalogador caller/mode, disponibilidade e destinations>
