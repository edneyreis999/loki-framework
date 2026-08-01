---
title: Catalogo de Contexto do Projeto Consumidor
type: consumer-context-contract
status: draft
created: 2026-06-25
self_contained: true
---

# Catalogo de Contexto do Projeto Consumidor

## Objetivo

No Loki, a memoria duradoura de negocio do projeto consumidor nao deve morar no
pacote. Ela deve morar em `/docs`, com `docs/index.xml` como catalogo
navegavel para LLMs.

Esta camada substitui a funcao util da `.context/` library do framework de
referencia sem copiar sua estrutura literalmente.

## Superficies Duradouras do Consumidor

- `docs/**/*.md`: verdade de negocio, lore, fluxo funcional, termos, regras
  especificas e contexto factual do software ou jogo.
- `docs/loki-init/**`: documentacao inicial produzida por `loki-init`,
  incluindo inventario comum, contexto de tecnologia, perguntas abertas e
  conflitos materializados pelo `catalogador` a partir de packets validados.
- `docs/index.xml`: catalogo navegavel por maquina que ajuda a localizar os
  documentos certos com baixo custo de contexto.
- `AGENTS.md`: instrucoes project-wide e roteamento minimo para dizer quando a
  LLM deve consultar `/docs`.
- `CLAUDE.md` ou equivalente: regras do adaptador e roteamento minimo
  especifico da ferramenta.

## Responsabilidades

- `standards-curator`: decide se o aprendizado vai para o pacote Loki ou para o
  contexto duradouro do consumidor.
- `retrospective-digester`: extrai candidatos `project-specific` de
  retrospectivas tecnicas para o orquestrador, sem escrever `/docs` nem decidir
  promocao final.
- `catalogador`: escreve ou revisa a documentacao duradoura do consumidor e
  mantem `docs/index.xml` coerente.
- `bibliotecario`: consulta o catalogo e recomenda a menor leitura suficiente.
- `source-researcher`: identifica lacunas, conflitos e evidencias multi-fonte
  que podem exigir documentacao duradoura, sem escrever ou promover contexto por
  conta propria.
- `lf-index-navigator`: procedimento tecnico para navegar no catalogo XML.

Quando `loki-continuous-improvement` recebe um plano completo, somente
candidatos com `scope: consumer` e destination de consumer docs entram nesta
integração. A recuperação usa `bibliotecario` a partir de `docs/index.xml`, e a
escrita continua exclusiva do `catalogador` em envelope
`task_scoped_writer`. O package usa outro root, outro catálogo e outro
librarian; nunca cria `docs/index.xml` no pacote.

Investigadores de dominio produzem `loki_init_research_packet` schema v1 com
fontes, sem escrever docs. O orquestrador valida cobertura, organiza lotes e
preserva continuacao; o `catalogador` materializa bootstrap, lotes e
reconciliacao final serialmente. Se estiver indisponivel, a escrita bloqueia:
nao existe writer alternativo para documentacao do consumidor.

## Regra de Promocao

O fluxo completo de captura, retrospectiva, classificacao e promocao esta em
[Workflow de Aprendizado do Loki](loki-learning-workflow.md). Esta secao cobre
apenas o destino de contexto duradouro do projeto consumidor.

- Conhecimento classificado para o package vai para command bundle em
  `skills/loki-*/`, skill reutilizavel, `agents/`, `templates/`, `docs/` ou
  validators do pacote Loki.
- Conhecimento classificado para consumer docs vai para `docs/**/*.md` do consumidor e deve
  atualizar `docs/index.xml`.
- `AGENTS.md` e `CLAUDE.md` do consumidor recebem apenas o minimo necessario
  para orientar navegacao e comportamento. Eles nao devem duplicar a regra de
  negocio inteira.

## Contrato de `docs/index.xml`

Use `templates/project-doc-index-template.xml` como base quando o catalogo ainda
nao existir.

Campos minimos esperados por documento:

- `path`
- `type`
- `priority`
- `summary`
- `use_when`
- `not_covered`
- `keywords`
- `sections` com `anchor`, `tokens` e `purpose`

Campos de descoberta usados para decidir leitura (`summary`, `use_when`,
`not_covered`, `keywords/keyword` e `sections/@purpose`) devem ser
self-contained em cold start. Eles precisam descrever o conteudo duradouro e
quando ler o documento sem depender de IDs transitorios de plano, CI, task,
build, delegacao ou run local. IDs estaveis de dominio, documento, path,
anchor ou fonte versionada podem aparecer quando vierem acompanhados de
descricao textual suficiente. IDs de packet, batch, run, invocation ou
handoff, assim como hashes, idempotency keys e revisions operacionais, nao sao
chaves obrigatorias do indice nem substituem as chaves human-semantic de
descoberta.

Exemplo minimo:

```xml
<documentation-catalog version="1.0">
  <metadata>
    <scope>project-docs</scope>
    <summary>Catalogo navegavel do projeto consumidor.</summary>
    <owner>catalogador</owner>
    <updated_at>YYYY-MM-DD</updated_at>
  </metadata>
  <documents>
    <document id="doc-001" path="docs/domain/example.md" type="domain-rule" priority="high">
      <summary>Regra de dominio para validar pedidos antes de alterar o fluxo principal.</summary>
      <use_when>Use ao revisar comportamento de pedidos, validacao de entrada ou condicoes de bloqueio do fluxo principal.</use_when>
      <not_covered>Nao cobre integracoes externas, layout de interface ou validacao runtime.</not_covered>
      <keywords>
        <keyword>pedido validacao dominio</keyword>
      </keywords>
      <sections>
        <section anchor="overview" tokens="120" purpose="Resumo da regra de dominio e dos casos em que ela bloqueia o fluxo principal." />
      </sections>
    </document>
  </documents>
</documentation-catalog>
```

## Guardrails

- Nenhum arquivo normativo do pacote Loki deve guardar fato, lore, nomenclatura
  funcional ou regra de negocio especifica do projeto consumidor.
- O pacote pode orientar aplicacao em `/docs`, `AGENTS.md` e `CLAUDE.md` do
  consumidor, mas esses arquivos sao destinos de aplicacao, nao fontes
  normativas do pacote.
- Se um documento duradouro novo for criado em `/docs`, `docs/index.xml` deve
  ser atualizado na mesma promocao.
- Somente `catalogador` materializa docs duradouros do consumidor. Docs do
  proprio pacote sao uma superficie distinta sob `framework-artifact-writer`
  dentro do package root.
