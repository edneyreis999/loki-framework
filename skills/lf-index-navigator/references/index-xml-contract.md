# index-xml-contract

`docs/index.xml` e o catalogo preferencial de documentacao duradoura do projeto
consumidor. Ele substitui o uso de `index.md` como superficie principal de
navegacao para contexto local.

## Required Structure

O documento deve seguir esta ideia minima:

```xml
<documentation-catalog version="1.0">
  <metadata>
    <scope>project-docs</scope>
    <summary>...</summary>
    <owner>catalogador</owner>
    <updated_at>YYYY-MM-DD</updated_at>
  </metadata>
  <documents>
    <document id="doc-001" path="docs/domain/example.md" type="domain-rule" priority="high">
      <summary>...</summary>
      <use_when>...</use_when>
      <not_covered>...</not_covered>
      <keywords>
        <keyword>example</keyword>
      </keywords>
      <sections>
        <section anchor="overview" tokens="120" purpose="..." />
      </sections>
    </document>
  </documents>
</documentation-catalog>
```

## Fields To Read First

- `document/@path`
- `document/@type`
- `document/@priority`
- `summary`
- `use_when`
- `not_covered`
- `keywords/keyword`
- `sections/section/@anchor`
- `sections/section/@tokens`
- `sections/section/@purpose`

Esses campos de descoberta devem ser compreensiveis em cold start:
`summary`, `use_when`, `not_covered`, `keywords/keyword` e
`sections/section/@purpose` precisam descrever o conteudo e o escopo duradouro
sem exigir memoria de IDs transitorios de plano, CI, task, build, delegacao ou
run local. IDs estaveis de dominio, documento, path, anchor ou fonte versionada
podem aparecer quando tambem houver descricao textual suficiente.

## Fallback Policy

- Preferir `docs/index.xml` sempre que existir.
- Usar `index.md` apenas em diretorios legados sem catalogo XML.
- Se ambos existirem e divergirem, `docs/index.xml` vence para navegacao do
  projeto consumidor.

## Catalog Quality Rules

- Todo documento duradouro novo em `/docs` deve aparecer no catalogo.
- Campos de descoberta do catalogo devem carregar significado proprio; nao use
  IDs transitorios como unica explicacao de `summary`, `use_when`,
  `not_covered`, `keywords` ou `purpose`.
- Se um documento mudar de escopo, `use_when`, `not_covered` e `sections`
  precisam ser revisados.
- `AGENTS.md` e `CLAUDE.md` podem apontar para o catalogo, mas nao substituem o
  catalogo.
