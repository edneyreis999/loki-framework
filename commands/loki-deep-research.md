---
name: loki:deep-research
type: command
status: draft
domain: research
required_skills:
  - lf-web-deep-research
required_commands: []
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
  adapter_projection:
    codex: "Advisory unless projected through config, profile or custom agent."
    claude_code: "May map to model/effort frontmatter where supported."
---

# loki:deep-research

## Purpose

Conduzir pesquisa profunda na internet com metodologia explicita, fontes
citadas, verificacao cruzada, mapa de contradicoes, assumptions marcadas e
handoff reutilizavel para analise tecnica, planejamento, decisao humana ou
documentacao.

## Inputs

- Pergunta de pesquisa, tese, decisao ou tema.
- Escopo, fora de escopo, profundidade esperada e prazo.
- Tipos de fonte preferidos ou proibidos, como docs oficiais, artigos
  academicos, repositorios primarios, noticias, foruns ou concorrentes.
- Destino do resultado, quando houver arquivo aprovado.
- Restricoes de idioma, periodo, geografia, dominio, seguranca ou compliance.

## Outputs

- Relatorio Markdown de deep research.
- Metodologia: objetivo, queries, filtros, fontes buscadas, fontes lidas,
  criterios de credibilidade e limitacoes.
- Achados classificados como fato, evidencia, inferencia, contradicao,
  assumption ou lacuna.
- Tabela de fontes com URL, data de acesso, data/publicacao quando relevante,
  tipo, credibilidade e uso no relatorio.
- Mapa de consenso, divergencias e pontos que exigem decisao humana ou pesquisa
  adicional.
- Recomendacao de proximo passo: `loki:tech-analysis`,
  `loki:human-decision-preflight`, `loki:generate-action-plan`,
  documentacao, backlog ou bloqueio.

## Allowed Writes

- Arquivo Markdown transitorio de pesquisa no plano ativo, quando o usuario
  pedir arquivo ou houver destino aprovado.
- `interaction/faseN/` para registrar pergunta, decisao ou aprovacao humana
  quando o comando estiver dentro de um plano Loki.

## Forbidden Writes

- Runtime, codigo, assets, configuracao, dados gerados ou superficies sensiveis
  do consumidor.
- `.claude/**`, `.agents/**` e `.codex/**`.
- Docs consolidados do consumidor, `AGENTS.md` ou `CLAUDE.md` sem tarefa de
  promocao posterior e approval apropriado.
- Mudancas em commands, skills, agents, templates, docs ou `manifest.yaml` do
  pacote Loki.

## Required Skills

- `lf-web-deep-research` para metodo de pesquisa web, verificacao cruzada,
  credibilidade, citacoes, contradicoes e formato de saida.
- `lf-index-navigator` quando o resultado precisar considerar documentacao
  duradoura local do consumidor antes de pesquisar externamente.
- `<technology_required_skills>` quando a pergunta envolver tecnologia,
  framework, API, seguranca, licenca ou dominio especializado.

## Handoffs

- `source-researcher` em modo read-only e paralelo e o mecanismo padrao de
  pesquisa para `deep` e `deeper`: o orquestrador deve dividir a pergunta em
  trilhas independentes e invocar um agente por trilha, fonte ou subpergunta.
  A main thread nao deve carregar conteudo bruto de paginas quando um agente
  puder ler e devolver apenas `source_research` compacto.
- Para `quick` e `standard`, usar `source-researcher` quando houver muitas
  fontes, contradicoes materiais, comparacao entre fontes locais e web, ou
  coleta paralelizavel por subperguntas independentes. Se a main thread fizer
  a pesquisa diretamente, deve justificar no relatorio por que o fan-out nao era
  necessario.
- `bibliotecario` em modo read-only quando a pesquisa precisar primeiro localizar
  documentacao duradoura do consumidor via `docs/index.xml`.
- `standards-curator` em modo proposal-only somente quando o resultado indicar
  possivel promocao de regra duradoura, padrao ou politica.

Handoffs paralelos podem ser usados apenas para trilhas independentes. Cada
agente deve receber um envelope com pergunta, queries/filtros permitidos, fontes
permitidas/proibidas, profundidade, limites de tokens e formato `source_research`.
A consolidacao final deve eliminar duplicatas, preservar divergencias e declarar
incerteza em vez de fabricar consenso.

## Workflow

