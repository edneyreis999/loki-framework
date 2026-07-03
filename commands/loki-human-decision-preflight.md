---
name: loki:human-decision-preflight
type: command
status: draft
domain: planning
required_skills:
  - lf-tech-analysis-authoring
  - lf-action-plan-authoring
execution_profile:
  model_class: generalist
  default_effort: medium
  max_effort: high
  escalation_signals:
    - many open human decisions
    - conflicting local evidence
    - sensitive writes or irreversible product choices
    - decision changes plan topology or acceptance criteria
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: medium
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:human-decision-preflight

## Purpose

Classificar decisoes humanas pendentes antes de gerar plano de acao, separando
o que precisa ser perguntado agora do que pode ser delegado, validado depois ou
resolvido por leitura local.

## Inputs

- Analise tecnica, brief, feedback normalizado, retrospectiva ou objetivo
  aprovado.
- Perguntas abertas, assumptions, riscos, human gates e decisoes humanas ja
  registradas.
- Escopo permitido, fora de escopo, superficies proibidas e destino opcional do
  registro transitorio.
- Documentacao duradoura do consumidor quando for relevante para a decisao.

## Outputs

- Perguntas classificadas em:
  - `must_ask_now`
  - `can_delegate_to_plan`
  - `can_validate_later`
  - `do_not_ask_llm_can_determine`
- Respostas humanas registradas quando fornecidas.
- Handoff para `loki:generate-action-plan` com `ready_for_next_phase`,
  decisoes resolvidas, pendencias delegadas, validators e gates.
- Stop condition quando uma decisao `must_ask_now` continuar sem resposta.

## Allowed Writes

- Nenhuma por default.
- Markdown transitorio no diretorio de analise ou plano aprovado, como
  `interaction/faseN/human-decision-preflight.md`, quando o usuario ou o
  workflow chamador fornecer destino exato.

## Forbidden Writes

- Runtime, engine, framework, assets, dados persistidos, configuracao ativa ou
  superficies sensiveis do consumidor.
- Docs duradouros do consumidor, `AGENTS.md`, `CLAUDE.md`, comandos, skills,
  agentes, templates, validators, `manifest.yaml` ou `install-scopes.json`.
- `.claude/**`
- `.agents/**`
- `.codex/**`

## Required Skills

- `lf-tech-analysis-authoring` para separar fatos, inferencias, hipoteses,
  perguntas abertas, fontes e gates.
- `lf-action-plan-authoring` para decidir se uma pendencia pode virar task,
  validator, human loop ou stop condition no plano.
- `lf-index-navigator` quando a decisao depender de documentacao duradoura em
  `/docs` do consumidor.
- `<technology_required_skills>` somente quando a analise ou o projeto
  declararem uma tecnologia especifica.

## Handoffs

- `bibliotecario` em modo read-only quando a resposta provavelmente estiver em
  `/docs` do consumidor e puder ser localizada por `docs/index.xml`.
- `source-researcher` em modo read-only quando a pergunta puder ser respondida
  por fontes locais multiplas, houver conflito de evidencia ou pesquisa externa
  aprovada.
- `runtime-qa` em modo proposal-only quando a decisao puder ser adiada para
  `human-validation` de comportamento perceptivel.
- Agentes de dominio em modo proposal-only quando ajudarem a distinguir
  preferencia humana de detalhe delegavel ao plano, sem escrever.

Handoffs nao decidem a resposta humana. Eles retornam evidencia, riscos,
validator proposto ou recomendacao de classificacao para o orquestrador.

## Classification Rules

Use `must_ask_now` quando a resposta:

- altera escopo, prioridade, aceite, narrativa/produto, identidade publica,
  destino de escrita, politica, permissao ou caminho de implementacao;
- escolhe entre finais, regras de negocio, tom, nomes, visibilidade, perda de
  dados, risco legal/seguranca ou comportamento irreversivel;
- muda a topologia do plano, dependencias, owners, gates ou arquivos alvo;
- nao pode ser inferida com seguranca por fonte local ou validator.

Use `can_delegate_to_plan` quando a pendencia:

