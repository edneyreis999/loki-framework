---
name: loki-enrich-tasks
description: Run the Loki `loki:enrich-tasks` command workflow in Codex. Revise and enrich Loki phase tasks before execution by incorporating prior retrospectives, build learnings, decisions, success criteria, and human loops without exposing unnecessary internal source material or creating direct normative handoffs; use before `loki:run-plan`.
when_to_use:
  - "Use before loki:run-plan when phase tasks need targeted enrichment from prior retrospectives, builds, decisions, success criteria, or human loops."
  - "Use when improving active plan tasks without promoting durable context directly."
argument-hint: "[phase, tasks.md, retrospectives, builds]"
arguments:
  required: []
  optional:
    - phase
    - tasks_md
    - retrospectives
    - builds
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: generalist
adapter_projection:
  codex: "Advisory unless projected through config, profile or custom agent."
  claude_code: "May map to model/effort frontmatter where supported."
escalation_signals:
  - conflicting retrospective or build evidence
  - enrichment changes execution order, scope, or gates
  - durable package policy may be affected
context: standard
agent: main
hooks: []
paths:
  package_skill: "skills/loki-enrich-tasks/SKILL.md"
shell: {}
type: skill
status: draft
used_by:
  - loki:enrich-tasks
---

# loki-enrich-tasks

## When To Use

Use para revisar tasks de uma fase antes de execucao, incorporando aprendizados de retrospectivas, builds e decisoes sem expor fontes internas desnecessarias nem promover contexto duradouro diretamente.

Use antes de `loki:run-plan`, quando a fase atual ja tem `tasks.md` ou `task-N.M.md` e existe evidencia transitoria que possa reduzir ambiguidade, retrabalho ou risco de implementacao.

## Inputs

- `FASE_ATUAL`: numero ou identificador da fase a revisar.
- `TASKS_MD`: caminho para `tasks.md` do plano ativo.
- `DIR_RETROSPECTIVAS`: arquivo ou diretorio com retrospectivas relevantes.
- `DIR_BUILDS`: arquivo ou diretorio com builds, validacoes ou evidencias relevantes.
- `INTERACTIONS_RELEVANTES` opcional: decisoes humanas, approvals, defaults ou rejeicoes.
- Escopo de enriquecimento solicitado, quando houver.

Resolva todos os caminhos no filesystem. Se algum caminho obrigatorio nao existir, estiver inacessivel ou for ambiguo, pare antes de editar e pergunte ao usuario.

## Procedure

1. Leia `TASKS_MD` antes de qualquer fonte antiga.
2. Identifique todas as tasks da `FASE_ATUAL` e localize arquivos detalhados como `task-N.M.md`.
3. Entenda objetivo, escopo tecnico, arquivos provavelmente impactados, riscos, dependencias, decisoes ja documentadas, validators, criterios de sucesso e human loops.
4. Analise retrospectivas, builds e interactions por arquivo ou lote pequeno. Quando houver suporte, paralelize a leitura e consolide apenas depois que todas as analises retornarem.
5. Para cada fonte transitoria, produza internamente: aprendizados tecnicos, relacao possivel com `FASE_ATUAL`, tasks afetadas, instrucoes concretas sugeridas, arquivos adicionais a investigar e nivel de confianca.
6. Investigue arquivos locais adicionais quando um aprendizado parecer aplicavel, mas depender do escopo atual.
7. Aplique o research gate condicionado descrito abaixo.
8. Resolva ambiguidades antes de editar. Nao trate diferenca terminologica como conflito real.
9. Edite apenas quando houver melhoria clara, aplicavel e tecnicamente justificada para a fase atual.
10. Converta aprendizados em diretrizes tecnicas objetivas: instrucao direta, restricao tecnica, validator, cuidado de implementacao, criterio de aceite ou nota de compatibilidade.
11. Preserve estrutura, nao reescreva texto correto por estilo, evite duplicacao e nao altere tasks de outras fases.
12. Registre qualquer mudanca de escopo como pergunta ou approval.
13. Se surgir atrito resolvido ou aprendizado aparentemente duradouro, registre apenas observacao local para consolidacao posterior na `loki:retrospectiva-tecnica`.

## Research Gate

Pesquisa externa e condicional. Execute somente quando uma destas condicoes for verdadeira:

- o usuario pedir internet ou contexto externo atual;
- a decisao depender de documentacao atual de biblioteca, framework, engine, API, plugin, seguranca, licenca ou compatibilidade;
- fontes locais explicarem o estado atual, mas nao o contrato upstream;
- uma skill tecnica exigir documentacao oficial atual.

