---
name: loki-index-navigator
description: Navigate consumer project documentation through `docs/index.xml` first, with `index.md` only as a legacy fallback. Use when `bibliotecario` needs low-cost discovery, when a workflow must inspect existing business docs before editing, or when a project keeps durable context in `/docs`.
type: skill
status: draft
used_by:
  - bibliotecario
  - catalogador
  - loki:continuous-improvement
---

# loki-index-navigator

## When To Use

Use esta skill quando a documentacao duradoura de um projeto consumidor morar
em `/docs` e houver um `docs/index.xml` servindo como catalogo navegavel.

Use tambem quando existir um legado com `index.md`; nesse caso, `index.md` e
apenas fallback, nao a superficie preferencial.

## Procedure

1. Comece procurando `docs/index.xml` no diretorio alvo ou no ancestral mais
   proximo dentro de `/docs`.
2. Se `docs/index.xml` existir, leia primeiro apenas os metadados de catalogo
   necessarios para navegar:
   - `metadata`
   - `document` com `path`, `type` e `priority`
   - `summary`
   - `use_when`
   - `not_covered`
   - `keywords`
   - `sections/section` com `anchor`, `tokens` e `purpose`
3. Se `docs/index.xml` nao existir, procure `index.md` apenas como fallback
   para projetos legados.
4. Escolha a menor leitura suficiente:
   - use uma secao quando o catalogo apontar ancora especifica;
   - use documento inteiro quando a pergunta exigir visao global ou varias
     secoes somarem a maior parte do arquivo.
5. Respeite o escopo do catalogo:
   - se `use_when` nao combinar, procure outro documento;
   - se `not_covered` excluir a pergunta, nao force leitura.
6. Quando a navegacao falhar por catalogo ausente, desatualizado ou ambiguo,
   devolva a lacuna ao orquestrador e recomende `catalogador`.
7. Responda apenas com base no que foi lido. Nao invente regra local nem infira
   contexto de negocio sem evidencia textual.

## Expected Output

- Lista curta de leituras recomendadas com caminho, alvo e motivo.
- Estimativa de custo quando `tokens` estiverem disponiveis no catalogo.
- Indicacao explicita de lacuna quando o catalogo nao suportar decisao segura.

## References

- Read [index-xml-contract.md](references/index-xml-contract.md) when parsing
  `docs/index.xml`, deciding required fields, or checking fallback behavior.

## Limits

- Nao abrir toda a arvore `/docs` por default.
- Nao tratar `AGENTS.md` ou `CLAUDE.md` como deposito principal de regra de
  negocio.
- Nao atualizar `docs/index.xml`; isso pertence ao `catalogador`.

## Required Gates

- Nenhum gate especial para leitura.
- Se a resposta depender de documento ainda nao catalogado, pare e devolva a
  lacuna.