- e uma decisao de implementacao dentro do escopo aprovado;
- pode virar task com owner, `target_files`, validators, human loop e stop
  condition;
- nao muda aceite, escopo ou ordem principal do plano.

Use `can_validate_later` quando a questao:

- depende de percepcao humana, Playtest, UX, audio, visual, performance,
  integracao ativa ou comportamento runtime;
- pode ser expressa como `human-validation` ou validator observavel depois da
  implementacao.

Use `do_not_ask_llm_can_determine` quando:

- a resposta deve ser obtida por leitura local, parse estruturado, docs
  duradouros, schema, codigo, configuracao ou validator;
- perguntar ao humano desperdicaria interacao ou transferiria para ele uma
  verificacao tecnica que o agente deve fazer.

## Workflow

1. Confirmar entrada, escopo, forbidden writes e destino transitorio opcional.
2. Ler a analise ou brief e extrair perguntas abertas, assumptions, riscos,
   human gates e pontos que afetam planejamento.
3. Separar perguntas de intencao humana de perguntas respondiveis por fonte
   local. Conferir rapidamente as fontes locais obvias antes de perguntar.
4. Classificar cada pergunta em uma das quatro categorias, sempre com evidencia
   e motivo.
5. Para `do_not_ask_llm_can_determine`, registrar a fonte ou busca local minima
   que deve responder a pergunta.
6. Para `can_delegate_to_plan`, registrar task/human loop/validator esperado.
7. Para `can_validate_later`, registrar gate `human-validation` e evidencia
   esperada.
8. Para `must_ask_now`, fazer uma pergunta por turno, priorizando a que mais
   bloqueia o plano. Nao listar varias perguntas como substituto da entrevista
   quando uma decisao bloqueante estiver ativa.
9. Atualizar o registro transitorio autorizado, se houver destino exato.
10. Encerrar com `ready_for_next_phase: true` somente quando nao houver
    `must_ask_now` sem resposta.

## Validators

- Toda pergunta tem categoria, fonte, impacto no plano e motivo para perguntar
  ou nao perguntar.
- Nenhuma pergunta `must_ask_now` e respondida por inferencia sem evidencia ou
  decisao humana registrada.
- Nenhuma pergunta `do_not_ask_llm_can_determine` e enviada ao humano antes de
  tentar a leitura local minima.
- Toda pendencia `can_delegate_to_plan` declara task, owner provavel, validator
  ou stop condition.
- Toda pendencia `can_validate_later` declara gate humano e evidencia esperada.
- `ready_for_next_phase` e `false` se houver `must_ask_now` sem resposta.
- Pesquisa externa foi omitida com motivo ou executada apenas apos consentimento
  explicito para a frase da busca.

## Human Gates

- `interview` para cada decisao `must_ask_now`.
- `approval` para qualquer registro transitorio escrito fora de um destino ja
  aprovado pelo workflow chamador.
- `research-consent` quando a classificacao depender de fonte externa atual.
- `human-validation` para comportamento perceptivel, runtime, integracoes,
  estado persistido ou output gerado.
- `technical-review` quando a preflight alterar politica, command, skill,
  agent, template, validator ou doc consolidado.

## Packaging Checks

- O comando usa namespace `loki:` e possui wrapper `skills/loki-human-decision-preflight`.
- `manifest.yaml` e `install-scopes.json` devem registrar o comando e a skill
  quando o artefato for adicionado ao conjunto instalavel.
- Validar estrutura com `python3 scripts/validate-install-scopes.py`.

## Stop Conditions

- Entrada minima ausente ou fonte principal nao localizada.
- Destino transitorio solicitado nao foi aprovado.
- Existe decisao `must_ask_now` sem resposta.
- A resposta depende de pesquisa externa e o usuario nao autorizou a busca.
- Ha conflito entre fonte local e resposta humana que muda escopo ou aceite.
- A proxima etapa exigiria escrita sensivel sem plano, validator e gate.

## Resume Contract

Registrar fonte analisada, destino transitorio, perguntas por categoria,
respostas humanas, fontes consultadas, research gate, proxima pergunta ativa,
status `ready_for_next_phase`, pendencias delegadas ao plano, validators, gates
e proximo comando recomendado.
