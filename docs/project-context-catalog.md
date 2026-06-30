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
- `docs/loki-init/**`: documentacao inicial produzida por `loki:init`,
  incluindo inventario comum, contexto de tecnologia, documentos por
  perspectiva, perguntas abertas e conflitos.
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
- `loki-index-navigator`: procedimento tecnico para navegar no catalogo XML.

## Regra de Promocao

O fluxo completo de captura, retrospectiva, classificacao e promocao esta em
[Workflow de Aprendizado do Loki](loki-learning-workflow.md). Esta secao cobre
apenas o destino de contexto duradouro do projeto consumidor.

- Aprendizado `universal` ou `probable-universal` vai para `commands/`,
  `skills/`, `agents/`, `templates/`, `docs/` ou validators do pacote Loki.
- Aprendizado `project-specific` vai para `docs/**/*.md` do consumidor e deve
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
      <summary>Resumo curto.</summary>
      <use_when>Quando a task precisar desta regra.</use_when>
      <not_covered>O que este documento nao cobre.</not_covered>
      <keywords>
        <keyword>example</keyword>
      </keywords>
      <sections>
        <section anchor="overview" tokens="120" purpose="Visao geral." />
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
