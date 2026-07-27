# Execution — loki-deep-research

## Purpose And Observable Contract

Este command e o orquestrador de pesquisa profunda na internet com metodologia,
fontes citadas, verificacao cruzada, contradicoes, assumptions e handoff para
analise, planejamento, decisao ou documentacao.

- Inicio: pergunta valida e entrada normalizada com escopo/custo resolvidos.
- Conclusao: relatorio proporcional a evidencia, handoffs terminais e gates
  resolvidos, ou stop condition explicita.
- Resultado verificavel: metodologia, achados classificados, fontes, consenso e
  divergencias, lacunas e proximo passo.
- Saidas obrigatorias: siga integralmente `references/response.md`.

## Execution Profile

```yaml
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - broad or ambiguous research scope
    - conflicting or weak external sources
    - high-stakes legal, medical, financial, security or compliance claims
    - expensive multi-lane or long-running web research
  handoff_effort:
    research: high
    documentation_transient: high
    documentation_durable: medium
    validator: medium
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha trilhas; selecione agentes;
forneca contexto autocontido; acompanhe handoffs ate terminal; aplique
validators/gates/approvals; consolide resultados sem fabricar consenso; e
mantenha responsabilidade pelo estado global depois de delegar.

## Allowed Writes

- Markdown transitorio de pesquisa no plano ativo quando pedido ou aprovado.
- `interaction/faseN/` para pergunta, decisao ou approval dentro de plano Loki.

## Forbidden Writes

- Runtime, codigo, assets, config, dados gerados ou `<sensitive_write_patterns>`.
- `.claude/**`, `.agents/**` e `.codex/**`.
- Docs consolidados, `AGENTS.md` ou `CLAUDE.md` sem promocao/approval posterior.
- Commands, skills, agents, templates, docs ou `manifest.yaml` do pacote.

## Required Skills And Commands

```yaml
required_skills:
  - lf-web-deep-research
required_commands: []
```

Carregue `lf-web-deep-research`. Carregue condicionalmente `lf-index-navigator`
quando docs duradouros locais precisarem contextualizar a web e
`<technology_required_skills>` quando o dominio exigir. Dependencias
condicionais nao se tornam obrigatorias para todo profile.

## Execution Planning And Replanning

Transforme a entrada em `agent_research_plan` com subperguntas, dependencias,
responsaveis, queries, fontes, validators e conclusao. Replaneje quando fonte,
acesso, contradicao, custo ou achado invalidar trilha posterior; confirme/reduza
escopo antes de pesquisa cara.

## Agents, Handoffs And Delegation

- `source-researcher`, read-only e paralelo, e padrao para cada trilha `deep` ou
  `deeper`; em `quick/standard`, use-o para muitas fontes, contradicoes ou alto
  custo de contexto. Justifique pesquisa direta quando aplicavel.
- `bibliotecario`, read-only, para localizar docs via `docs/index.xml`.
- `standards-curator`, proposal-only, para possivel promocao normativa.

Cada envelope inclui pergunta, objetivo, unidade, fatos/decisoes, queries e
fontes permitidas/proibidas, paths, profundidade/token limit, dependencias,
escopo, writes, criterios, validators/gates, formato `source_research` e destino.
Nao use contexto implicito. Registre origem, destino, objetivo, entrada,
resultado esperado, status, evidencia e proximo destino; acompanhe ate terminal.

Trilhas independentes podem rodar em paralelo; consolide serialmente, elimine
duplicatas e preserve divergencias.

## Workflow

1. Confirme pergunta, escopo, fora de escopo, profundidade, destino, fontes e
   restricoes.
2. Carregue `lf-web-deep-research` e skills especializadas.
3. Se depender do estado local, leia primeiro as fontes locais minimas.
4. Crie `agent_research_plan`; confirme/reduza escopo amplo antes de alto custo.
5. Para `deep/deeper`, despache `source-researcher` por trilha; para
   `quick/standard`, delegue quando contexto bruto exceder handoff compacto.
6. Limite main thread a plano, envelopes, handoffs, consolidacao e decisao.
7. Pesquise em ondas: descoberta, fontes primarias, leitura e cross-check.
8. Consolide queries, filtros, rejeicoes, datas e confianca/exclusao.
9. Separe fato, evidencia, inferencia, assumption, lacuna e contradicao.
10. Compare autoridade, atualidade, proximidade primaria, independencia e
    conflito de interesse.
11. Sintetize proporcionalmente; nao extrapole para implementacao.
12. Declare proximos passos, validators, decisoes e limites.

## Write Ownership And Serialization

Qualquer criacao/alteracao de relatorio deve ir a Write Agent apropriado com
target, writes, validators, gates, evidencias e handoff. Escrita direta so apos
registrar ausencia de Write Agent e assumir owner unico/envelope completo.
Serialize arquivos compartilhados e interrompa escopos sobrepostos.

Se escrever diretamente, registre no completion record tipo, motivo, lacuna de
agente, oportunidade/escopo futuro, evidencias e riscos; o orquestrador captura
evidence sanitizada ou declara gap, sem fallback de retrospectiva.

## Validators And Human Gates

- Pergunta/escopo visiveis; queries, filtros, fontes e datas registrados.
- `deep/deeper` tem plano e `source_research` por trilha ou stop condition.
- Main thread nao ingeriu bruto longo delegavel.
- Achados citados ou marcados; duas fontes independentes ou limitacao.
- Fontes primarias preferidas; contradicoes preservadas; fatos locais vencem web.
- Implementacao posterior aponta para `loki-tech-analysis`/plano.
- `interview` para pergunta/escopo/destino ambiguo.
- `approval` para pesquisa longa/cara/paga/login/scraping/dados pessoais.
- Para recomendação que possa mudar o pacote, registre somente candidato para
  futura `loki-continuous-improvement`; esta pesquisa não invoca Writer nem
  Auditor do pacote.
- `human-validation` para comportamento, integracao, compliance ou negocio.
- Pare quando validator/gate/approval falhar ou estiver pendente.

## Packaging Checks

Encaminhe mudanca do pacote para o workflow de extracao de conhecimento ou para
`loki-continuous-improvement`; nao aplique. Ambos podem estar instalados no
perfil consumer, mas qualquer mutacao de artefato consolidado do pacote continua
exigindo package root e envelope `destination_scope: package`. Um relatorio
transitorio preserva os targets do command de analise e nao concede mutacao.
Fontes externas sao evidencia citada, nunca dependencia normativa ou autorizacao.

## Stop Conditions

- Pergunta ampla sem recorte; acesso/login/pago/scraping sem approval; ausencia
  de fontes confiaveis; conflito irresoluvel; pedido exige escrita/promocao ou
  decisao de alto risco prematura.
- Entrada/permissao insuficiente, dependencia indisponivel, handoff sem destino,
  conflito de writers, validator falho ou gate/approval pendente.

## Evidence-First Cutover

Cada subagente devolve completion record; o orquestrador captura evidence
sanitizada após o handoff ou registra `partial`, `unavailable` ou `unsupported`.
Não registrar CoT privado nem invocar retrospectiva automaticamente.

## Resume Contract

Registre entrada, pergunta, escopo, profundidade, plano/agentes, subperguntas,
queries, fontes lidas/rejeitadas, handoffs, achados, contradicoes, lacunas,
assumptions, writes/owners, validators, gates, decisoes, riscos, etapas
concluidas, pendencias, proxima acao e condicao de retomada. Nao reinicie se o
estado permitir continuar.
