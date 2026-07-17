# Response — loki-run-plan

## Response

Use este contrato para respostas intermediárias e terminais.

## Consumer And Formats

Consumidor principal: `Both`.

- `LLM`: responda em XML válido, estável e parseável, sem prosa fora da raiz
  `command_response`, com `summary`, `status`, `artifacts`, `evidence`,
  `handoff`, `risks` e `next_steps`.
- `Humano`: responda em Markdown claro, conciso e acionável, com no máximo
  7.000 caracteres. Priorize resultado, estado, decisões necessárias, riscos e
  próximos passos.
- `Both`: responda em Markdown legível por pessoa e recuperável por outra LLM,
  sem limite rígido. Use estrutura somente quando melhorar leitura e retomada.

Se outro consumidor for explicitamente escolhido, aplique seu formato. Se o
consumidor estiver indefinido e a escolha alterar o formato, resolva-o antes de
responder.

## Intermediate Response

Quando houver pergunta, gate ou stop condition real, responda com status atual,
decisão exata necessária, evidências disponíveis, handoffs, riscos, próxima
ação e `LokiRunState` mínimo. Não preencha o resultado terminal nem declare
conclusão.

## Terminal Response

Para o consumidor padrão `Both`, preencha integralmente
`../assets/response-template.md`. Para qualquer consumidor, comunique resumo,
status final ou atual, fase/tasks, artefatos criados/alterados/analisados,
evidências e validators, handoffs concluídos ou pendentes, gates e approvals,
falhas/lacunas/riscos, próximos passos com owner e `LokiRunState`. Para cada
Write Agent selecionado pela formula canonica, exponha um resumo do
`domain_context_preflight` com agent/task, durable root, README/docs read,
freshness `current|stale|absent|unavailable|uncertain`, current sources,
conflicts, gaps/materiality/substitutes, source precedence, cross-domain e
durable-gap handoffs, result `ready|ready-with-gaps|blocked`, reason e minimum
`minimum_next_input`. O mesmo registro deve existir no task state e
`LokiRunState`.

Declare explicitamente que docs/brief fornecidos pelo orquestrador nao
substituiram o preflight pessoal. Se target for consumer docs, reporte
`catalogador`, `calling_workflow: loki-run-plan`, `write_mode:
task_scoped_writer`, disponibilidade e destinations; indisponibilidade e
`blocked` pre-write sem fallback.

Não use resposta terminal após checkpoint de task enquanto outra task do escopo
selecionado estiver pronta na DAG. Não declare conclusão com validator falho, gate/approval material pendente,
handoff aberto ou stop condition ativa. Ao fim de uma fase concluída, inclua a
retrospectiva iniciada ou recomendada.

## Material Human Input Disclaimer

Emita disclaimer final destacado somente quando restar input humano material
real, como `pending-technical-review`, `pending-human-validation`,
`pending-approval`, `interview` ou bloqueio equivalente. Não emita disclaimer
quando a task seguiu o plano aprovado e nenhuma decisão humana material resta.
O disclaimer deve ser a última seção, usar o status exato e listar ações
concretas:

```markdown
--------------
pending-technical-review
------------

- Aprovar ou ajustar ...
- Confirmar ...
```

## XML Shape For LLM

```xml
<command_response>
  <summary></summary>
  <status></status>
  <artifacts></artifacts>
  <evidence></evidence>
  <handoff></handoff>
  <domain_context_preflight></domain_context_preflight>
  <consumer_docs_ownership></consumer_docs_ownership>
  <risks></risks>
  <next_steps></next_steps>
</command_response>
```
