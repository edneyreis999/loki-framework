# Response — loki-agentic-development

## Response

Use este contrato para respostas intermediárias e terminais.

## Consumer And Formats

Consumidor principal: `Both`. Para `LLM`, XML válido com `summary`, `status`,
`artifacts`, `evidence`, `handoff`, `risks`, `next_steps`. Para `Humano`,
Markdown acionável com até 7.000 caracteres. Para `Both`, Markdown legível por
pessoa e recuperável por LLM, sem limite rígido.

## Intermediate Response

Em decision gate, approval ou stop, informe status, decisão
exata, evidência, estado dos handoffs, risco, próxima ação e resume state. Não
declare conclusão nem componha resposta terminal.

Para o handoff unificado, preserve respostas intermediárias distintas para
input/digest conflict, dispatch em reconciliação e falha de state integrity.
Exponha o mesmo `implementation_handoff_id`; não crie uma segunda chamada.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, artefatos,
evidências/validators, handoffs, gates/approvals, riscos, próximos passos e
resume state. Não conclua com validator, gate, handoff ou stop condition aberto.

Inclua uma seção `unified_implementation_handoff` com demand/analysis locators e
digests, `implementation_handoff_id`, plan directory, returned state/digest,
validators, evidence, dashboard e terminal status. Para todo estado degradado,
exponha reason e `minimum_next_path`. Completion/evidence e execution knowledge
permanecem conceitos separados.

Inclua também o `manual_qa_handoff` v2 fechado com exatamente as treze chaves
`schema_version`, `status`, `run_id`, `execution_id`, `plan_directory`,
`automatic_evidence_refs`, `manual_qa_result_ref`,
`manual_qa_attestation_ref`, `task_refs`, `acceptance_criterion_refs`,
`gate_refs`, `changed_target_refs` e `reason`; não adicione digests nem altere
a ordem das listas. Para
`ready-for-manual-qa`, preserve `reason: null` e indique `loki-manual-qa` como
próximo comando com o mesmo plan directory, identidades, evidências e locators.
Para `manual-qa-not-required`, exponha a razão não vazia e não invoque QA
manual. Para `manual-qa-not-evaluated`, exponha a razão não vazia e mantenha o
parent `blocked`. O status do parent permanece fechado em `completed` ou
`blocked`; não derive steps, declaração, atestação ou resultado manual neste
workflow.

A resposta deve obedecer à matriz fechada: implementation handoff `scheduled`,
`dispatched`, `running`, `partial`, `failed` ou `cancelled` corresponde somente
a `manual-qa-not-evaluated` com parent `blocked`; `awaiting-manual-qa`
corresponde somente a `ready-for-manual-qa` com parent `completed`; `completed`
ou `completed-with-limitations` corresponde somente a
`manual-qa-not-required` com parent `completed`. Igualdade das projeções não
torna válida uma combinação fora dessa matriz.

Renderize esse mapping somente quando as projeções atuais em
`agentic-run-manifest.xml` e `agentic-run-digest.xml`, relidas do disco, forem
iguais nas treze chaves. Chave extra, digest, identidade/anchor divergente,
status/razão incompatível ou ausência em uma projeção bloqueia a resposta; não
reconstrua a partir da conversa.

## XML Shape For LLM

```xml
<command_response>
  <summary></summary><status></status><artifacts></artifacts><evidence></evidence><handoff></handoff>
  <unified_implementation_handoff><inputs></inputs><identity></identity><state></state><validators></validators><evidence></evidence><dashboard></dashboard><next_action></next_action></unified_implementation_handoff>
  <manual_qa_handoff><schema_version></schema_version><status></status><run_id></run_id><execution_id></execution_id><plan_directory></plan_directory><automatic_evidence_refs></automatic_evidence_refs><manual_qa_result_ref></manual_qa_result_ref><manual_qa_attestation_ref></manual_qa_attestation_ref><task_refs></task_refs><acceptance_criterion_refs></acceptance_criterion_refs><gate_refs></gate_refs><changed_target_refs></changed_target_refs><reason></reason></manual_qa_handoff>
  <risks></risks><next_steps></next_steps>
</command_response>
```
