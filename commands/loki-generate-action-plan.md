---
name: loki:generate-action-plan
type: command
status: draft
domain: planning
required_skills:
  - loki-action-plan-authoring
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
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:generate-action-plan

## Purpose

Gerar plano faseado e executavel por outro agente, com tasks autocontidas,
dependencias, referencias concretas, human loops, validacao observavel e
estrutura de artefatos Loki.

## Inputs

- Analise tecnica, brief, feedback ou objetivo aprovado.
- Escopo permitido, fora de escopo e superficies proibidas.
- Decisoes humanas ja registradas.
- Diretorio base candidato para o plano.
- Documentacao duradoura do consumidor quando for relevante para o escopo.

## Outputs

- `tasks.md` faseado.
- `task-N.M.md` para cada task.
- Pastas `interaction/faseN/`, `builds/faseN/` e `retrospetivas/faseN/` para
  todas as fases.
- Lista explicita de human loops, validators e stop conditions.
- Owner de escrita por task, com `target_files`, `allowed_writes` e
  `scoped_write_domains` quando a execucao puder usar agente `scoped-writer`.
- Estado de retomada suficiente para `loki:run-plan`.

## Allowed Writes

- Markdown e subpastas vazias dentro do novo diretorio de plano aprovado.

## Forbidden Writes

- Runtime, engine, framework ou superficies sensiveis do consumidor fora do
  escopo aprovado.
- Qualquer superficie fora do novo diretorio de plano aprovado.
- `.claude/**`
- `.agents/**`
- `.codex/**`
- Blueprint consolidado ou documentacao duradoura sem approval posterior.

## Required Skills

- `loki-action-plan-authoring` para contrato de plano, templates, validadores e
  regras de granularidade.
- `loki-index-navigator` quando o plano depender de documentacao duradoura em
  `/docs` do consumidor.
- `<technology_required_skills>` somente quando o escopo aprovado ou a analise
  tecnica exigir detalhes de uma tecnologia especifica.

## Handoffs

- `source-researcher` em modo read-only quando o input aprovado tiver
  referencias fracas, `TODO: localizar`, fontes desconhecidas ou conflitos que
  impedem gerar tasks executaveis. O retorno deve virar referencia concreta,
  pergunta humana ou stop condition; nunca decisao tecnica automatica.
- `bibliotecario` quando a lacuna estiver restrita a documentacao duradoura do
  consumidor em `/docs` e puder ser resolvida por `docs/index.xml`.

## Workflow

1. Fazer scan das entradas, decisoes humanas e limites de escrita.
2. Planejar antes de escrever: fases, tasks, dependencias, referencias,
   validators, human loops, write owners e ordem topologica.
3. Se faltar referencia concreta, usar `TODO: localizar`; se a lacuna impedir
   task executavel, parar e perguntar.
4. Propor diretorio de destino com nome simples baseado no escopo e aguardar
   confirmacao explicita.
5. Criar `tasks.md`, `task-N.M.md` e as subpastas por fase usando:
   - `templates/tasks-template.md`
   - `templates/task-template.md`
6. Rodar validadores estruturais antes de declarar o plano pronto.

## Artifact Structure

Para cada plano aprovado:

- `tasks.md`
- `task-N.M.md`
- `interaction/faseN/`
- `builds/faseN/`
- `retrospetivas/faseN/`

Criar `interaction/`, `builds/` e `retrospetivas/` com uma subpasta para cada
fase, mesmo que fiquem vazias na geracao inicial.

## Required Fields

Cada fase deve declarar objetivo, tasks, dependencias de fase quando houver e
validacao observavel.

Cada task deve declarar objetivo, contexto, requisitos, fora de escopo,
dependencias, referencias, passos de implementacao, validators,
observable_validation, human_loop, scoped_write_plan, definition of done e
resume notes.

## Validators

- Toda fase tem pelo menos uma validacao observavel.
- Toda task tem referencias concretas ou `TODO: localizar` explicito.
- Nenhuma task e generica ou maior que um passe focado de 2-4h.
- Dependencias formam ordem topologica sem pular setup obrigatorio.
- Escritas sensiveis futuras possuem gate humano e validator correspondente.
- Tasks com agente `scoped-writer` possuem owner, `target_files`,
  `allowed_writes`, `scoped_write_domains`, validators e gates.
- As pastas `interaction/`, `builds/` e `retrospetivas/` possuem subpasta para
  cada fase.
- O plano pode ser retomado por `tasks.md` e `task-N.M.md` sem memoria da
  conversa.

## Human Gates

- `interview` para escolhas de escopo, risco, prioridade ou referencia
  bloqueante.
- `approval` antes de autorizar escrita sensivel futura ou criar o diretorio do
  plano.
- `human-validation` para comportamento perceptivel, runtime, integracoes,
  estado persistido ou output gerado.
- `technical-review` quando o plano alterar command, skill, agent, template,
  validator ou politica consolidada.

## Stop Conditions

- O objetivo nao tem escopo verificavel.
- O diretorio de plano ainda nao foi confirmado.
- A ordem de execucao depende de decisao humana ainda nao tomada.
- Referencias ausentes tornam uma task inexequivel.
- O plano exigiria escrita fora do escopo aprovado.

## Resume Contract

O plano deve permitir retomada por `tasks.md` e pelos arquivos `task-N.M.md`,
sem depender de memoria da conversa. Registrar fase atual, task atual, status,
human loops pendentes, validators, arquivos esperados e proxima acao.