Placement:

1. Primeiro mapeie fontes locais e superficies afetadas.
2. Depois formule perguntas externas precisas.
3. Prefira documentacao oficial, repositorios primarios, release notes ou provedor atual de documentacao disponivel no ambiente.
4. Registre fonte, versao/data quando relevante, fato extraido e impacto na task.

Nao use pesquisa externa para sobrescrever fatos locais do projeto consumidor. Se fonte externa conflitar com o estado local, registre o conflito e recomende validator ou decisao humana.

## Ambiguity Resolution

Pergunte ao usuario somente quando todas as condicoes forem verdadeiras:

- existe divergencia real entre fontes relevantes;
- a divergencia afeta edicao ou execucao da fase atual;
- as fontes conflitantes parecem aplicaveis ao mesmo escopo;
- nao ha evidencia suficiente para escolher com seguranca;
- prosseguir pode gerar retrabalho, implementacao incorreta ou alteracao indevida.

Nao pergunte quando:

- a divergencia nao afeta a fase atual;
- aprendizado validado por execucao corrige claramente uma fonte anterior no mesmo escopo;
- a informacao pertence a outro componente, fase, modulo ou cenario;
- a diferenca e apenas terminologica;
- a duvida pode ser resolvida lendo artefatos disponiveis.

Classifique conflitos antes de agir:

| Conflito | Acao |
| --- | --- |
| Task diz X, aprendizado validado aplicavel diz Y | Usar Y sem perguntar |
| Task diz X, aprendizado diz Y, mas escopo de Y e incerto | Perguntar ao usuario |
| Aprendizado A diz X, aprendizado B diz Y, ambos aplicaveis | Perguntar ao usuario |
| Aprendizado diz X, documento atual diz Y, ambos aplicaveis e plausiveis | Perguntar ao usuario |
| Aprendizado diz X, documento antigo diz Y | Usar aprendizado sem perguntar |
| Documento diz X, outro documento diz Y, ambos atuais e aplicaveis | Perguntar ao usuario |
| Informacao divergente pertence a outro escopo | Ignorar para a fase atual ou registrar fora de escopo |
| Divergencia nao altera execucao | Nao perguntar |

Quando resolver sem perguntar, mantenha registro interno da divergencia, fonte mais confiavel, motivo e impacto na edicao.

## Editing Rules

- Edite apenas `TASKS_MD`, arquivos de task da `FASE_ATUAL` ou `interaction/faseN/`.
- Nao edite fases anteriores ou futuras.
- Nao adicione novas tasks, requisitos ou objetivos fora do escopo da fase, salvo quando necessario para evitar erro tecnico diretamente ligado a execucao.
- Nao altere arquivos apenas porque encontrou um aprendizado antigo.
- Se a task ja refletir corretamente o aprendizado, nao edite.
- Nunca cite, linke, nomeie ou insinue retrospectivas, builds, arquivos analisados, datas de fonte interna ou frases como "foi aprendido anteriormente", "na fase passada" ou "no build anterior" dentro dos artefatos editados.
- Use fontes transitorias apenas como contexto interno.

## Outputs

- Tasks enriquecidas.
- Pendencias humanas explicitadas.
- Resultado do research gate: nao necessario, pulado com motivo ou realizado com fontes citadas.
- Observacoes locais para consolidacao posterior na `loki:retrospectiva-tecnica`.
- Backlog de melhorias fora de escopo.

## Validation Checklist

Antes de finalizar, valide:

- Todos os caminhos obrigatorios foram resolvidos.
- As alteracoes atingem apenas a fase atual.
- Nenhum texto editado menciona fonte interna sensivel.
- Nenhum trecho correto foi reescrito por estilo.
- Cada mudanca reduz risco real ou ambiguidade concreta.
- Cada instrucao adicionada e especifica o bastante para orientar implementacao.
- Pesquisa externa foi realizada com fonte citada ou pulada com motivo.
- Fonte externa nao substituiu evidencia local do projeto consumidor.
- Toda duvida que mudaria escopo, ordem, human loop ou criterio de sucesso virou gate humano.

## Limits

- Nao muda o objetivo da fase sem approval.
- Nao promove regra duradoura.
- Nao gera candidato normativo direto para `loki:continuous-improvement`.
- Nao usa internet como etapa obrigatoria; pesquisa externa e gate condicionado.

## Required Gates

- `interview` para decisao de escopo.
- `approval` para mudanca de politica, template, command, skill, agent ou standard; nesse caso, interrompa a promocao direta e deixe a consolidacao para a `loki:retrospectiva-tecnica`.
