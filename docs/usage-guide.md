---
title: Guia de Uso do Loki Framework Local
type: usage-guide
status: draft
created: 2026-06-24
scope: local-project-package
---

# Guia de Uso do Loki Framework Local

O Loki Framework local organiza trabalho em projetos de software e jogos usando
`commands`, `skills` e `agents`. Ele e um pacote documental e operacional
autocontido: descreve como conduzir analise, plano, execucao, validacao e
melhoria continua sem depender de blueprint, planos historicos ou arquivos de
outro projeto.

## Estrutura

- `commands/`: fluxos invocaveis, como feedback, analise tecnica, plano, execucao e melhoria continua.
- `skills/`: procedimentos tecnicos ou processuais que devem ser carregados quando o dominio aparecer.
- `agents/`: papeis especialistas que retornam analise, checklist ou proposta.
- `templates/`: contratos minimos para criar novos comandos e componentes.
- `docs/`: limites, inventario e guia de uso.
- `docs/project-context-catalog.md`: contrato entre o pacote Loki e a
  documentacao duradoura do projeto consumidor.
- `manifest.yaml`: lista componentes, origem, destino sugerido e guardrails.

## Fluxos Canonicos

Use estes dois documentos como fonte principal do ciclo operacional:

- [Workflow de Execucao de Plano do Loki](loki-plan-execution-workflow.md):
  descreve como uma descricao curta vira analise, plano, tasks, escrita
  serializada, validacao e evidencia.
- [Workflow de Aprendizado do Loki](loki-learning-workflow.md): descreve como
  resultados, bugs, feedbacks e retrospectivas viram ajuste local, candidato,
  regra duradoura ou backlog.

Quando a melhoria atingir o proprio pacote, aplique
`docs/package-authoring-guardrails.md` depois de identificar o destino pelo
workflow de aprendizado.

## Gates Humanos

O framework usa gates para impedir validacao falsa:

- `interview`: quando falta requisito, preferencia ou contexto.
- `approval`: antes de politica duradoura, instalacao, promocao ou escrita sensivel.
- `runtime-validation`: obrigatorio para comportamento perceptivel, estado
  runtime, integracoes ativas ou superficies declaradas por skill tecnica.
- `technical-review`: para mudanca em command, skill, agent, template, validator ou doc consolidado.

Parsers estruturais, validadores de linguagem e diff restrito reduzem risco
estrutural, mas nao substituem validacao humana quando a mudanca afeta
comportamento perceptivel ou o runtime do consumidor.

## Skills Core e Extensoes

As skills Loki (`loki-feedback`, `loki-enrich-tasks`,
`loki-run-plan-execution`, `loki-retrospectiva-tecnica`, `loki-command-creator`,
`loki-agent-creator`, `loki-skill-creator`, `loki-index-navigator`,
`loki-tech-analysis-authoring` e `loki-action-plan-authoring`) governam
entrevista, autoria de analises e planos, enriquecimento de tasks, execucao de fase,
retrospectiva, navegacao de documentacao e evolucao controlada de commands,
agents e skills.

Skills tecnicas por tecnologia entram somente quando o projeto consumidor, o
pedido do usuario ou o plano aprovado declarar aquela superficie.

### Extensao Opcional: RPG Maker MZ

Use `loki-rpg-maker-mz-data-json` somente quando o projeto consumidor exigir
edicao ou revisao de superficies de dados RPG Maker MZ, como Database, Common
Events ou mapas.

Use `loki-rpg-maker-mz-plugin-workflow` somente quando o projeto consumidor
exigir criar, editar, validar ou ativar plugins RPG Maker MZ.

Essas duas skills sao extensoes especializadas opcionais. Elas nao sao
obrigatorias para feedback, analise tecnica, plano de acao, execucao de plano,
retrospectiva ou melhoria continua do core Loki.

Para evoluir o pacote, use os criadores certos por tipo de artefato e valide contra `docs/package-authoring-guardrails.md`. O objetivo e transformar aprendizado em regra operacional sem depender de memoria da conversa.

## Quando Registrar Aprendizados

Use [Workflow de Aprendizado do Loki](loki-learning-workflow.md) como unica
referencia canonica para decidir entre ajuste local, retrospectiva, promocao
duradoura e backlog.

## Agents

- `standards-curator`: classifica aprendizados como universal, provavel-universal, project-specific ou backlog.
- `bibliotecario`: consulta `docs/index.xml` antes de abrir a documentacao
  duradoura do consumidor.
- `catalogador`: consolida aprendizado `project-specific` em `/docs` do
  consumidor e mantem o catalogo XML.
- `runtime-qa`: produz checklist e evidencia exigida; nunca simula
  confirmacao humana.
- `execution-context-reader`: extrai contexto em modo read-only para
  `loki:run-plan`, usando `DIR_ANALISE`, tasks e fontes locais permitidas sem
  escrever.
- `source-researcher`: mapeia fatos, lacunas e conflitos em pesquisa
  multi-fonte antes de analise, plano, feedback, enriquecimento ou promocao,
  sem decidir solucao nem escrever.
- `technical-implementer`: no MVP e `proposal-only`; propoe mudancas,
  validadores e gates, mas nao escreve diretamente.

## Contexto Duradouro do Consumidor

- O pacote Loki guarda regras do framework, nao fatos do projeto consumidor.
- Regras de negocio, lore, fluxo funcional e terminologia do projeto consumidor
  devem morar em `docs/**/*.md`.
- `docs/index.xml` e o catalogo preferencial para `bibliotecario` e
  `loki-index-navigator`.
- `AGENTS.md` e `CLAUDE.md` do consumidor recebem apenas roteamento minimo para
  dizer quando a LLM deve consultar `/docs`.

## Regra de Uso Seguro

Mantenha o diretorio do pacote como fonte auditavel. Instale em `.claude/` ou
`.agents/` somente depois de approval especifico. Nao copie `.agents/` como
fonte normativa. Nao declare runtime validado sem gate humano apropriado.

Quando a mudanca for no proprio pacote, nao pare em retrospectiva ou intuicao: atualize o artefato normativo correto, registre impacto no `manifest.yaml` se necessario e termine com validacao objetiva de estrutura e autocontencao.
