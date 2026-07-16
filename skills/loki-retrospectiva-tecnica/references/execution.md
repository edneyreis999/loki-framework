# Execution — loki-retrospectiva-tecnica

## Purpose And Observable Contract

Este command orquestra retrospectiva tecnica objetiva e auditavel depois de
conclusao/pausa clara ou resolucao real, para outra LLM retomar contexto e para
melhoria continua avaliar evidencia sem transformar a retrospectiva em regra.

- Inicio: entrada normalizada com resultado observavel e fontes localizadas.
- Conclusao: retrospectiva no destino autorizado, validada e sem promocao direta,
  ou stop condition explicita.
- Resultado verificavel: artefatos, validacoes, decisoes, atritos, aprendizados,
  riscos e caminho minimo ligados a fontes concretas.
- Saidas obrigatorias: siga integralmente `references/response.md`.

## Execution Profile

```yaml
execution_profile:
  model_class: generalist
  default_effort: medium
  max_effort: high
  escalation_signals:
    - reusable learning may become durable policy
    - evidence is incomplete or conflicting
    - retrospective recommends package artifact changes
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: medium
    documentation_durable: high
    validator: low
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha captura/revisao em unidades
com responsaveis; selecione agentes; forneca contexto autocontido; acompanhe
handoffs ate terminal; aplique validators, gates e approvals; e consolide
evidencias, atritos, riscos e proximos passos. Mantenha responsabilidade pelo
estado global depois de delegar.

## Allowed Writes

- Retrospectiva do plano ativo no path convencionado.
- `target_retrospective` exato fornecido pelo chamador.
- Pequeno resumo de status somente quando a task autorizar path exato.

## Forbidden Writes

- `AGENTS.md`, `CLAUDE.md` ou contexto duradouro do consumidor.
- Promocao direta de standards, commands, skills, agents, templates,
  validators, docs consolidados, `manifest.yaml` ou `install-scopes.json`.
- Runtime, engine, framework, `<consumer_runtime_surfaces>` ou
  `<sensitive_write_patterns>` fora de escopo.
- `.claude/**`, `.agents/**` e `.codex/**`.

## Required Skills And Commands

```yaml
required_skills: []
required_commands: []
```

Nao carregue skill por default. Carregue `<technology_required_skills>` somente
quando necessario para interpretar evidencia de tecnologia, sem promover regra.

## Execution Planning And Replanning

Transforme a entrada normalizada em plano de coleta, classificacao, escrita e
validacao com fontes, responsaveis, handoffs, gates e criterio de conclusao.
Replaneje quando evidencia contradizer uma inferencia, invalidar um aprendizado
ou revelar que a dificuldade ainda nao foi resolvida.

## Handoffs

- `standards-curator`, proposal-only, quando classificacao ou destino duradouro
  candidato estiver ambiguo;
- `loki-continuous-improvement` somente como proximo workflow para candidato
  recorrente, validado e estruturado; nao e dependencia desta execucao;
- Write Agent apropriado para materializar a retrospectiva.

Antes de invocar subagente, entregue objetivo, unidade, fatos/decisoes, fontes,
paths, dependencias, escopo, allowed/forbidden writes, criterios, validators,
gates, formato e destino. Nao use contexto implicito. Registre origem, destino,
objetivo, entrada, resultado esperado, status, evidencia e proximo destino;
acompanhe ate estado terminal.

## Procedure

1. Declare objetivo, resultado, criterio, restricoes e target exato.
2. Liste artefatos criados, alterados, consultados ou descartados.
3. Registre validacoes feitas, nao feitas, bloqueadas, inconclusivas ou humanas.
4. Registre decisoes, correcoes, mudancas de escopo e pendencias.
5. Reconstitua somente o rastro operacional material; nao exponha cadeia de pensamento.
6. Classifique atritos materiais e inferencias boas/ruins pela taxonomia abaixo.
7. Para script/comando/validator, registre objetivo, entrada, esperado,
   observado, surpresa, artefato, utilidade e reuso.
8. Para mismatch de ambiente, registre expectativa, estado real, deteccao,
   impacto e preflight preventivo.
9. Registre desperdicio material com impacto qualitativo e acao preventiva.
10. Escreva o caminho minimo para uma proxima LLM.
11. Separe aprendizado validado, hipotese, falha operacional e preferencia humana.
12. Gere candidato duradouro somente com fonte, escopo, destino, verificacao e gate.
13. Marque riscos residuais e proximo passo.

## Execution Friction Taxonomy

Registre somente categorias com ocorrencia material; nao invente atrito:

- `inference-good`: evidencia confiavel, ganho e lookup repetivel.
- `inference-bad`: plausibilidade inicial, falha, correcao e check preventivo.
- `file-discovery`: arquivo, simbolo, contrato, symlink, mirror ou fonte dificil.
- `script-command`: comando, cwd, objetivo, entrada, resultado, artefato, custo e reuso.
- `unexpected-output`: resultado vazio, truncado, ruidoso ou contraditorio.
- `environment-mismatch`: versao, PATH, shell, cwd, sandbox, permissao, rede,
  cache, symlink, mirror, variavel, package manager ou runtime inesperado.
- `tool-friction`: ferramenta indisponivel, lenta, limitada ou com fallback.
- `validation-friction`: validator ausente, tardio, flakey, caro ou inconclusivo.
- `source-friction`: fonte ambigua, defasada, duplicada ou fragmentada.
- `handoff-friction`: agente/skill/command/template/doc errado, tardio ou incompleto.
- `state-friction`: worktree, concorrencia, diff, cache, lock ou estado inesperado.
- `dependency-friction`: pacote, API, schema, database, migration ou tipo divergente.
- `format-friction`: JSON, YAML, Markdown, encoding, case, line endings ou locale.
- `external-research-friction`: pesquisa evitavel, recusada, tardia ou ampla demais.
- `user-correction`: decisao ou redirecionamento humano que mudou a execucao.
- `communication-waste`: pergunta redundante, resposta/plano longo ou status inutil.
- `search-waste`: busca/leitura ampla, repetida, irrelevante ou tardia.
- `scope-waste`: trabalho fora da task, cosmetico ou intermediario inutilizado.
- `safety-gate-friction`: approval/review/validation descoberto tarde ou ambiguo.
- `minimum-next-path`: menor sequencia futura para chegar ao mesmo resultado.

## Friction Record Format

Para cada atrito material registre `Category`, `What Happened`,
`Expected Behavior`, `Actual Behavior`, `Context`, `Evidence`, `Cause`
(confirmada, provavel ou desconhecida), `Resolution Or Outcome`, `Was Useful`
(sim, nao ou parcialmente), `Waste Impact` (`low`, `medium` ou `high`, sem
numero inventado de tokens), `Reuse Guidance`, `Avoid Next Time` e
`Minimum Next Step`.

## Learning Capture Format

Cada candidato registra aprendizado ou `Mistake Description`, comportamento
esperado/real, contexto, causa suspeita, evidencia de resolucao, categoria de
atrito, caminho minimo, reuse/avoid guidance, waste impact qualitativo e fonte.
Marque hipoteses e correcoes parciais como nao validadas.

## Write Ownership And Serialization

Selecione Write Agent apropriado com target exato, writes, validators, gates,
evidencias e handoff. Defina owner unico, detecte sobreposicao, serialize writes
e interrompa concorrentes; leituras independentes podem ser paralelas.

Escrita direta so depois de registrar ausencia de Write Agent. Assuma envelope
com allowed/forbidden writes, validators, approvals, criterios e evidencias e
registre na propria retrospectiva tipo de escrita, motivo, oportunidade/escopo
de writer futuro, evidencias e riscos. Conveniencia nao justifica a excecao.

## Validators

- Cada aprendizado cita fonte concreta e separa fato, inferencia, decisao,
  validacao, risco, hipotese, atrito e desperdicio.
- O target fornecido e respeitado exatamente.
- Erros/acertos/atritos registram esperado, real, contexto, causa e reuso.
- Scripts, inferencias, mismatches e desperdicios possuem os campos aplicaveis.
- Somente evidencia validada ou que resolveu o problema vira aprendizado.
- Candidato duradouro sai como proposta/handoff, nunca promocao aplicada.
- Gate, validator ou handoff pendente interrompe conclusao.

## Human Gates

- `technical-review` para recomendacao de mudanca duradoura.
- `approval` para promocao posterior ou sincronizacao de contexto duradouro.

## Packaging Checks

Se houver candidato do pacote, registre tipo de artefato e encaminhe com
referencia aos guardrails; nao altere artefatos normativos nesta execucao.

## Limits

Retrospectiva nao e standard. Nao inclua conversa bruta, cadeia de pensamento
ou cronologia extensa; nao trate sucesso como eficiencia; nao invente dados nem
oculte atalhos uteis; nao promova hipotese ou correcao parcial.

## Stop Conditions

- Fase sem resultado claro ou dificuldade ainda em teste.
- Evidencia ausente ou contraditoria impede classificacao segura.
- Texto mistura evidencia com promocao direta.
- Escopo/permissao insuficiente, dependencia indisponivel, handoff sem destino,
  conflito de writers, validator falho ou gate/approval pendente.

## Resume Contract

Registre entrada, objetivo, resultado, artefatos, validacoes, decisoes, rastro
material, scripts/comandos, inferencias, atritos, outputs inesperados,
desperdicios, caminho minimo, aprendizados, riscos, candidatos, handoffs,
writers, gates, etapas concluidas, proxima acao e condicao para continuar.
Retome desse estado em vez de reiniciar.
# Evidence-first source rule

Accept `execution_evidence_sources` (validated manifests, completion records,
and read-only audit reports) as the preferred input. A legacy
`operational_trace` is contextual only and must not be reopened by default.
The orchestrator captures completion evidence; this command does not trigger an
automatic agent retrospective and must preserve gaps, inference labels and
lineage without exposing raw traces or private reasoning.
