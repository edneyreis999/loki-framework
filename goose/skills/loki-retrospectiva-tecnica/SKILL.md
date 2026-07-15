---
name: loki-retrospectiva-tecnica
description: Produza retrospectivas técnicas Loki no Goose após fase concluída, pausa clara ou dificuldade resolvida, capturando evidências, validações, decisões humanas, atritos operacionais, aprendizados reutilizáveis, riscos residuais e candidatos para melhoria contínua sem promover regras diretamente.
---

# loki-retrospectiva-tecnica

## Quando usar

Use ao concluir ou pausar claramente uma fase, ou após resolver uma dificuldade real, quando outra LLM precisará retomar contexto com evidência auditável. Use também quando a execução consumiu mais ferramentas, buscas, scripts, tokens ou correções humanas do que deveria.

## Procedimento

1. Confirme que há resultado claro, pausa explícita ou dificuldade resolvida. Se a equipe ainda estiver testando hipóteses, pare.
2. Identifique destino de escrita: use `target_retrospective` exatamente quando fornecido; caso contrário, derive um Markdown em `retrospetivas/faseN/` ou no diretório aprovado pelo usuário.
3. Registre objetivo, resultado, critério de conclusão, artefatos criados/alterados/consultados/descartados e decisões humanas.
4. Liste validações feitas, bloqueadas, inconclusivas ou dependentes de gate humano.
5. Reconstitua apenas o rastro operacional material: ferramentas, comandos, scripts, buscas, leituras, tentativas úteis, tentativas falhas e correções de rota.
6. Classifique atritos relevantes pela taxonomia abaixo; omita categorias sem ocorrência material e não invente atritos para preencher checklist.
7. Para scripts, comandos ou validadores, registre objetivo, entrada, resultado esperado, resultado observado, surpresa, artefatos gerados, utilidade real e reutilização recomendada.
8. Para inferências úteis ou incorretas, registre evidência inicial, lacuna, resultado, correção de rota e lookup mínimo recomendado.
9. Para mismatches de ambiente, registre expectativa da LLM, estado real, detecção, impacto e preflight que teria evitado o atrito.
10. Redija com segurança: não inclua segredos, tokens, env vars, chaves privadas, transcrições brutas ou outputs sensíveis; prefira resumo redigido com referência segura à fonte.
11. Escreva o caminho mínimo recomendado para uma próxima LLM resolver tarefa equivalente com menos tentativas.
12. Extraia aprendizados reutilizáveis somente quando validados ou quando resolveram o problema de fato; marque hipóteses como não validadas.
13. Quando útil para deduplicação futura, adicione campos opcionais como `pattern_key`, `recurrence_count`, `first_seen`, `last_seen`, `see_also` e `lifecycle_status`, sem tratá-los como autorização automática de promoção.
14. Gere candidatos para melhoria contínua apenas como proposta ou handoff, nunca como mudança duradoura aplicada.
15. Liste riscos residuais, gates pendentes e próximo passo.

## Taxonomia de atrito

- `inference-good`: inferência correta que acelerou execução.
- `inference-bad`: inferência incorreta, prematura ou confiante demais.
- `file-discovery`: dificuldade para achar arquivo, símbolo, contrato, fonte de verdade ou artefato gerado.
- `script-command`: shell, Python, validator, build, test, parser ou snippet executado.
- `unexpected-output`: resultado vazio, truncado, ruidoso, contraditório ou diferente do esperado.
- `environment-mismatch`: versão, dependência, PATH, shell, cwd, permissão, rede, cache, symlink, runtime state ou package manager inesperado.
- `tool-friction`: ferramenta indisponível, lenta, limitada, sem permissão ou ambígua.
- `validation-friction`: validação ausente, tardia, flakey, cara, quebrada, inconclusiva ou humana.
- `source-friction`: fonte local ambígua, defasada, duplicada, fragmentada ou consultada tarde.
- `handoff-friction`: agente, skill, command, template ou doc carregado tarde, errado, duplicado ou incompleto.
- `state-friction`: worktree suja, mudança concorrente, diff inesperado, cache, lockfile ou estado persistido.
- `dependency-friction`: pacote, API, plugin, engine, schema, database, migration ou generated type inesperado.
- `format-friction`: JSON, YAML, frontmatter, Markdown, schema, encoding, case, line endings, locale ou timezone.
- `external-research-friction`: pesquisa externa necessária, evitável, recusada, tardia ou ampla demais.
- `user-correction`: correção, redirecionamento, decisão, escopo novo ou esclarecimento humano.
- `communication-waste`: pergunta ou explicação que não ajudou, resposta longa demais ou plano maior que a tarefa.
- `search-waste`: busca ampla, leitura integral, leitura repetida ou falta de lookup localizado.
- `scope-waste`: trabalho fora da task, refactor cosmético ou investigação maior que o risco.
- `safety-gate-friction`: approval, technical-review, human-validation ou research-consent ausente ou descoberto tarde.
- `minimum-next-path`: sequência menor recomendada para próxima execução.

## Formato mínimo de retrospectiva

Inclua seções para:

- objetivo e estado final;
- artefatos e evidências;
- validações;
- decisões humanas e gates;
- rastro operacional material;
- atritos e desperdícios;
- caminho mínimo recomendado;
- aprendizados reutilizáveis com fonte;
- candidatos para melhoria contínua;
- riscos residuais e próximos passos.

## Limites

- Retrospectiva não é standard.
- Não promova regra, skill, agent, command, doc, validator, template ou manifest diretamente.
- Não escreva em `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.codex/**`, `.claude/**` ou runtime sensível sem aprovação explícita separada.
- Acione `technical-review` e `approval` quando a retrospectiva recomendar mudança duradoura.
