---
name: loki-feedback
description: Run the Loki `loki:feedback` command workflow in Codex. Diagnose software or game project feedback through a strict one-question-at-a-time interview before proposing any fix; use when the user reports validation feedback, visual bugs, gameplay or product feel, UX problems, audio/input issues, unexpected runtime behavior, integration symptoms, or other observed symptoms.
type: skill
status: draft
used_by:
  - loki:feedback
---

# loki-feedback

## When To Use

Use quando o usuario trouxer feedback, bug visual, validacao humana, sensacao de gameplay ou produto, problema de UX, audio, input, integracao, estado de runtime ou comportamento inesperado.

## Procedure

1. Resuma o sintoma em uma frase.
2. Normalize o feedback em acao disparadora, comportamento observado, comportamento esperado e condicoes.
3. Marque campos ausentes como duvidas pendentes.
4. Faca uma pergunta por vez.
5. Diferencie observacao, expectativa e contexto.
6. Identifique superficie provavel: runtime, configuration/data, integration code, content/assets, UI/UX surfaces, docs/process, audio/input ou narrativa.
7. Leia apenas fontes locais necessarias e permitidas para confirmar ou rejeitar hipoteses materiais.
8. Se informacao externa atual for material, proponha a frase exata da busca e peca consentimento antes de pesquisar.
9. Nao pesquise na internet sem consentimento explicito para a frase apresentada.
10. Proponha diagnostico e proximo passo sem aplicar escrita, somente quando nao houver duvida critica pendente.

## External Research Consent

Pesquisa externa e opcional. Use apenas quando o diagnostico depender de
versao, engine, plugin, API, biblioteca, compatibilidade, bug conhecido,
seguranca, licenca ou documentacao oficial atual.

Quando precisar pesquisar, faca a pergunta em turno proprio:

```markdown
Posso pesquisar na internet por: "<frase exata da busca>"?
```

Se o usuario recusar, continue com evidencias locais quando isso ainda for
suficiente. Se a recomendacao depender da pesquisa recusada, registre a lacuna
como risco, pergunta aberta ou stop condition.

## Inputs

- Feedback bruto.
- Caminho ou feature relacionada.
- Evidencia do usuario quando houver.

## Outputs

- Diagnostico.
- Perguntas e respostas.
- Proposta de proximo passo.
- Gates necessarios.
- Query de pesquisa proposta, consentimento e fontes citadas quando pesquisa externa for aprovada.

## Limits

- Nao simula confirmacao humana.
- Nao declara validacao humana como aprovada.
- Nao escreve no consumer runtime/engine/framework.
- Nao pesquisa na internet sem apresentar a frase exata da busca e receber consentimento explicito.

## Required Gates

- `interview` ate remover ambiguidade critica.
- `research-consent` quando contexto externo atual for material para o diagnostico ou proposta.
- `human-validation` quando a validacao depender de comportamento perceptivel, estado de runtime, integracoes ou superficies especificas da tecnologia usada.
