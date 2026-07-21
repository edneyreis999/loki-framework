# Retrospectiva técnica — plano 032 até task-2.2

## Status

partial

## Resumo

Escopo registrado: execução observável do plano 032 desde a task-1.1 até o
trabalho realizado para a task-2.2. A task-1.1 produziu e recebeu aprovação
humana para a matriz canônica. A task-1.2 restaurou o baseline do validator de
upgrade, com suite 17/17. A task-2.1 fechou os schemas agentic canônicos
(manifest 4, report 5 e digest 4) e seus mirrors. O diff atual da task-2.2
fecha a policy de session evidence e os resultados observados incluem fixtures
positivas/negativas e WTR limpo após uma correção de ordem.

A fase 2 não está concluída: task-2.3 permanece futura. Além disso, o estado
persistido do plano ainda declara task-2.2 como `pending`; esta retrospectiva
não afirma sua conclusão persistida.

## Artefatos

### Criados

- `builds/fase1/canonical-contract-matrix.md` — matriz da task-1.1, com os
  contratos canônicos e os cortes planejados.
- Este arquivo de retrospectiva.

### Alterados e observados

- `scripts/validate-install-loki-upgrade.py` — baseline da task-1.2.
- Validator, contratos e templates agentic da task-2.1, incluindo seus mirrors.
- Diff de session evidence da task-2.2: collector, validator, contratos e os
  pares de templates autorizados.
- `tasks.md` e `task-1.1.md` a `task-2.2.md` — fonte do escopo, dependências e
  estado persistido.

### Não alterados por esta retrospectiva

Nenhuma regra, skill, command, template, validator, catálogo de inferências ou
artefato de consumidor foi promovido, pontuado, reorganizado ou removido.

## Evidências e validadores

| Escopo | Fato observável | Fonte |
| --- | --- | --- |
| task-1.1 | matriz materializada; source-map e classification review passaram; aprovação humana registrada | `builds/fase1/canonical-contract-matrix.md#execution-completion`; `task-1.1.md#resume-notes` |
| task-1.2 | suite de upgrade passou 17/17; contagens observadas 99/68/108 | `task-1.2.md#observable-validation`; `task-1.2.md#resume-notes` |
| task-2.1 | agentic self-test, XML parse, paridade de 4 mirrors e scan legado passaram | `task-2.1.md#resume-notes` |
| task-2.2 | fixtures positivas/negativas de session evidence, XML parse, `cmp`, diff check e WTR foram relatados como passados após correção | evidência operacional fornecida para esta retrospectiva; diff atual autorizado |
| plano | `validate-run-plan-review-state` foi executado com sucesso durante a continuidade | evidência operacional fornecida para esta retrospectiva |

Lacuna: não há checkpoint persistido em `tasks.md` nem `loki_task_state`
atualizado que confirme o terminal da task-2.2. Isso deve ser reconciliado no
fluxo de execução antes de liberar a task-2.3.

## Decisões humanas

- A matriz da task-1.1 foi aprovada em chat em 2026-07-21.
- Correção de execução: o usuário esclareceu que `Human Loop` e
  `technical-review` classificam a revisão, mas não autorizam uma parada
  cerimonial quando não existe blocker. A referência aplicável é a `Human Gate
  Resolution Policy` de `lf-run-plan-execution`.

## Rastro operacional material

1. Confirmou-se a matriz canônica para separar schemas `1` ainda canônicos de
   compatibilidade legada a remover.
2. Corrigiu-se o drift do validator de upgrade antes dos cortes de contrato.
3. Fecharam-se schemas agentic e paridade entre templates raiz e mirrors.
4. O trabalho de session evidence substituiu campos negativos legados por uma
   policy positiva e fechada; o validator passou a rejeitar shapes
   desconhecidos.
5. Uma revisão WTR identificou ordem inválida de `overall_status`; a ordem foi
   corrigida e a validação foi repetida com resultado limpo.

## Atritos de execução

### 1. Revisão cerimonial após task-1.2

- Category: `user-correction`, `communication-waste`, `safety-gate-friction`
- What Happened: foi solicitada aprovação humana adicional após o baseline
  verde, embora não houvesse desvio, falha ou nova decisão material.
- Expected Behavior: continuar a DAG após validação suficiente e registrar
  revisão técnica como evidência, sem transformar o Human Loop em blocker.
- Actual Behavior: a execução foi interrompida por um checkpoint cerimonial.
- Context: task-1.2; policy de human gates de `lf-run-plan-execution`.
- Evidence: correção explícita do usuário e referência de policy indicada.
- Cause: confirmada — interpretação incorreta do Human Loop como parada
  obrigatória.
- Resolution Or Outcome: a interpretação foi corrigida; a continuidade deve
  parar apenas diante de blocker real, desvio, validator falho/inconclusivo,
  escopo novo ou risco não coberto.
- Was Useful: parcialmente; expôs uma ambiguidade operacional a evitar.
- Waste Impact: medium.
- Reuse Guidance: consultar a Human Gate Resolution Policy ao encontrar um
  gate de revisão.
- Avoid Next Time: não pedir aprovação apenas para encerrar uma task validada.
- Minimum Next Step: prosseguir para a próxima dependência pronta e registrar
  a revisão no estado/evidência aplicável.

### 2. Ordem inválida no shape de session evidence

- Category: `validation-friction`, `format-friction`
- What Happened: WTR da task-2.2 detectou ordem inválida envolvendo
  `overall_status`.
