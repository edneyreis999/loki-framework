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

## XML Shape For LLM

```xml
<command_response>
  <summary></summary><status></status><artifacts></artifacts><evidence></evidence><handoff></handoff>
  <unified_implementation_handoff><inputs></inputs><identity></identity><state></state><validators></validators><evidence></evidence><dashboard></dashboard><next_action></next_action></unified_implementation_handoff>
  <risks></risks><next_steps></next_steps>
</command_response>
```
