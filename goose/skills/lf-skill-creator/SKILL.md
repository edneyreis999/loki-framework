---
name: lf-skill-creator
description: Use ao criar, revisar ou migrar skills Goose-native; mantém SKILL.md conciso, separa referências longas e garante que skill seja conhecimento especializado reutilizável, não orquestrador completo.
---

# lf-skill-creator

## Quando usar

Use quando a necessidade for encapsular conhecimento especializado reutilizável: procedimento técnico, critérios de validação, heurísticas de autoria, uso de ferramenta ou regra de formato aplicável em mais de um workflow.

## Procedimento essencial

1. Confirme que a necessidade pertence a uma skill:
   - skill ensina como executar uma capacidade;
   - command/recipe orquestra fluxo com estado e gates;
   - custom agent exerce papel especialista com julgamento próprio.
2. Use layout Goose-native:
   ```text
   goose/skills/<skill-name>/SKILL.md
   goose/skills/<skill-name>/references/   # somente quando necessário
   ```
3. O frontmatter de `SKILL.md` deve conter `name` e `description` com gatilho claro.
4. Mantenha `SKILL.md` objetivo: propósito, quando usar, procedimento essencial, validações e limites.
5. Coloque exemplos extensos, templates, scripts, notas de plataforma e material condicional em `references/` somente quando forem necessários.
6. Evite duplicar longas instruções de recipe dentro da skill; a skill deve ser reutilizável e carregável sob demanda.
7. Ao migrar de Loki/Codex/Claude, remova metadados específicos de adaptador que não tenham efeito no Goose e preserve apenas comportamento procedural.

## Validação

- Diretório próprio com `SKILL.md`.
- `name` e `description` existem e descrevem o gatilho.
- A skill não orquestra múltiplos agentes como função principal.
- Detalhes longos foram movidos para referências quando necessário.
- O guia de migração documenta se a skill precisa instalação/sincronização para diretórios de descoberta do Goose.

## Limites

- Não gravar skills Goose-native em root `skills/**`, `.agents/**`, `.codex/**` ou `.claude/**`.
- Não criar supporting files sem necessidade concreta.
