---
name: lf-command-creator
description: Use ao criar, revisar ou migrar workflows invocáveis Goose/Loki com entradas, saídas, gates, write boundaries, handoffs, validações e estado retomável; trate command bundles/recipes como orquestradores e separe Input, Execution e Response.
---

# lf-command-creator

## Quando usar

Use esta skill quando a tarefa for criar, revisar ou migrar um command Loki, Goose Recipe, subrecipe ou workflow invocável equivalente.

Use também quando houver dúvida se uma melhoria deve virar command/recipe, skill, custom agent, template, validator, documentação normativa ou backlog.

## Procedimento essencial

1. Classifique a necessidade:
   - `command`/recipe quando o valor principal for orquestrar um fluxo com estado, gates, outputs e handoffs.
   - `skill` quando o valor for conhecimento especializado reutilizável, sem orquestração completa.
   - `custom agent` quando houver papel especialista com julgamento próprio, isolamento de contexto ou contrato de escrita/leitura.
   - `template` quando o valor principal for formato de saída repetível.
2. Modele todo command/recipe em três fases:
   - `Input`: coleta, valida e normaliza parâmetros; no Goose isso pertence principalmente ao `Initial Prompt` e `Parameters`.
   - `Execution`: interpreta a solicitação, monta plano, chama skills/agentes/subrecipes, controla gates e preserva escrita serializada; no Goose isso pertence a `Instructions`.
   - `Response`: produz saída para o consumidor correto: humano, LLM ou ambos.
3. Defina contrato mínimo: propósito, entradas, outputs, allowed writes, forbidden writes, gates humanos, validators, stop conditions, handoffs e resume state.
4. Se houver escrita no projeto, prefira delegar para um Write Agent apropriado. Se o command/recipe precisar escrever diretamente por ausência de agente especializado, registre essa exceção e a oportunidade de criar um Write Agent.
5. Antes de propor mudança em artefato duradouro do Loki Framework, verifique destino correto, impacto em docs/manifest, regras de autoria do pacote e gates `technical-review` + `approval`.
6. Não copie frontmatter Loki/Codex/Claude literalmente para Goose. Traduza semântica para campos Goose: Title, Description, Instructions, Initial Prompt, Activities, Parameters, Extensions, Response e Subrecipes.
7. Preserve write boundaries e stop conditions de forma explícita nas Instructions.
8. Para resposta longa editorial em Markdown, deixe `response.json_schema` vazio.

## Validação

- O workflow tem início, fim e critério de conclusão claros.
- As três fases Input/Execution/Response estão reconhecíveis.
- Escritas sensíveis têm owner único, escopo aprovado, gate e validator.
- Handoffs têm entrada, saída e destino definidos.
- O formato de resposta corresponde ao consumidor.
- A solução não transforma skill em mini-orquestrador nem agent em checklist procedural longo.

## Limites

- Não editar root `skills/**`, root `agents/**`, `manifest.yaml`, `.agents/**`, `.codex/**` ou `.claude/**` sem autorização explícita.
- Não usar artefatos transitórios como fonte normativa final.
