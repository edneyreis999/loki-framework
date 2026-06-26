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

Investigar feedback de usuario, QA ou validacao humana por entrevista curta, uma pergunta por vez, ate obter diagnostico suficiente para propor proximos passos.

## Inputs

- Feedback bruto do usuario.
- Contexto de feature, fluxo, integracao, UI, audio, estado runtime ou comportamento observado.
- Artefatos existentes de plano, validation ou interaction quando houver.

## Outputs

- Diagnostico resumido.
- Perguntas e respostas registraveis em `interaction/faseN/`.
- Proposta de correcao ou investigacao, sem aplicar escrita automaticamente.
- Resultado do research gate: nao necessario, recusado, aprovado com query, ou realizado com fontes citadas.

## Allowed Writes

- Markdown do plano ativo em `interaction/faseN/`.
- Resumo de diagnostico no plano ativo, quando solicitado.

## Forbidden Writes

- Superficies sensiveis do consumidor declaradas por plano, skill tecnica ou contexto (`<sensitive_write_patterns>`).
- Artefatos de runtime, engine ou framework sem approval.
- `.claude/**`
- `.agents/**`

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
10. Propor correcao ou investigacao apenas quando nao houver duvida critica pendente.

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
  `runtime-qa` quando a superficie provavel ja estiver identificada.

Paralelismo nao substitui a regra de uma pergunta por turno: se houver
ambiguidade critica, resolver a entrevista antes de acionar handoffs paralelos.

## Stop Conditions

- O usuario nao consegue confirmar o comportamento observado.
- A proxima acao exigiria escrita sensivel sem approval.
- Ha conflito entre evidencias e feedback.
- A recomendacao depende de pesquisa externa, o usuario nao autoriza a busca proposta e nao ha evidencia local suficiente.

## Resume Contract

Registrar pergunta ativa, resposta humana, query de pesquisa proposta, consentimento de pesquisa, fontes externas aprovadas, status e proximo passo em `interaction/faseN/<task>-feedback.md`.
