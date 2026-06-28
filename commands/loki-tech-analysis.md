---
name: loki:tech-analysis
type: command
status: draft
domain: spec-driven
required_skills:
  - loki-tech-analysis-authoring
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - architecture or security risk
    - conflicting multi-source evidence
    - irreversible or high-impact recommendation
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

# loki:tech-analysis

## Purpose

Produzir analise tecnica baseada em evidencias antes de plano ou execucao,
separando escopo, fontes, fatos, hipoteses, superficies afetadas, decisoes,
riscos, validators, gates humanos e handoff para planejamento.

## Inputs

- Brief, PRD, NSD, feedback ou pedido direto.
- Caminhos de fonte no projeto.
- Escopo permitido, fora de escopo e superficies proibidas.
- Decisoes humanas, assumptions, standards ou tasks relacionadas quando existirem.
- Documentacao duradoura do consumidor quando for relevante para o escopo.

## Outputs

- Analise tecnica Markdown usando `templates/technical-analysis-template.md`.
- Mapa de fontes, fatos, inferencias, hipoteses e perguntas abertas.
- Lista de arquivos, superficies runtime, pontos de integracao, contratos de
  estado, validators, gates humanos e docs possivelmente afetados.
- Resultado do research gate: nao necessario, pulado com motivo ou realizado com
  fontes citadas.
- Recomendacao de plano, investigacao adicional ou bloqueio.

## Allowed Writes

- Arquivos Markdown de analise no plano ativo.
- `interaction/faseN/` quando houver pergunta humana.

## Forbidden Writes

- Runtime, engine, framework ou superficies sensiveis do consumidor fora do escopo aprovado.
- `.claude/**` e `.agents/**`.
- Docs consolidados sem task de promocao.

## Required Skills

- `loki-tech-analysis-authoring` para contrato de evidencia, pesquisa,
  matriz de decisao, validators e handoff.
- `loki-index-navigator` quando a analise depender de documentacao duradoura em
  `/docs` do consumidor.
- `<technology_required_skills>` por pedido do usuario, contexto detectado ou
  retrospectiva que tenha criado ou indicado skill especializada aprovada.

## Handoffs

- `source-researcher` em modo read-only quando a analise precisar mapear fatos,
  lacunas e conflitos entre varias fontes antes da matriz de decisao. Use quando
  o contexto for ruidoso, as fontes forem desconhecidas, houver pesquisa externa
  aprovada ou quando uma hipotese material exigir evidencia alem de 1-2 leituras
  locais simples.
- `bibliotecario` em modo read-only quando a documentacao duradoura do
  consumidor exigir navegacao por `docs/index.xml`. Pode rodar em paralelo com
  a analise tecnica quando a pergunta documental for independente.
- `technical-implementer` em modo proposal-only quando uma superficie tecnica
  exigir proposta de abordagem sem escrita direta. Pode rodar em paralelo com
  `runtime-qa` depois que superficies ou hipoteses tecnicas forem conhecidas.
- `runtime-qa` em modo proposal-only quando os validators ou gates humanos
  precisarem de checklist especializado. Pode rodar em paralelo com
  `technical-implementer`, retornando apenas checklist, riscos e gate humano.

Quando mais de um handoff `read-only` ou `proposal-only` for aplicavel, acionar
em paralelo apenas entradas independentes e consolidar fontes, riscos, conflitos
e gates antes da matriz de decisao. O `source-researcher` nao escolhe solucao;
ele entrega evidencia para a analise.

## Workflow

1. Confirmar objetivo, insumos, escopo, fora de escopo, destino do artefato e
   forbidden writes.
2. Carregar `loki-tech-analysis-authoring` e qualquer skill tecnica exigida
   pelo contexto. Nao tornar skills de tecnologia obrigatorias por default.
3. Ler instrucoes de roteamento do consumidor quando entrar em um projeto
   (`AGENTS.md`, `CLAUDE.md` ou equivalente).
4. Mapear fontes locais primarias antes de docs interpretativos: arquivos alvo,
   configuracao runtime, schemas, IDs, contratos, dados gerados ou pontos de
   integracao.
5. Separar fatos, inferencias, hipoteses e perguntas abertas. Para cada
   hipotese material, fazer 1-2 leituras ou buscas locais que possam confirmar
   ou rejeitar a causa antes de escrever recomendacao.
6. Aplicar o research gate somente depois do mapeamento local:
   - pesquisar externamente se o usuario pedir ou se a decisao depender de
     documentacao atual de biblioteca, framework, engine, API, plugin,
     seguranca, licenca ou compatibilidade;
   - preferir docs oficiais, repositorios primarios, release notes ou provedor
     atual de documentacao disponivel no ambiente;
   - registrar fonte, versao/data quando relevante, fato extraido e impacto;
   - nao deixar pesquisa externa substituir o estado local do consumidor.
7. Comparar alternativas em matriz: abordagem local/nativa, dependencia ou
   plugin/framework, implementacao customizada, defer ou bloqueio.
8. Declarar superficies afetadas, pontos de integracao, contratos de estado,
   validators, gates humanos, riscos, docs afetados e recomendacao.
9. Escrever a analise com `templates/technical-analysis-template.md`.
10. Rodar validators antes de recomendar `loki:generate-action-plan`.

## Validators

- Toda recomendacao tem fonte, cadeia de inferencia ou assumption explicita.
- Hipoteses nao confirmadas estao marcadas e nao aparecem como fatos.
- Superficies afetadas, forbidden writes, validators e gates humanos estao
  declarados.
- Pesquisa externa foi realizada com fontes citadas ou pulada com motivo.
- Fontes externas nao substituem evidencias locais do consumidor.
- A analise e suficiente para alimentar `loki:generate-action-plan` sem memoria
  da conversa.
- Mudancas no proprio pacote declaram impacto em `manifest.yaml`, docs,
  templates ou skills quando aplicavel.

## Human Gates

- `interview` para lacunas de requisito.
- `technical-review` quando a analise alterar politica ou contrato.
- `human-validation` apenas como gate recomendado para execucoes futuras que afetem comportamento perceptivel, runtime, integracoes ou estado persistido.

## Packaging Checks

- Se a analise revisar command, skill, agent, template, validator ou doc
  consolidado do pacote, aplicar as regras de autoria e autocontencao
  disponiveis.
- Atualizar `manifest.yaml` apenas quando artefatos forem adicionados, removidos,
  renomeados ou movidos no pacote.
- Validar que referencias normativas do pacote continuam internas ao package
  root.

## Stop Conditions

- Fonte minima insuficiente.
- Pedido exige implementar antes de aprovar escopo.
- Risco blocker sem alternativa segura.
- Pesquisa externa revela conflito sem validator ou decisao humana possivel.
- Nao e possivel definir validators ou gates humanos para as superficies
  afetadas.

## Resume Contract

Salvar status, fontes lidas, research gate, fatos, hipoteses, riscos,
perguntas abertas, validators, gates humanos e proximo passo no artefato de
analise.
