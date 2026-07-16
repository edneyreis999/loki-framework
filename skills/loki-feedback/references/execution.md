# Execution — loki-feedback

## Purpose And Observable Contract

Este command e o orquestrador de uma entrevista curta que investiga feedback de
usuario, QA ou validacao humana, uma pergunta por vez, ate haver diagnostico
suficiente para propor proximos passos sem aplicar alteracoes.

- Inicio: entrada normalizada com `raw_feedback` valido e lacunas identificadas.
- Conclusao: nenhuma duvida critica permanece, as hipoteses estao apoiadas por
  evidencia permitida e existe diagnostico ou stop condition explicita.
- Resultado verificavel: diagnostico, registro das perguntas/respostas, proposta
  sem escrita e estado do research gate.
- Saidas obrigatorias: siga integralmente `references/response.md`.

Leia tambem
`references/diagnostic-output-and-forward-test.md` quando precisar emitir estados
intermediarios/terminais formais ou executar o forward test. Essa referencia e
complementar; em conflito, este contrato e o command transicional pareado
prevalecem.

## Execution Profile

```yaml
execution_profile:
  model_class: generalist
  default_effort: medium
  max_effort: high
  escalation_signals:
    - external research is required
    - evidence conflicts with user feedback
    - high-risk technical proposal
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: low
    documentation_durable: high
    validator: medium
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha o diagnostico em unidades com
responsavel identificavel; selecione agentes apropriados; forneca a cada
subagente contexto autocontido; acompanhe cada handoff ate sucesso, falha,
bloqueio ou parada; aplique validators/gates/approvals; e consolide evidencias,
riscos e proximos passos. A responsabilidade pelo estado global continua com o
orquestrador depois da delegacao.

## Allowed Writes

- Nenhuma. O diagnostico e a resposta terminal permanecem read-only; qualquer
  registro persistente pertence ao workflow chamador e exige um envelope de
  escrita proprio.

## Forbidden Writes

- Plano ativo, task files, build evidence ou interaction records, salvo a
  retrospectiva tecnica autorizada.
- Correcoes de codigo, configuracao, docs duradouros, commands, skills, agents,
  templates, validators, `manifest.yaml` ou `install-scopes.json`.
- `<sensitive_write_patterns>`, runtime, engine ou framework.
- `.claude/**`, `.agents/**` e `.codex/**`.

## Required Skills And Commands

```yaml
required_skills: []
required_commands: []
```

Evidence/gap e responsabilidade do orquestrador na resposta e no estado da
sessao; nao crie completion record persistente neste command.

## Execution Planning And Replanning

Transforme a entrada normalizada em plano com hipoteses, perguntas pendentes,
fontes locais permitidas, handoffs, validators, gates e criterio de conclusao.
Replaneje quando uma resposta ou evidencia invalidar uma hipotese; nao preserve
perguntas ou etapas que deixaram de ser materiais.

## Agents, Handoffs And Delegation

Delegue trabalho quando houver agente apropriado e a ambiguidade critica ja
estiver resolvida:

- `source-researcher`, read-only, para multiplas fontes locais ou pesquisa web
  ja aprovada;
- `runtime-qa`, read-only, para checklist/risco de comportamento em execucao;
- `technical-implementer` ou skill tecnica, proposal-only, para uma possivel
  correcao sensivel; nunca para aplicar a correcao neste command.

Antes de invocar subagente, forneca objetivo, unidade de trabalho, fatos e
decisoes, fontes/paths, dependencias, escopo, allowed/forbidden writes, criterios
de sucesso/falha, validators, gates, formato de saida e destino do handoff. Nao
use referencias implicitas como "continue" ou "use o contexto acima".

Registre por handoff origem, destino, objetivo, entrada, resultado esperado,
status, evidencia e proximo destino. Acompanhe-o ate estado terminal; invocacao
nao equivale a conclusao. Leituras independentes podem rodar em paralelo depois
da entrevista; nenhuma delegacao pode violar a regra de uma pergunta por turno.

## Workflow

1. Consuma a entrada normalizada do SKILL; nao volte a interpretar o pedido
   bruto de forma ambigua.
2. Normalize acao disparadora, observado, esperado e condicoes; marque ausencias.
3. Faca exatamente uma pergunta objetiva por turno enquanto houver ambiguidade
   critica. Nao apresente bateria, formulario ou pergunta dupla.
4. Leia apenas fontes locais necessarias e permitidas.
5. Acione `research-consent` somente quando informacao externa atual for
   material. Em turno proprio, pergunte exatamente:
   `Posso pesquisar na internet por: "<frase exata da busca>"?`
6. Nao pesquise sem consentimento explicito para essa frase.
7. Construa hipoteses separando fatos, inferencias e lacunas.
8. Proponha correcao, investigacao, plano, retrospectiva ou outro command apenas
   quando nao houver duvida critica.
9. Nao aplique a correcao. Encaminhe para o workflow apropriado, como
   `loki-tech-analysis`, `loki-human-decision-preflight`,
   `loki-generate-action-plan`, `loki-run-plan`,
   `loki-retrospectiva-tecnica` ou `loki-continuous-improvement`.
10. Retorne o diagnostico e o estado retomavel ao workflow chamador; nao crie
    registro persistente.

## Write Ownership And Serialization

Este command nao escreve arquivos e nao seleciona writer. Quando o diagnostico
exigir registro ou implementacao, encaminhe ao workflow chamador ou ao command
apropriado, que deve definir owner, targets, envelope, validators e gates antes
de qualquer escrita.

## Validators And Human Gates

- `interview` sempre que o feedback estiver ambiguo.
- `research-consent` para a frase exata antes de pesquisa externa.
- `human-validation` antes de declarar comportamento perceptivel, runtime,
  visual, audio, input, integracao ativa ou estado persistido como validado.
- A pergunta critica mais recente tem resposta util.
- Nenhuma duvida critica permanece no diagnostico terminal.
- A recomendacao esta ligada a evidencia, hipotese ou decisao humana.
- O fluxo nao aplicou a correcao nem realizou escrita nao autorizada.
- Falha ou pendencia de validator/gate/approval interrompe o fluxo.

## Packaging Checks

Nao altere pacote, consumer runtime nem superficies instaladas. Se o feedback
indicar mudanca duradoura, faca handoff; nao promova diretamente.

## Stop Conditions

- `raw_feedback` ausente ou invalido.
- Duvida critica sem resposta ou pedido de encerrar a entrevista.
- Pesquisa necessaria sem consentimento para a query exata.
- Evidencia exige acesso indisponivel ou escrita fora do escopo.
- Escopo/permissao insuficiente, dependencia indisponivel, handoff sem destino,
  conflito de writers, validator falho ou gate/approval pendente.
- Seria necessario aplicar a correcao antes de concluir o diagnostico.

## Evidence-First Cutover

Cada subagente devolve completion record; o orquestrador captura evidence
sanitizada após o handoff ou registra `partial`, `unavailable` ou `unsupported`.
Não registrar CoT privado nem invocar retrospectiva automaticamente.

## Resume Contract

Registre entrada normalizada, pergunta atual, respostas, fatos, inferencias,
hipoteses, fontes lidas, query proposta/aprovada, handoffs e seus estados,
validators, gates, approvals, writes/excecoes, diagnostico parcial, riscos,
etapas concluidas, pendencias, proxima acao e condicao para continuar. Retome
desse estado; nao reinicie do zero quando ele for suficiente.