1. Confirmar pergunta, escopo, fora de escopo, profundidade, destino, fontes
   preferidas/proibidas e restricoes.
2. Carregar `lf-web-deep-research` e qualquer skill especializada exigida pelo
   dominio.
3. Se a decisao depender do estado local do consumidor, ler primeiro fontes
   locais minimas; a web nao substitui o estado real do projeto.
4. Criar plano multiagentico de pesquisa com subperguntas, criterios de fonte,
   estrategia de busca e `agent_research_plan`. Para escopo amplo, confirmar ou
   reduzir o plano antes de pesquisas caras.
5. Para `deep` e `deeper`, despachar uma instancia de `source-researcher` por
   trilha independente. Para `quick` e `standard`, despachar agentes quando o
   custo de contexto de leitura na main thread for maior que o handoff compacto.
6. Limitar a main thread a plano, contratos dos agentes, handoffs compactos,
   consolidacao e decisao de proximo passo. Conteudo bruto, paginas longas e
   listas extensas ficam dentro dos agentes.
7. Executar busca em ondas pelos agentes: descoberta ampla, refinamento por
   fontes primarias, leitura profunda de fontes selecionadas e verificacao
   cruzada.
8. Consolidar `source_research` de cada agente, registrando queries, filtros,
   fontes rejeitadas relevantes, datas e motivos de confianca ou exclusao.
9. Separar fato, evidencia, inferencia, assumption, lacuna e contradicao.
10. Comparar fontes por autoridade, atualidade, proximidade da fonte primaria,
    independencia e conflito de interesse.
11. Produzir sintese com conclusoes proporcionais a evidencia, sem extrapolar
    para implementacao quando a pergunta era apenas pesquisa.
12. Declarar proximos passos, validators, decisoes humanas pendentes e limites.

## Validators

- A pergunta de pesquisa e o escopo estao visiveis no relatorio.
- Para `deep` e `deeper`, existe `agent_research_plan` e ao menos um
  `source_research` por trilha independente, ou ha stop condition explicita.
- A main thread consolidou handoffs compactos e nao ingeriu conteudo bruto longo
  que poderia ter ficado isolado em agente.
- Queries, filtros, fontes lidas e datas relevantes foram registradas.
- Cada achado material tem fonte citada ou esta marcado como inferencia,
  assumption ou lacuna.
- Pelo menos duas fontes independentes sustentam alegacoes materiais, ou a
  limitacao esta declarada.
- Fontes primarias foram preferidas quando disponiveis.
- Contradicoes e conflitos de evidencia foram preservados, nao suavizados.
- O relatorio nao recomenda implementacao sem indicar `loki:tech-analysis` ou
  plano posterior quando necessario.
- Pesquisa externa nao sobrescreve fatos locais do consumidor.

## Human Gates

- `interview` quando a pergunta, escopo ou destino estiverem ambiguuos.
- `approval` antes de pesquisa longa, cara, com ferramentas pagas, login,
  automacao agressiva, scraping sensivel ou coleta de dados pessoais.
- `technical-review` quando a pesquisa recomendar mudanca duradoura em artefato
  do pacote Loki ou politica de projeto.
- `human-validation` quando o resultado envolver comportamento perceptivel,
  integracoes ativas, compliance ou decisao de negocio relevante.

## Packaging Checks

- Se o resultado recomendar mudar o pacote Loki, encaminhar para
  `loki:knowledge-extraction-analysis` ou `loki:continuous-improvement`; este
  comando nao aplica mudanca duradoura diretamente.
- Nao registrar fontes externas como dependencias normativas do pacote; elas sao
  evidencia citada.

## Stop Conditions

- Pergunta ampla demais para produzir resposta verificavel sem recorte.
- Pesquisa depende de acesso, login, ferramenta paga ou scraping sensivel sem
  approval.
- Fontes confiaveis minimas nao foram encontradas.
- Fontes materiais entram em conflito e nao ha criterio suficiente para
  resolver ou escalar.
- O pedido exige escrita tecnica, promocao normativa ou decisao de alto risco
  antes de concluir a pesquisa.

## Resume Contract

Registrar pergunta, escopo, profundidade, `agent_research_plan`, agentes
acionados, subperguntas, queries, fontes lidas e rejeitadas, handoffs
`source_research`, achados, contradicoes, lacunas, assumptions, decisoes
pendentes, validators, gates e proximo comando recomendado.
