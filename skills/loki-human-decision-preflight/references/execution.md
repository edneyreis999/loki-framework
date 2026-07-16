# Execution — loki-human-decision-preflight

## Purpose And Observable Contract

Este command orquestra a classificacao de decisoes humanas pendentes antes do
planejamento, separando o que precisa ser perguntado agora do que pode ser
delegado, validado depois ou resolvido por leitura local.

- Inicio: entrada normalizada com `analysis_or_brief` valido, escopo e
  forbidden surfaces conhecidos.
- Conclusao: todas as perguntas estao classificadas e nenhuma decisao
  `must_ask_now` permanece sem resposta, ou existe stop condition explicita.
- Resultado verificavel: classificacoes com fonte, impacto e motivo, respostas
  humanas registradas, pendencias delegadas e `ready_for_next_phase` coerente.
- Saidas obrigatorias: siga integralmente `references/response.md`.

## Execution Profile

```yaml
execution_profile:
  model_class: generalist
  default_effort: medium
  max_effort: high
  escalation_signals:
    - many open human decisions
    - conflicting local evidence
    - sensitive writes or irreversible product choices
    - decision changes plan topology or acceptance criteria
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: medium
    documentation_durable: high
    validator: medium
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha a preflight em unidades com
responsavel identificavel; selecione agentes apropriados; forneca a cada
subagente contexto autocontido; acompanhe cada handoff ate sucesso, falha,
bloqueio ou parada; aplique validators, gates e approvals; e consolide
classificacoes, evidencias, riscos e proximos passos. A responsabilidade pelo
estado global continua com o orquestrador depois da delegacao.

## Allowed Writes

- Nenhuma por default.
- Markdown transitorio somente no `target_decision_record` exato e aprovado,
  dentro do diretorio de analise ou plano autorizado pelo workflow chamador.

## Forbidden Writes

- Runtime, engine, framework, assets, dados persistidos, configuracao ativa,
  `<consumer_runtime_surfaces>` ou `<sensitive_write_patterns>`.
- Docs duradouros do consumidor, `AGENTS.md`, `CLAUDE.md`, commands, skills,
  agents, templates, validators, `manifest.yaml` ou `install-scopes.json`.
- `.claude/**`, `.agents/**` e `.codex/**`.
- Qualquer superficie declarada em `forbidden_surfaces`.

## Required Skills And Commands

```yaml
required_skills:
  - lf-tech-analysis-authoring
  - lf-action-plan-authoring
required_commands: []
```

Carregue `lf-tech-analysis-authoring` para separar fatos, inferencias,
hipoteses, fontes e gates. Carregue `lf-action-plan-authoring` para decidir se
uma pendencia cabe em task, validator, human loop ou stop condition. Carregue
condicionalmente `lf-index-navigator` para docs duradouros do consumidor e
`<technology_required_skills>` quando o contexto declarar tecnologia.

## Execution Planning And Replanning

Converta a entrada normalizada em plano de classificacao com perguntas,
fontes, dependencias, responsaveis, validators, gates e criterio de conclusao.
Priorize a decisao que mais bloqueia o plano. Replaneje quando nova fonte ou
resposta alterar categoria, escopo, impacto ou ordem das perguntas.

## Agents, Handoffs And Delegation

- `bibliotecario`, read-only, quando a resposta provavelmente estiver em
  `/docs` e puder ser localizada por `docs/index.xml`;
- `source-researcher`, read-only, para fontes locais multiplas, conflito de
  evidencia ou pesquisa externa previamente aprovada;
- `runtime-qa`, proposal-only, para propor evidencia de `human-validation`;
- agente de dominio, proposal-only, para distinguir preferencia humana de
  detalhe delegavel.

Handoffs nao decidem respostas humanas. Antes de invocar subagente, entregue
objetivo, unidade, fatos e decisoes, fontes e paths, dependencias, escopo,
allowed/forbidden writes, criterios de sucesso/falha, validators, gates,
formato de saida e destino do handoff. Nao use referencias implicitas como
"continue" ou "use o contexto acima".

Registre por handoff origem, destino, objetivo, entrada, resultado esperado,
status, evidencia e proximo destino. Acompanhe ate estado terminal; invocacao
nao equivale a conclusao. Delegue leituras e propostas quando houver agente
apropriado, mas nunca delegue a decisao humana.

## Classification Rules

Use `must_ask_now` quando a resposta alterar escopo, prioridade, aceite,
narrativa/produto, identidade publica, destino de escrita, politica, permissao,
risco legal/seguranca, comportamento irreversivel, topologia do plano,
dependencias, owners, gates ou arquivos-alvo, e nao puder ser inferida com
seguranca por fonte local ou validator.

Use `can_delegate_to_plan` para decisao de implementacao dentro do escopo
aprovado que possa virar task com owner, targets, validator, human loop ou stop
condition sem mudar aceite, escopo ou ordem principal.

Use `can_validate_later` quando a resposta depender de percepcao humana,
playtest, UX, audio, visual, performance, integracao ativa ou runtime e puder
ser representada por `human-validation` e evidencia observavel posterior.

Use `do_not_ask_llm_can_determine` quando leitura local, parse, docs, schema,
codigo, configuracao ou validator puder responder tecnicamente.

## Workflow

1. Consuma a entrada normalizada; confirme escopo, forbidden writes e destino.
2. Extraia perguntas, assumptions, riscos, human gates e pontos de planejamento.
3. Separe intencao humana de perguntas respondiveis por fonte local e confira
   primeiro as fontes obvias permitidas.
4. Classifique cada pergunta com categoria, fonte, impacto e motivo.
5. Para `do_not_ask_llm_can_determine`, registre o lookup local minimo.
6. Para `can_delegate_to_plan`, registre task, owner provavel, validator, human
   loop ou stop condition esperada.
7. Para `can_validate_later`, registre gate e evidencia futura.
8. Para `must_ask_now`, faca exatamente uma pergunta objetiva por turno,
   priorizando a mais bloqueante; nunca apresente bateria ou pergunta dupla.
9. Atualize somente o `target_decision_record` autorizado, quando existir.
10. Defina `ready_for_next_phase: true` apenas sem `must_ask_now` pendente;
    caso contrario, mantenha `false` e pare no estado `needs-input`.

## Write Ownership And Serialization

Antes de criar ou alterar o registro transitorio, selecione Write Agent
apropriado e entregue target exato, writes, validators, gates, evidencias e
handoff. Defina um unico owner por arquivo, detecte sobreposicao, serialize a
escrita e interrompa writers concorrentes; leituras independentes podem ser
paralelas.

Escrita direta so e permitida depois de registrar que nenhum Write Agent
apropriado existe. Assuma owner unico e envelope completo com allowed/forbidden
writes, validators, approvals, criterios e evidencias. Registre no completion
record o tipo de escrita, motivo da ausencia, oportunidade e escopo de um
writer futuro, evidencias e riscos. Conveniencia nao justifica a excecao.

## Validators

- Toda pergunta tem categoria, fonte, impacto e motivo.
- Nenhuma `must_ask_now` e inferida sem evidencia ou decisao humana registrada.
- Nenhuma `do_not_ask_llm_can_determine` chega ao humano antes do lookup minimo.
- Toda `can_delegate_to_plan` declara task, owner, validator ou stop condition.
- Toda `can_validate_later` declara gate e evidencia esperada.
- `ready_for_next_phase` e `false` enquanto houver `must_ask_now` sem resposta.
- Pesquisa externa ocorre somente apos consentimento para a frase exata.
- Falha ou pendencia de validator, gate ou approval interrompe o fluxo.

## Human Gates

- `interview` para cada decisao `must_ask_now`, uma por turno.
- `approval` para escrever fora de destino ja aprovado pelo chamador.
- `research-consent` antes de qualquer busca externa, com query exata.
- `human-validation` para comportamento perceptivel, runtime, integracoes,
  estado persistido ou output gerado.
- `technical-review` se a preflight propuser alterar artefato consolidado.

## Packaging Checks

Nao altere o pacote durante a execucao. Se a preflight revelar mudanca
duradoura, encaminhe-a ao workflow apropriado. Valide apenas as referencias e
limites locais disponiveis para a invocacao.

## Stop Conditions

- `analysis_or_brief` ausente, invalido ou nao localizado.
- Destino transitorio sem approval ou fora do envelope.
- Decisao `must_ask_now` sem resposta.
- Pesquisa externa necessaria sem consentimento para a query exata.
- Conflito entre fonte e resposta humana que muda escopo ou aceite.
- Escopo/permissao insuficiente, dependencia indisponivel, handoff sem destino,
  conflito de writers, validator falho ou gate/approval pendente.
- Proxima etapa exigiria escrita sensivel sem plano, validator e gate.

## Evidence-First Cutover

Cada subagente devolve completion record; o orquestrador captura evidence
sanitizada após o handoff ou registra `partial`, `unavailable` ou `unsupported`.
Não registrar CoT privado nem invocar retrospectiva automaticamente. A
persistência terminal atômica do preflight permanece inalterada.

## Resume Contract

Registre entrada normalizada, fonte analisada, destino, perguntas por categoria,
respostas humanas, fontes consultadas, research gate, handoffs e estados,
validators, gates, approvals, writers, proxima pergunta ativa,
`ready_for_next_phase`, pendencias delegadas, etapas concluidas, riscos, proxima
acao e condicao para continuar. Retome desse estado em vez de reiniciar.
