---
name: loki:feedback
type: command
status: draft
domain: qa-feedback
required_skills:
  - loki-feedback
execution_profile:
  model_class: generalist
  default_effort: medium
  max_effort: high
  escalation_signals:
    - external research is required
    - evidence conflicts with user feedback
    - high-risk technical proposal
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: low
    documentation_durable: high
    validator: medium
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:feedback

## Purpose

Investigar feedback de usuario, QA ou validacao humana por entrevista curta,
uma pergunta por vez, ate obter diagnostico suficiente para propor proximos
passos, sem aplicar alteracoes no projeto ou no pacote.

## Inputs

- Feedback bruto do usuario.
- Contexto de feature, fluxo, integracao, UI, audio, estado runtime ou comportamento observado.
- Artefatos existentes de plano, validation ou interaction quando houver.

## Outputs

- Diagnostico resumido.
- Perguntas e respostas para registro pelo orquestrador ou por retrospectiva
  tecnica posterior.
- Proposta de correcao, investigacao ou encaminhamento, sem aplicar escrita.
- Resultado do research gate: nao necessario, recusado, aprovado com query, ou realizado com fontes citadas.

## Allowed Writes

- Nenhuma por default.
- Excepcao unica: criar ou complementar um artefato de retrospectiva tecnica
  autorizado pelo workflow `loki:retrospectiva-tecnica`, quando o objetivo for
  registrar feedback, atrito, decisao humana, risco residual ou aprendizado para
  uma futura melhoria continua.

## Forbidden Writes

- Arquivos do plano ativo, task files, build evidence ou interaction records,
  salvo quando a execucao atual for explicitamente uma retrospectiva tecnica
  autorizada.
- Correcoes de codigo, configuracao, docs duradouros, comandos, skills,
  agentes, templates, validators, `manifest.yaml` ou `install-scopes.json`.
- Superficies sensiveis do consumidor declaradas por plano, skill tecnica ou contexto (`<sensitive_write_patterns>`).
- Artefatos de runtime, engine ou framework.
- `.claude/**`
- `.agents/**`
- `.codex/**`

## Gates

- `interview`: sempre que o feedback estiver ambiguo.
- `research-consent`: opcional; quando contexto externo atual for material, informar a frase exata da busca e pedir consentimento antes de pesquisar.
- `human-validation`: obrigatorio antes de declarar comportamento perceptivel, runtime, visual, audio, input, integracao ativa ou estado persistido como validado.

## Workflow

1. Carregar `loki-feedback`.
2. Normalizar o feedback em acao disparadora, comportamento observado, comportamento esperado e condicoes.
3. Marcar campos ausentes como duvidas pendentes.
4. Fazer uma pergunta por turno ate remover ambiguidade critica.
5. Ler apenas fontes locais necessarias e permitidas para confirmar ou rejeitar hipoteses materiais.
6. Acionar `research-consent` somente se informacao externa atual for necessaria para versao, engine, plugin, API, biblioteca, compatibilidade, bug conhecido, seguranca, licenca ou documentacao oficial.
7. Quando acionar `research-consent`, perguntar em turno proprio: `Posso pesquisar na internet por: "<frase exata da busca>"?`
8. Nao pesquisar na internet sem consentimento explicito do usuario para a frase apresentada.
9. Construir hipoteses com evidencia local, decisao humana ou fonte externa aprovada.
10. Propor correcao, investigacao, plano de acao, retrospectiva ou
    encaminhamento para outro comando apenas quando nao houver duvida critica
    pendente.
11. Nao aplicar a correcao proposta. Se o feedback revelar uma mudanca
    necessaria, encaminhar para o comando apropriado (`loki:tech-analysis`,
    `loki:generate-action-plan`, `loki:run-plan`,
    `loki:retrospectiva-tecnica` ou `loki:continuous-improvement`) em vez de
    editar diretamente.
12. Se for necessario registrar aprendizado operacional, criar ou complementar
    somente o artefato de retrospectiva tecnica autorizado; nao escrever em
    task, interaction, build ou fonte duradoura por conta do feedback.

## Handoffs

- `source-researcher` em modo read-only quando o feedback ja estiver
  normalizado e for necessario confirmar ou rejeitar hipoteses com fontes
  locais multiplas, documentacao duradoura ou pesquisa externa aprovada. Nao
  usar enquanto houver ambiguidade critica que ainda exige pergunta humana.
- `runtime-qa` em modo read-only para checklist e risco quando o feedback
  depender de comportamento em execucao. Depois que o feedback estiver
  normalizado e sem pergunta humana bloqueante, pode rodar em paralelo com a
  proposta tecnica.
- `technical-implementer` ou skill tecnica selecionada apenas como proposta
  quando houver possivel escrita sensivel. Pode rodar em paralelo com
  `runtime-qa` quando a superficie provavel ja estiver identificada, mas o
  `loki:feedback` nao aplica a proposta.
- `loki:retrospectiva-tecnica` quando o feedback e uma correcao operacional ou
  aprendizado que deve ficar registrado antes de melhoria continua. Neste caso,
  a unica escrita permitida e o artefato de retrospectiva tecnica autorizado.

Paralelismo nao substitui a regra de uma pergunta por turno: se houver
ambiguidade critica, resolver a entrevista antes de acionar handoffs paralelos.

## Stop Conditions

- O usuario nao consegue confirmar o comportamento observado.
- A proxima acao exigiria escrita sensivel sem approval.
- Ha conflito entre evidencias e feedback.
- A recomendacao depende de pesquisa externa, o usuario nao autoriza a busca proposta e nao ha evidencia local suficiente.
- O usuario pede para aplicar a correcao diretamente dentro de
  `loki:feedback`; encaminhar para o comando apropriado em vez de escrever.

## Resume Contract

Retornar ao usuario pergunta ativa, resposta humana, query de pesquisa proposta,
consentimento de pesquisa, fontes externas aprovadas, status e proximo passo.
Persistir esse registro apenas quando um artefato de retrospectiva tecnica
estiver autorizado pelo workflow `loki:retrospectiva-tecnica`.
