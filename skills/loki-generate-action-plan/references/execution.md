# Execution — loki-generate-action-plan

## Purpose And Observable Contract

Este command orquestra a transformacao de entrada aprovada em plano faseado,
executavel por outra LLM e retomavel sem memoria da conversa.

- Inicio: entrada normalizada, escopo verificavel e preflight pronta quando aplicavel.
- Conclusao: diretorio aprovado contem todos os artefatos e validadores passam,
  ou existe stop condition explicita.
- Resultado verificavel: DAG de fases/tasks focadas, owners, writes, validators,
  human loops, stop conditions e estado de retomada.
- Saidas obrigatorias: siga integralmente `references/response.md`.

## Execution Profile

```yaml
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - large multi-phase plan
    - complex dependency graph
    - sensitive writes or human gates are hard to model
  handoff_effort:
    research: high
    coding: medium
    documentation_transient: high
    documentation_durable: high
    validator: medium
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha planejamento em unidades com
responsaveis; selecione agentes; forneca contexto autocontido; acompanhe cada
handoff ate estado terminal; aplique validators, gates e approvals; e consolide
plano, evidencias, riscos e proximos passos. Mantenha responsabilidade pelo
estado global depois de delegar.

## Allowed Writes

- Markdown e subpastas vazias somente dentro do novo diretorio de plano depois
  de approval explicito e separado para esse path exato.

## Forbidden Writes

- Qualquer superficie fora do diretorio de plano aprovado.
- Runtime, engine, framework, `<consumer_runtime_surfaces>`,
  `<sensitive_write_patterns>` ou superficies proibidas.
- `.claude/**`, `.agents/**` e `.codex/**`.
- Blueprint consolidado, docs duradouros, `AGENTS.md` ou `CLAUDE.md` sem
  approval posterior especifico.

## Required Skills And Commands

```yaml
required_skills:
  - lf-action-plan-authoring
required_commands: []
```

Carregue `lf-action-plan-authoring` antes de planejar. Carregue
`lf-template-library` e leia integralmente os templates `tasks-template.md` e
`task-template.md` antes de materializar arquivos. Carregue condicionalmente
`lf-index-navigator` para docs do consumidor e
`<technology_required_skills>` quando o escopo exigir tecnologia.

## Execution Planning And Replanning

Transforme a entrada normalizada em DAG com fases, tasks de um passe focado de
2–4h, dependencias, referencias, owners, target files, validators, human loops,
gates e criterios de conclusao. Planeje antes de escrever. Replaneje quando uma
decisao, referencia, dependencia ou validator invalidar etapas posteriores;
nunca esconda mudanca de topologia.

## Handoffs

- `source-researcher`, read-only, para referencias fracas, `TODO: localizar`,
  fontes desconhecidas ou conflitos bloqueantes;
- `bibliotecario`, read-only, para lacuna limitada a `/docs` localizavel por
  `docs/index.xml`;
- Write Agent `scoped-writer` aplicavel, para materializar arquivos do plano.

Antes de invocar subagente, entregue objetivo, unidade, fatos/decisoes, fontes,
paths, dependencias, escopo, allowed/forbidden writes, criterios, validators,
gates, formato e destino do handoff. Nao use contexto implicito. Registre
origem, destino, objetivo, entrada, resultado esperado, status, evidencia e
proximo destino; acompanhe ate terminal. O retorno de pesquisa vira referencia,
pergunta humana ou stop condition, nunca decisao automatica.

## Workflow

1. Consuma entrada normalizada, decisoes, preflight e limites.
2. Pare com `must_ask_now` aberto ou `ready_for_next_phase: false`.
3. Planeje fases, tasks, dependencias, referencias, validators, human loops,
   owners e ordem topologica antes de escrever.
4. Use `TODO: localizar` para lacuna nao bloqueante; pare se ela impedir uma
   task executavel.
5. Proponha path simples baseado no escopo e aguarde approval explicito e
   separado do diretorio, mesmo quando `candidate_plan_directory` foi enviado.
6. Depois do approval, crie `tasks.md`, cada `task-N.M.md` e as subpastas de
   fase usando os templates roteados por `lf-template-library`.
7. Rode validadores estruturais e corrija o plano antes de concluir.

## Artifact Structure

Crie no diretorio aprovado:

- `tasks.md`;
- um `task-N.M.md` por task;
- `interaction/faseN/`, `builds/faseN/` e `retrospetivas/faseN/` para toda fase,
  mesmo quando inicialmente vazias.

## Required Fields

Cada fase declara objetivo, tasks, dependencias e validacao observavel. Cada
task declara objetivo, contexto, requisitos, fora de escopo, dependencias,
referencias, passos, validators, observable validation, human loop,
scoped write plan, definition of done e resume notes.

## Write Ownership And Serialization

Prefira Write Agent `scoped-writer` aplicavel para task com targets exatos e
escrita pesada/sensivel. O envelope declara owner, target files, allowed writes,
scoped write domains, validators, gates e evidencias. Se o orquestrador for
owner apesar de writer aplicavel, registre justificativa no execution profile
ou scoped write plan.

Defina owner unico por arquivo, detecte sobreposicao, serialize writes e
interrompa writers concorrentes; leituras independentes podem ser paralelas.
Escrita direta so depois de registrar ausencia de Write Agent. Nesse caso,
assuma envelope completo e registre no completion record tipo de escrita, motivo,
oportunidade/escopo de writer futuro, evidencias e riscos. Conveniencia nao e
justificativa.

## Validators

- Toda fase tem validacao observavel e toda task tem referencia concreta ou
  `TODO: localizar` explicito.
- Nenhuma task e generica ou maior que um passe focado de 2–4h.
- Dependencias formam DAG/topologia valida sem pular setup.
- Escritas sensiveis futuras possuem gate e validator.
- Scoped writers declaram owner, targets, writes, domains, validators e gates;
  excecoes do orquestrador tem justificativa.
- Todas as tres subpastas existem para cada fase.
- O plano e retomavel apenas por `tasks.md` e `task-N.M.md`.
- Falha ou pendencia de validator, gate ou approval interrompe o fluxo.

## Human Gates

- `interview` para escopo, risco, prioridade ou referencia bloqueante.
- `approval` separado antes de criar o diretorio e para escrita sensivel futura.
- `human-validation` para comportamento, runtime, integracoes, persistencia ou output.
- `technical-review` quando o plano alterar artefato ou politica consolidada.

## Packaging Checks

Gerar o plano nao altera o pacote. Quando o escopo futuro tocar o pacote, cada
task deve incluir guardrails e technical-review aplicaveis.

## Stop Conditions

- Objetivo ou escopo sem verificacao; diretorio ainda nao confirmado.
- `must_ask_now` sem resposta ou ordem dependente de decisao humana.
- Referencia ausente torna task inexequivel.
- Escopo/permissao insuficiente, dependencia indisponivel, handoff sem destino,
  conflito de writers, validator falho ou gate/approval pendente.
- Plano exigiria escrita fora do escopo aprovado.

## Evidence-First Cutover

Cada subagente devolve completion record; o orquestrador captura evidence
sanitizada após o handoff ou registra `partial`, `unavailable` ou `unsupported`.
Não registrar CoT privado nem invocar retrospectiva automaticamente.

## Resume Contract

Registre entrada, path candidato/aprovado, DAG, fase/task atual, status,
handoffs, human loops, validators, owners, writes, artefatos esperados,
etapas concluidas, lacunas, riscos, proxima acao e condicao para continuar.
Retome por `tasks.md` e `task-N.M.md`, sem reiniciar quando o estado bastar.
