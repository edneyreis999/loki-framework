---
name: lf-agent-creator
description: Use ao criar, revisar ou migrar custom agents Goose/Loki; exige categoria explícita de agente, permissões, forbidden writes, handoff, validação, gates, stop conditions e formato de resposta.
---

# lf-agent-creator

## Quando usar

Use quando a unidade principal for um papel especialista com julgamento próprio, contexto isolado, responsabilidade de escrita escopada, validação independente ou saída proposal-only/read-only.

Use também para decidir entre agent, skill e command/recipe.

## Categorias obrigatórias

Todo agente deve declarar uma categoria operacional:

1. `write-agent`: implementa mudanças em código, documentação ou superfície aprovada dentro de envelope explícito.
2. `write-test-agent`: cria e persiste testes determinísticos, sem alterar produção, configuração ou documentação funcional.
3. `read-only-proposal-only-agent`: analisa, pesquisa, revisa ou propõe sem modificar arquivos.

## Procedimento essencial

1. Confirme que agente é a abstração correta: agent = quem julga; skill = como executar; command/recipe = o que orquestrar.
2. Defina responsabilidade estreita, entradas, outputs, allowed writes, forbidden writes, gates, stop conditions e formato de resposta.
3. Para `write-agent`, exija antes do início:
   - escopo aprovado;
   - arquivos/domínios permitidos;
   - destino de handoff;
   - validações esperadas;
   - instruções para testes determinísticos e validação manual no handoff.
4. Para `write-test-agent`, restrinja escrita a arquivos de teste e defina destino de sucesso e de falha antes do início.
5. Para `read-only-proposal-only-agent`, proíba escrita persistente e exija retorno estruturado com evidências, lacunas, confiança, riscos e próximo passo.
6. Agentes de escrita devem validar antes do handoff. Podem usar artefatos temporários em `planos/<plano>/builds/<fase>/`, mas devem removê-los salvo autorização explícita para preservar evidência transitória.
7. `write-agent` e `write-test-agent` devem registrar retrospectiva técnica antes do handoff quando o workflow exigir aprendizado ou evidência de execução.
8. Para agentes Goose-native, use Markdown com frontmatter mínimo `name`, opcional `description` e `model`, seguido de instruções de papel/comportamento.

## Validação

- Categoria declarada.
- Allowed/forbidden writes compatíveis com a categoria.
- Handoff de sucesso/falha definido antes da execução.
- Gates e stop conditions não dependem apenas de boa vontade do agente.
- O agente não acumula orquestração de command/recipe.

## Limites

- Não gerar agentes que escrevam fora do envelope aprovado.
- Não tratar Summon como destino final quando o objetivo for runtime Goose sem dependência Codex/Claude; crie/stage custom agent Goose-native em `goose/agents/**` quando o papel sobreviver.
