# Execution — loki-catalogar-docs

## Purpose And Observable Contract

Este command orquestra a catalogacao de documentacao duradoura do consumidor,
validando o alvo, descobrindo a arvore com limites verificaveis, processando-a
bottom-up e delegando mudancas ao Write Agent `catalogador` por envelopes
escopados.

- Inicio: entrada normalizada com `DOCS_DIR` valido e workspace conhecido.
- Conclusao: todos os batches autorizados chegaram a estado terminal, os
  indices compartilhados foram consolidados serialmente, os validators foram
  executados e gates pendentes foram registrados.
- Resultado verificavel: catalogo coerente com a arvore autorizada, arquivos
  afetados enumerados, `docs/index.xml` parseavel quando alterado e estado
  retomavel suficiente para outra LLM.
- Saidas obrigatorias: siga integralmente `references/response.md`.

## Orchestrator Responsibilities

Coordene as fases Input, Execution e Response. Decomponha o fluxo em unidades
com responsavel identificavel; selecione agentes; forneca a cada subagente um
contexto autocontido; acompanhe handoffs ate sucesso, falha, bloqueio ou parada;
aplique validators, gates e approvals; e consolide artefatos, evidencias,
riscos e proximos passos. O orquestrador continua responsavel pelo progresso e
estado global depois da delegacao; invocar um agente nao conclui a unidade.

## Execution Profile

```yaml
execution_profile:
  model_class: frontier_reasoning
  default_effort: high
  max_effort: xhigh
  escalation_signals:
    - ambiguous documentation target or ownership
    - recursive tree near command limits
    - conflicting target_files or shared index writes
    - durable consumer documentation changes without recorded approval
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: low
    documentation_durable: high
    validator: medium
```

Trate esse perfil como intencao provider-neutral. Codex o aplica de forma
consultiva salvo projecao em perfil, invocacao ou custom agent; Claude Code o
projeta apenas onde houver suporte.

## Required Skills And Commands

```yaml
required_skills: []
required_commands: []
```

Nenhuma skill tecnica e obrigatoria por default. Carregue
`lf-index-navigator` quando precisar navegar ou auditar um `docs/index.xml`
existente antes de montar envelopes. Carregue `<technology_required_skills>`
somente quando o conteudo do consumidor exigir validacao especializada.

## Allowed Writes

- `docs/**/*.md` e `docs/index.xml`, somente por `catalogador`, dentro de
  envelope aprovado e com ownership explicito.
- Outros arquivos de documentacao dentro de `DOCS_DIR` somente quando
  `OUT_OF_DOCS_APPROVAL` provar que o alvo e documentacao duradoura do
  consumidor e autorizar o escopo exato.
- Reports transitorios do plano ativo apenas quando o workflow chamador
  declarar destinos exatos em `target_files`.

Antes de toda escrita, declare `target_files`, `allowed_writes`, `write_mode`,
`scoped_write_domains`, owner, validators e gates. Approval para catalogar nao
autoriza ampliar o envelope.

## Forbidden Writes

- `.claude/**`, `.agents/**` e `.codex/**`.
- Caminhos absolutos externos ao workspace ou traversal/symlink que resolva
  para fora dele.
- Codigo-fonte, runtime, engine, dados, assets, build, artefatos gerados ou
  configuracao que nao sejam documentacao duradoura explicitamente aprovada.
- `index.md` por diretorio como comportamento default; o catalogo primario da
  primeira versao e `docs/index.xml`.
- Escrita paralela em `docs/index.xml`, indice de diretorio pai ou qualquer
  arquivo com owners sobrepostos.
- Stage, commit ou alteracao do indice Git.

## Execution Planning And Replanning

Converta a entrada normalizada em plano com descoberta, niveis bottom-up,
dependencias, envelopes, responsaveis, validators, gates e criterios de
conclusao. Calcule todos os `target_files` antes de abrir um batch. Replaneje
explicitamente se a descoberta mudar total, profundidade, classificacao do
alvo, ownership, disjuncao, necessidade de approval ou consolidacao do indice.
Nao continue com um plano invalidado.

## Path, Discovery And Tree Gates

1. Resolva `DOCS_DIR` contra o workspace real. Pare se nao existir, nao for
   diretorio, sair do workspace ou atravessar symlink/traversal externo.
