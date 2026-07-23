# loki-tech-analysis — Response Contract

## Response

### Consumidor e materialização

O consumidor principal é `Both`. Use
`../assets/response-template.md` para materializar a resposta terminal em
Markdown legível por humanos e recuperável por outra LLM, sem limite rígido de
tamanho. Preencha todos os campos com o estado real; use `none` somente quando
o campo for inaplicável e isso tiver sido verificado.

Se o caller exigir exclusivamente outro consumidor, selecione exatamente um:

- `LLM`: responda em XML válido, estável e parseável, sem prosa fora do elemento
  raiz, usando no mínimo:

```xml
<command_response>
  <summary></summary>
  <status></status>
  <artifacts></artifacts>
  <evidence></evidence>
  <handoff></handoff>
  <risks></risks>
  <next_steps></next_steps>
</command_response>
```

- `Humano`: responda em Markdown claro, conciso e acionável com no máximo 7.000
  caracteres, priorizando resultado, estado, decisões necessárias, riscos e
  próximos passos.
- `Both`: responda em Markdown, sem limite rígido, usando o template e estrutura
  suficiente para retomada por uma LLM.

Se o consumidor não estiver definido e a escolha mudar o formato, resolva-o
antes da resposta terminal.

### Resposta intermediária

Durante `Input`, entrevista, gate ou parada recuperável, responda somente com a
pergunta, decisão ou controle necessário, o motivo, o estado preservado e a
condição exata para continuar. Não use a resposta intermediária para declarar
conclusão, omitir um gate ou simular a resposta terminal.

### Conteúdo obrigatório

Toda resposta terminal ou de parada deve comunicar:

- resumo do resultado;
- status final ou atual;
- artefatos criados, alterados ou analisados;
- evidências, fontes e resultados de validators;
- handoffs concluídos e pendentes;
- gates e approvals concluídos e pendentes;
- falhas, lacunas, blockers e riscos residuais;
- próximo passo, comando recomendado e owner esperado;
- resume state suficiente para outra LLM continuar sem memória da conversa.

Para análise concluída, identifique o `destination`, o resultado do research
gate, a decisão `human_decision_preflight.required` e a recomendação entre
`loki-human-decision-preflight`, `loki-implement-feature`, investigação
adicional ou bloqueio.

Não declare `completed`, `ready` ou equivalente enquanto houver validator
falho, gate ou approval pendente, handoff aberto, pergunta humana bloqueante ou
condição de parada ativa. Nesse caso, use status `blocked`, `paused` ou
`awaiting-input` e registre a condição de retomada.
