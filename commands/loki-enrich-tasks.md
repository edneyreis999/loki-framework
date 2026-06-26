---
name: loki:enrich-tasks
type: command
status: draft
domain: continuous-improvement
required_skills:
  - loki-enrich-tasks
execution_profile:
  model_class: generalist
  default_effort: medium
  max_effort: high
  escalation_signals:
    - conflicting retrospective or build evidence
    - enrichment changes execution order, scope, or gates
    - durable package policy may be affected
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: low
    documentation_durable: high
    validator: low
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:enrich-tasks

## Purpose

Revisar e enriquecer tasks da fase ativa usando aprendizados anteriores, retrospectivas e builds, melhorando apenas a execucao do plano atual sem promover contexto duradouro diretamente.

## Inputs

- `FASE_ATUAL`: numero ou identificador da fase alvo.
- `TASKS_MD`: caminho para `tasks.md` do plano ativo.
- `DIR_RETROSPECTIVAS`: arquivo ou diretorio com retrospectivas relevantes.
- `DIR_BUILDS`: arquivo ou diretorio com builds, validacoes ou evidencias relevantes.
- `INTERACTIONS_RELEVANTES` opcional: decisoes humanas, approvals, defaults ou rejeicoes que possam afetar a fase.
- Escopo de enriquecimento solicitado.

## Outputs

- Tasks atualizadas ou proposta de patch.
- Registro de decisoes e pendencias humanas.
- Resultado do research gate: nao necessario, pulado com motivo ou realizado com fontes citadas.
- Registro local de observacao ou atrito resolvido para consolidacao posterior na `loki:retrospectiva-tecnica`.
- Backlog de melhorias quando algo estiver fora do escopo.

## Allowed Writes

- Markdown do plano ativo.
- `interaction/faseN/` para perguntas ou defaults aprovados.

## Forbidden Writes

- `AGENTS.md`
- `CLAUDE.md`
- Project-context duradouro do projeto consumidor.
- Commands, skills, agents, templates, validators, docs consolidados e `manifest.yaml`.
- Runtime, engine, framework ou superficies sensiveis do consumidor fora do escopo aprovado.
- `.claude/**` e `.agents/**`.

## Required Skills

- `loki-enrich-tasks`

## Workflow

1. Confirmar `FASE_ATUAL`, `TASKS_MD`, fontes transitorias, escopo permitido e forbidden writes.
2. Carregar `loki-enrich-tasks` antes de analisar ou editar tasks.
3. Ler `TASKS_MD`, identificar tasks da fase alvo e localizar `task-N.M.md` correspondentes.
4. Entender objetivo, arquivos provaveis, riscos, dependencias, criterios de sucesso, validators e human loops da fase antes de ler aprendizados antigos.
5. Analisar retrospectivas, builds e interactions em paralelo por arquivo ou lote pequeno quando o ambiente permitir.
6. Consolidar achados em uma visao interna com relacao com a fase, tasks afetadas, instrucao concreta, necessidade de leitura adicional e confianca.
7. Aplicar research gate condicionado somente depois do contexto local:
   - pesquisar externamente se o usuario pedir ou se a decisao depender de documentacao atual de biblioteca, framework, engine, API, plugin, seguranca, licenca ou compatibilidade;
   - preferir docs oficiais, repositorios primarios, release notes ou provedor atual de documentacao disponivel;
   - registrar fonte, versao/data quando relevante, fato extraido e impacto;
   - nunca deixar pesquisa externa substituir o estado local do projeto consumidor.
8. Resolver ambiguidades antes de editar: use aprendizado validado por execucao quando ele corrigir claramente a task no mesmo escopo; pergunte ao usuario apenas quando fontes aplicaveis e plausiveis exigirem decisoes incompativeis.
9. Editar somente `tasks.md`, `task-N.M.md` da fase alvo ou `interaction/faseN/`, preservando estrutura, evitando duplicacao e transformando aprendizados em diretrizes tecnicas objetivas.
10. Rodar checklist final: fase certa, texto sem fonte interna sensivel, nenhuma reescrita cosmetica, instrucao especifica, nenhuma duvida pendente que exija gate humano.

## Handoffs

- `source-researcher` em modo read-only quando uma edicao de task depender de
  compatibilidade atual, contrato upstream, conflito entre fontes ou lacuna
  multi-fonte que o research gate tenha autorizado. O retorno deve ser
  convertido em instrucao objetiva, pergunta humana, validator ou stop
  condition da fase atual.
- Nenhum handoff normativo direto. Observacoes locais seguem para consolidacao
  posterior apenas quando o usuario executar `loki:retrospectiva-tecnica`.

## Validators

- As mudancas atingem apenas `tasks.md`, `task-N.M.md` ou `interaction/faseN/`.
- O enriquecimento reduz ambiguidade ou risco real da fase atual.
- Tasks corretas nao foram reescritas por estilo, reorganizacao ou preferencia de redacao.
- Aprendizados foram convertidos em instrucao direta, restricao tecnica, validator, cuidado de implementacao, criterio de aceite ou nota de compatibilidade.
- Qualquer aprendizado que pareca duradouro fica apenas registrado como observacao local para consolidacao posterior na `loki:retrospectiva-tecnica`, nao como candidato normativo direto.
- As fontes usadas ficam registradas em alto nivel, sem copiar material interno desnecessario.
- Pesquisa externa foi realizada com fontes citadas ou pulada com motivo.
- Fontes externas nao substituem evidencias locais do projeto consumidor.

## Human Gates

- `interview` quando o enriquecimento mudar escopo, ordem, human loop ou criterio de sucesso.
- `approval` apenas se o enriquecimento passar a exigir mudanca de politica ou artefato duradouro; nesse caso, interrompa a edicao local e registre a necessidade para a `loki:retrospectiva-tecnica`.

## Packaging Checks

- Nao aplicavel por default. Se a descoberta sugerir mudar package docs, `AGENTS.md`, `CLAUDE.md` ou outro artefato duradouro, registrar a observacao no plano ativo e deixar a consolidacao para a `loki:retrospectiva-tecnica`.

## Stop Conditions

- Caminhos obrigatorios inexistentes, inacessiveis ou ambiguos.
- Nao e possivel determinar quais tasks pertencem a `FASE_ATUAL`.
- Fontes aplicaveis ao mesmo escopo conflitam e nao ha evidencia segura para escolher uma fonte de verdade.
- O enriquecimento exigiria revelar fonte interna sensivel.
- A melhoria correta pertence a uma superficie duradoura do projeto ou do pacote.
- A mudanca alteraria politica do framework sem approval.
- Pesquisa externa revela conflito material sem validator ou decisao humana possivel.

## Resume Contract

Registrar o que foi alterado no plano ativo, por que, quais fontes foram usadas em alto nivel, resultado do research gate, quais pendencias continuam abertas e quais observacoes devem ser consolidadas depois na `loki:retrospectiva-tecnica`.
