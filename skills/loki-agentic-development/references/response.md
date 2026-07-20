# Response — loki-agentic-development

## Response

Use este contrato para respostas intermediárias e terminais.

## Consumer And Formats

Consumidor principal: `Both`. Para `LLM`, XML válido com `summary`, `status`,
`artifacts`, `evidence`, `handoff`, `risks`, `next_steps`. Para `Humano`,
Markdown acionável com até 7.000 caracteres. Para `Both`, Markdown legível por
pessoa e recuperável por LLM, sem limite rígido.

## Intermediate Response

Em decision gate, approval, human validation ou stop, informe status, decisão
exata, evidência, estado dos handoffs, risco, próxima ação e resume state. Não
declare conclusão nem componha resposta terminal.

Para WTR, preserve respostas intermediárias distintas para requested-policy
conflict, checkpoint `dispatched` em reconciliação, `outcome-unknown` consultivo
e falha de integridade. Exponha o mesmo plan-executor handoff/checkpoint já
persistido; não derive policy nem crie uma segunda chamada.

## Terminal Response

Preencha `../assets/response-template.md` com status, resumo, artefatos,
evidências/validators, handoffs, gates/approvals, riscos, próximos passos e
resume state. Não conclua com validator, gate, handoff ou stop condition aberto.

Inclua uma seção `write_test_review` que reconcilie requested frequency e
provenance capturados com policy/effective frequency devolvidos por
`loki-run-plan`. Referencie manifest, plan-executor handoff, checkpoint,
coverage, review handoff/run, evidence, risk, digest e backlog pelos mesmos IDs.
Skips, raw `blocked`, findings, failure e unknown mantêm
`execution_status_effect: none` e nunca selecionam o status externo. Para todo
estado degradado, exponha reason e `minimum_next_path`. Completion/evidence,
execution knowledge e review permanecem conceitos separados.

## XML Shape For LLM

```xml
<command_response>
  <summary></summary><status></status><artifacts></artifacts><evidence></evidence><handoff></handoff>
  <write_test_review><request></request><reconciled_policy></reconciled_policy><checkpoints></checkpoints><lineage></lineage><risks></risks><backlog></backlog><next_action></next_action></write_test_review>
  <risks></risks><next_steps></next_steps>
</command_response>
```
