# loki-demand-text-improver — Response Contract

## Primary consumer

O consumidor é `Both`. Responda em Markdown recuperável, sem limite rígido,
usando o idioma predominante da demanda. Use
`assets/response-template.md` como o asset roteado e esqueleto terminal; omita
apenas blocos marcados opcionais.

Quando a projeção exigir somente humano, mantenha Markdown acionável com no
máximo 7.000 caracteres. Quando exigir somente LLM, converta os mesmos campos
para XML com `summary`, `status`, `artifacts`, `evidence`, `handoff`, `risks` e
`next_steps`; não altere o estado nem invente evidence.

## Terminal states

- `completed`: target criado uma vez e todos os validators passaram.
- `blocked`: zero escrita; inclua blocker, gate/validator e mínimo próximo input.
- `partial`: houve handoff/validator ou arquivo criado que não pôde ser validado;
  não declare demanda final pronta.

Com `must_ask_now`, mostre o preflight resumido, faça exatamente uma pergunta
material e termine o turno. Não inclua uma segunda pergunta em bullets,
parênteses ou próximos passos.

## Required response content

A resposta terminal sempre contém status, resumo, artefatos, evidence/validators,
handoffs e ownership, gates/approvals, assumptions/validate-later, riscos,
resume state e próximos passos. Em `completed`, aponte o target e declare que
nenhum workflow downstream foi invocado. Em `blocked`, declare explicitamente
que nenhum arquivo foi criado. Em `partial`, liste exatamente o que existe e o
que não foi validado.

Pode sugerir, sem executar, que o usuário escolha depois entre análise técnica,
decision preflight, action planning ou outro destino. Não apresente essa escolha
como continuação automática.

## LLM projection

```xml
<loki_demand_text_improver_response>
  <summary></summary>
  <status>completed|blocked|partial</status>
  <artifacts></artifacts>
  <evidence></evidence>
  <handoff></handoff>
  <risks></risks>
  <next_steps></next_steps>
</loki_demand_text_improver_response>
```