2. Confirme que o alvo pertence a `/docs`. Fora de `/docs`, exija
   `OUT_OF_DOCS_APPROVAL` registrado e evidencia de que o alvo e documentacao
   duradoura, nao codigo, runtime, build ou configuracao.
3. Exclua deterministicamente `.git/`, `node_modules/`, `dist/`, `build/`,
   `.next/`, `.cache/`, `.turbo/` e `coverage/`.
4. Com `RECURSIVE: false`, use apenas `DOCS_DIR`.
5. Com `RECURSIVE: true`, descubra no maximo profundidade 10. Pare se a
   profundidade exceder 10 ou se o total exceder 100 diretorios.
6. Se o total for maior que 20 e menor ou igual a 100, exija
   `LARGE_TREE_CONFIRMATION` antes de catalogar.
7. Ordene a arvore das folhas para a raiz e preserve essa dependencia em todos
   os batches.

## Agents, Handoffs And Scoped-Write Envelope

Delegue criacao, alteracao, movimentacao ou remocao documental ao Write Agent
`catalogador`; o command coordena e nao e o executor principal. Use
`scoped-writer` somente depois de approval de escrita e com `target_files`
comprovadamente disjuntos. Use `proposal-only` enquanto faltar approval, quando
a disjuncao nao estiver provada ou quando a unidade tocar `docs/index.xml` ou
indice pai antes da etapa serial.

Antes de invocar qualquer subagente, entregue contexto autocontido contendo:

- objetivo da tarefa, motivo e unidade de trabalho;
- fatos, decisoes humanas, restricoes e exclusoes;
- paths e fontes exatos, com relevancia;
- dependencias e resultados dos batches filhos;
- `command: loki-catalogar-docs`;
- `write_mode: task_scoped_writer` ou `proposal-only`;
- `target_files` exatos e `allowed_writes` iguais ou mais restritos;
- `scoped_write_domains: ["consumer-docs", "docs-index"]`;
- owner exclusivo, success/failure destination e proibicao de writers
  concorrentes;
- validators, human gates, approvals e evidencias esperadas;
- criterios de sucesso, falha, conclusao e formato de resposta.

Nao use referencias implicitas como "conforme discutido", "continue" ou "use
o contexto acima". O `catalogador` nao decide escopo, recursao, paralelismo,
limites nem permissao de escrita; devolve a lacuna ao orquestrador sem escrever.

Registre para cada handoff origem, destino, objetivo, entrada entregue,
resultado esperado, status, evidencia recebida e proximo destino. Acompanhe-o
ate estado terminal e consolide os retornos de um nivel antes de subir.

## Bottom-Up Fan-Out And Index Serialization

Para cada nivel bottom-up, prove disjuncao de `target_files` antes de qualquer
fan-out. Leituras e propostas independentes podem ocorrer em paralelo. Escritas
podem ser delegadas em paralelo somente quando os envelopes sao disjuntos, o
approval e o ownership estao registrados e nenhum envelope toca
`docs/index.xml`, indice pai ou outra superficie compartilhada.

Defina um unico owner por arquivo em cada momento. Detecte sobreposicao antes
de delegar, interrompa writers concorrentes e serialize toda escrita
compartilhada. Depois que os batches filhos terminarem ou entregarem propostas,
execute uma unica consolidacao serial de `docs/index.xml` e indices pais.

## Direct-Write Exception

Escrita direta pelo orquestrador e proibida enquanto `catalogador` ou outro
Write Agent apropriado estiver disponivel. Somente se nenhum Write Agent
apropriado existir, registre essa ausencia e assuma explicitamente um envelope
com target exato, allowed/forbidden writes, owner unico, validators, gates,
approvals, criterios de sucesso/falha e evidencias. Conveniencia, velocidade ou
tamanho da mudanca nao justificam a excecao.

Se a excecao ocorrer, registre no completion record o tipo de escrita, o
motivo da ausencia, a oportunidade e o escopo de um futuro Write Agent, as
evidencias e os riscos. Nao encerre sem esse registro.

## Workflow

1. Consuma o registro normalizado e confirme gates de path e approvals.
2. Aplique exclusoes e descubra a arvore dentro dos limites.
3. Monte a ordem bottom-up e calcule `target_files` por nivel.
4. Detecte conflitos e escolha `scoped-writer` ou `proposal-only` para cada
   envelope do `catalogador`.
5. Execute apenas fan-out disjunto; acompanhe todos os handoffs e consolide um
   nivel antes do seguinte.