- Expected Behavior: emitter e validator respeitam a ordem fechada do contrato.
- Actual Behavior: a primeira versão não respeitava a sequência esperada; a
  correção e o reteste obtiveram resultado limpo.
- Context: collector/validator e fixture de session evidence da task-2.2.
- Evidence: resultado operacional de WTR e diff atual autorizado.
- Cause: confirmada pelo resultado do validator; causa de design além da ordem
  observada não foi registrada.
- Resolution Or Outcome: reordenar o campo e repetir a validação.
- Was Useful: sim; a validação fechada detectou a incompatibilidade antes de
  qualquer alegação de terminal persistido.
- Waste Impact: low.
- Reuse Guidance: validar ordem XML além da presença de campos ao endurecer um
  shape.
- Avoid Next Time: executar a fixture/validator fechado antes do handoff WTR.
- Minimum Next Step: conservar esse validator no conjunto de aceite da task.

### 3. Reconciliação de checkpoints WTR

- Category: `state-friction`, `format-friction`
- What Happened: durante a continuidade, foi necessário ordenar paths e ajustar
  índices para registrar/referenciar checkpoints WTR corretamente.
- Expected Behavior: checkpoint e referências locais refletem os targets e a
  ordem do estado do plano.
- Actual Behavior: exigiu ajuste operacional adicional antes da continuidade.
- Context: `tasks.md` e estados de task da execução parcial.
- Evidence: rastros de checkpoint referenciados em `task-1.1.md`,
  `task-1.2.md` e `task-2.1.md`.
- Cause: confirmada apenas como necessidade de reconciliação de estado; não há
  evidência suficiente para atribuir causa mais específica.
- Resolution Or Outcome: paths foram ordenados e índices ajustados para os
  checkpoints já persistidos.
- Was Useful: parcialmente; mantém o estado retomável, mas não altera o
  contrato de produto.
- Waste Impact: low.
- Reuse Guidance: ordenar a lista de paths e verificar índices antes de
  persistir um checkpoint.
- Avoid Next Time: aplicar essa checagem no preflight de persistência WTR.
- Minimum Next Step: reconciliar também a task-2.2 somente com sua evidência
  terminal disponível.

## Caminho mínimo recomendado

1. Reconciliar e persistir o estado/evidência terminal da task-2.2, caso seus
   validators ainda estejam confirmados no worktree.
2. Executar a task-2.3: remover `operational_trace` do contrato público da
   retrospectiva e adicionar sua rejeição explícita.
3. Rodar os validators definidos em task-2.3 e persistir o checkpoint antes de
   avançar para a fase 3.

## Aprendizados e candidatos

### Aprendizado validado

Um valor de schema `1` não identifica, por si só, compatibilidade legada: a
matriz canônica confirmou schemas `1` ainda canônicos em famílias específicas.

### Falha operacional corrigida

O Human Loop de revisão não é uma condição automática de pausa. A continuidade
depende de blockers materiais, não da mera presença do gate.

### Hipótese não promovida

Ordenar paths antes da persistência de WTR pode reduzir reconciliações futuras.
É uma hipótese operacional; esta retrospectiva não a transforma em política.

### Candidatos especializados de inferência

```yaml
analytic_inference_candidates: []
analytic_inference_candidates_empty_reason: "não há capture_id e lineage persistidos suficientes para candidato especializado"
```

- Validação dos candidatos: não aplicável; nenhum candidato emitido.
- Lineage indisponível: `capture_id` e lineage de execução não foram
  persistidos nas fontes autorizadas desta retrospectiva.
- Consumer/state root provenance: unavailable; a retrospectiva não resolve
  roots nem consulta catálogo.
- Gates para avaliação downstream: nenhum candidato encaminhado.
- Catalogo escrito/promovido/pontuado/reorganizado/purgado: false.
- Route permitido: `loki-continuous-improvement` para avaliação futura; nenhuma
  promoção automática.

## Handoffs, gates e approvals

- task-1.1: aprovação humana da matriz concluída.
- task-1.2 e task-2.1: validações e WTR persistidos como limpos nas fontes.
- task-2.2: trabalho e validações foram observados, mas o terminal ainda não
  está persistido no plano; não liberar task-2.3 por esta retrospectiva.
- Nenhuma aprovação nova é solicitada por este registro.

## Riscos ou blockers

- A fase 2 permanece incompleta enquanto task-2.3 não executar.
- O estado persistido de task-2.2 diverge do trabalho/validação relatados;
  requer reconciliação factual antes da próxima dependência.
- A policy de session evidence é um contrato fechado: mudanças posteriores
  precisam preservar suas fixtures negativas e a ordem XML validada.

## Próximos passos

Owner: orquestrador do plano 032.

Retomar na task-2.2 para reconciliar sua evidência terminal e, em seguida,
executar a task-2.3 conforme sua dependência explícita.

## Resume state

```yaml
resume_state:
  plan: planos/032-remove-legacy-compatibility/tasks.md
  phase: fase2
  completed_persisted_tasks: [task-1.1, task-1.2, task-2.1]
  observed_unreconciled_work: task-2.2
  next_dependency: task-2.2
  blocked_release: task-2.3
  required_reconciliation: persist only evidence that is still observable and validated
  retrospective_write_scope: planos/032-remove-legacy-compatibility/retrospetivas/fase2/retrospectiva-fase2-tasks-1-1-a-2-2.md
```