6. Consolide `docs/index.xml` e qualquer indice pai em etapa unica e serial.
7. Rode validators automaticos, registre gates humanos e prepare a Response.

## Validators

- `DOCS_DIR` existe, e diretorio e permanece dentro do workspace.
- O alvo esta em `/docs` ou possui `OUT_OF_DOCS_APPROVAL` escopado e registrado.
- A descoberta exclui `.git/`, `node_modules/`, `dist/`, `build/`, `.next/`,
  `.cache/`, `.turbo/` e `coverage/`.
- Profundidade `<= 10`, total `<= 100` e `LARGE_TREE_CONFIRMATION` presente
  quando total `> 20`.
- Todo handoff contem contexto autocontido, `target_files`, `allowed_writes`,
  `write_mode`, `scoped_write_domains`, owner, validators, gates e destinos.
- Batches paralelos possuem `target_files` disjuntos; indices compartilhados
  possuem uma unica escrita serial.
- Se `docs/index.xml` mudar, parseie-o como XML valido; cada documento
  catalogado deve possuir `path`, `summary`, `use_when`, `not_covered`,
  `keywords` e `sections`; paths existem; nao ha entradas duplicadas ou orfas.
- Hyperlinks e referencias cruzadas tocados resolvem para destinos existentes.
- O diff permanece no envelope aprovado e nenhuma forbidden write ocorreu.

Associe cada acao ao validator, gate ou approval correspondente e verifique o
resultado antes de continuar. Pare quando um controle obrigatorio estiver
ausente, pendente, rejeitado ou falhar. Validator automatico nao substitui gate
humano.

## Human Gates

- `interview` quando `DOCS_DIR`, `RECURSIVE` ou classificacao do alvo estiver
  ambigua.
- `approval` antes de qualquer escrita em documentacao duradoura.
- `approval` especifico para alvo fora de `/docs`.
- `human-validation` para coerencia, clareza e navegabilidade que nao possam
  ser comprovadas deterministicamente; registre roteiro e evidencia esperada.
- `technical-review` para mudancas no command bundle, `catalogador`, roteamento,
  manifest, install scopes ou validators do pacote.

## Packaging Checks

Este e um command bundle final `schema2` com `serialization: skill-bundle`.
Confirme que `skills/loki-catalogar-docs/SKILL.md` tem o mesmo stem e que
`execution.md`, `response.md` e `assets/response-template.md` existem, sem
projecao de contrato legada dentro do bundle. Valide o pacote com
`python3 scripts/validate-install-scopes.py` e com os scans de guardrails.
Quando o command for aceito ou seu inventario mudar, confirme tambem a
sincronia de `manifest.yaml`, `install-scopes.json`,
`docs/operational-inventory.md` e do roteador compartilhado; uma auditoria
escopada nao autoriza altera-los sem inclui-los explicitamente no escopo.

## Stop Conditions

- Entrada obrigatoria ausente, invalida ou ambigua.
- Escopo ou permissao insuficiente; alvo inexistente, nao diretorio ou fora do
  workspace; alvo fora de `/docs` sem approval.
- Alvo de codigo, runtime, engine, dados, assets, build ou configuracao sem
  escopo documental explicito.
- Profundidade maior que 10, total maior que 100 ou total maior que 20 sem
  confirmacao.
- `target_files` sobrepostos, conflito de owners, writer concorrente ou indice
  compartilhado planejado em paralelo.
- Handoff incompleto ou sem destino; dependencia indisponivel.
- Approval/gate pendente ou rejeitado; validator ausente, falho ou inconclusivo.
- Proxima acao exige forbidden write ou decisao humana ausente.

## Evidence-First Cutover

Cada subagente devolve completion record; o orquestrador captura evidence
sanitizada ou registra `partial`, `unavailable` ou `unsupported`, sem
retrospectiva automática ou CoT privado.

## Resume Contract

Registre inputs originais e normalizados, workspace, `DOCS_DIR` resolvido,
recursividade, exclusoes, arvore, profundidades, total, batches bottom-up,
envelopes e handoffs com status, `target_files`, allowed writes, owners,
conflitos, arquivos afetados, validators e evidencias, gates e approvals,
etapas concluidas, `blocked_by`, riscos, proxima acao e condicao para continuar.
Retome desse estado sem reiniciar o trabalho ja validado.
