---
title: Guardrails de Autoria do Pacote Loki
type: package-authoring-guardrails
status: draft
created: 2026-06-24
self_contained: true
---

# Guardrails de Autoria do Pacote Loki

Este documento transforma os aprendizados operacionais do plano `010-manual-fixes-loki-framework` em regras de autoria para evoluir o proprio pacote `002-loki-framework-local`.

Use este checklist sempre que a mudanca tocar command bundles, `skills/`, `agents/`,
`codex/agents/`, `scripts/`, `templates/`, `docs/`, `README.md`, `index.md`, `index.xml` ou
`manifest.yaml`.

Quando a mudanca nascer de aprendizado, retrospectiva ou melhoria continua,
aplique primeiro o
[Workflow de Aprendizado do Loki](loki-learning-workflow.md). Este arquivo cobre
os guardrails depois que o destino candidato tocar o pacote ou uma superficie
duradoura.

## Preflight de Destino

Antes de escrever:

1. Classifique a mudanca como `command`, `skill`, `agent`, `template`, `doc`, `manifest`, `standard` ou `backlog`.
2. Classifique tambem o perfil de execucao esperado usando
   [Model and Effort Guidance for Loki Artifacts](model-effort-guidance.md):
   documentacao duravel, artefato transitorio, implementacao de codigo,
   escrita human-like, leitura read-only ou orquestracao.
3. Confirme se o destino certo e:
   - artefato consolidado do pacote;
   - contexto duradouro do projeto consumidor, como `docs/**/*.md`,
     `docs/index.xml`, `AGENTS.md` ou `CLAUDE.md`;
   - ou apenas artefato transitorio do plano ativo.
4. Se o aprendizado pertencer apenas a task, interaction, build, validation ou retrospectiva da fase atual, nao promova para o pacote; mantenha local ou faca handoff apropriado.
5. Se a mudanca for normativa para o pacote, exija pelo menos `technical-review`.
6. Se a mudanca relaxar politica, instalar em `.claude/**`, `.codex/**` ou `.agents/**`, sincronizar contexto duradouro no consumidor, ou promover regra duradoura, exija `approval`.

## Superficies Duradouras vs Transitorias

### Superficies duradouras

- `AGENTS.md`: instrucoes project-wide que devem guiar a LLM ao longo de multiplos planos.
- `CLAUDE.md` ou equivalente: comportamento especifico de Claude Code, Codex ou outro adaptador.
- `docs/**/*.md` do consumidor: regras de negocio, lore, fluxo funcional,
  terminologia e contexto factual que devem sobreviver a varios planos.
- `docs/index.xml` do consumidor: catalogo navegavel para localizar a
  documentacao duradoura com baixo custo.
- command bundles, `skills/`, `agents/`, `codex/agents/`, `scripts/`,
  `templates/`, `docs/`, `README.md`, `index.md`, `manifest.yaml` e validators
  do pacote.

### Artefatos transitorios

- `tasks.md`, `task-N.M.md`, `interaction/`, `builds/`, `validation/`, notes de execucao e outros artefatos do plano em curso.
- Retrospectivas de fase, que podem sobreviver ao plano como evidencia auditavel, mas nao sao o destino final de regra duradoura.

### Regra de placement

- Corrija a superficie duradoura que teria evitado a repeticao do erro.
- Nao use task, interaction, build ou retrospectiva como destino final quando a melhoria e project-wide ou normativa.
- Nao promova para `AGENTS.md` ou `CLAUDE.md` algo que seria melhor expresso como skill, command, agent, template ou validator reutilizavel.
- Nao grave regra de negocio do projeto consumidor no pacote Loki. Esse
  conteudo vai para `/docs` do consumidor e seu `docs/index.xml`.

## Regras de Estrutura

### Identidade operacional vs serializacao

Classifique o papel operacional antes de considerar o caminho fisico:

- `skills/loki-<stem>/SKILL.md` com `type: command` identifica um **command**
  operacional, independentemente do diretorio;
- `serialization: skill-bundle` torna o bundle a unica fonte e
  proibe campos de projection ou contrato pareado;
- `lf-*` e namespaces explícitos de domínio ou tecnologia identificam
  **skills** operacionais;
- `agents/**` e suas projeções identificam **agents**.

A identidade operacional prevalece sobre diretório, extensão, seção de
inventário ou formato de instalação. Nunca use `type: skill`, a expressão
`wrapper skill` ou o caminho `skills/**` para reclassificar um bundle
`loki-*` como skill.

Cada command bundle declara `type: command`, `serialization: skill-bundle`,
Input no `SKILL.md`, Execution/Response em `references/` e template em `assets/`.
Toda auditoria produz uma única tabela 24/24 com evidência por arquivo e heading.

### Skills

- Toda skill empacotada deve morar em `skills/<skill-name>/SKILL.md`.
- O nome da pasta deve ser igual ao `name` no frontmatter.
- Em `skills/`, o prefixo `loki-` e reservado para commands operacionais, nao
  para skills; exige `serialization: skill-bundle` e proibe contrato pareado.
- Helpers internas do framework devem usar o prefixo `lf-*`.
- Skills opcionais de tecnologia ou dominio devem usar namespace proprio, como
  `rpg-maker-mz-*`, e nao `loki-*` salvo quando forem projeções de comandos.
- `name` e `description` sao obrigatorios no frontmatter top-level.
- O `description` deve carregar o principal contexto de trigger. `When To Use` no corpo nao substitui isso.
- Metadados multi-adapter devem preservar os tipos aceitos pelo runtime:
  `hooks` como mapping (`{}` quando vazio) e `shell` como `bash` ou
  `powershell`; `hooks: []` e `shell: {}` falham no diagnóstico Claude Code.
- Quando a skill orientar roteamento de modelo, use a semantica provider-neutral
  definida em `docs/model-effort-guidance.md` e nao prometa enforcement em
  adaptadores que tratam `SKILL.md` apenas como metadado.
- Material condicional, exemplos longos e variantes devem ir para `references/`.
- Nao deve haver arquivos `.md` soltos diretamente em `skills/`.

### Commands

- A identidade canonica e o proprio `name: loki-<stem>`.
- O contrato precisa declarar `allowed_writes`, `forbidden_writes`,
  `required_skills`, `required_commands`, `validators`, `human_gates`,
  `stop_conditions` e `resume_contract`. Dependências `loki-*` pertencem a
  `required_commands`; `required_skills` aceita somente skills operacionais.
- O contrato deve apontar para `model_class`, `effort`, sinais de escalamento
  ou `execution_profile` quando orientar custo, raciocinio ou handoffs.
- Quando o comando processar aprendizados de fase, ele deve separar claramente fonte transitoria de destino duradouro.
- Se o comando evoluir o proprio pacote, ele deve listar validacoes de pacote e artefatos normativos impactados.
- Use somente o bundle com `type: command` e `serialization: skill-bundle`.
  Atualize `manifest.yaml` e `install-scopes.json` na mesma mudanca.

### Agents

- Agentes devem ter responsabilidade estreita e formato `read-only`,
  `proposal-only` ou `scoped-writer`; destinos exatos de escrita pertencem ao
  envelope do workflow chamador, nao a uma permissao fixa no contrato do agente.
- `proposal-only` continua proibindo escrita em docs duradouros, runtime, codigo,
  assets, config, inventarios finais, `AGENTS.md`, `CLAUDE.md`, `.agents/**`,
  `.codex/**` e `.claude/**`, salvo approval explicito em outro contrato.
- `loki-init` classifica investigadores como
  `init_inventory_domain_investigator`. Eles sao read-only/proposal-only e
  retornam `loki_init_research_packet` schema v1 com fontes, fatos, inferencias,
  lacunas, conflitos e cobertura; nao escrevem `/docs`, nao invocam
  `catalogador` e nao recebem excecao de escrita como fallback.
- Somente `catalogador` escreve documentacao duradoura do consumidor. No init,
  a sequencia serial usa `init-bootstrap-cataloger`,
  `init-publication-batch` e `init-final-reconciliation`, com caller, mode,
  fontes e targets explicitos, cobertura, continuacao, materializacao e
  retomada. Indisponibilidade bloqueia; nao existe writer alternativo.
- Quando `loki-init` exigir retrospectiva tecnica por agente, todo agente
  invocado pode receber tambem uma excecao estreita para escrever somente o
  proprio `target_retrospective` exato em
  `planos/000-init-loki/retrospetivas/fase1/<agent-name>-retrospectiva.md`.
  Essa excecao nao autoriza docs duradouros, inventarios finais, runtime,
  codigo, assets, config, `AGENTS.md`, `CLAUDE.md`, `.agents/**`,
  `.codex/**` ou `.claude/**`.
- `loki-run-plan` pode invocar agentes `scoped-writer` como owners de escrita
  por task. O envelope deve declarar `target_files`, `allowed_writes`,
  `scoped_write_domains`, validators e gates; nenhum agente escreve fora desses
  arquivos.
- Antes de cada task, `loki-run-plan` aplica `lf-domain-context-preflight`:
  consulta o catalogo, prefere fontes atuais quando docs estiverem stale,
  registra freshness, conflitos e lacunas e usa `bibliotecario` apenas para a
  menor leitura suficiente. O preflight nao autocorrige `/docs`; tasks de docs
  do consumidor pertencem ao `catalogador`.
- Workflows Loki que exijam retrospectiva tecnica por agente podem conceder
  permissao estreita para o proprio `target_retrospective` exato sob o
  diretorio de retrospectivas da fase ativa, como
  `planos/<plano>/retrospetivas/faseN/<agent-name>-retrospectiva.md`.
- Essas permissoes devem ser projetadas como capacidades requeridas do agente;
  nao use handoff como substituto para arquivo proprio do agente nem transforme
  isso em permissao ampla de escrita.
- `description` deve explicar gatilhos concretos e limites.
- Metadados de agente devem distinguir `model_class`, `effort`, isolamento e
  projecao por adaptador quando o agente puder ser materializado em Claude Code,
  Codex custom agent ou outro runtime.
- Mudancas em agentes do pacote devem indicar impacto em `manifest.yaml` e docs quando aplicavel.
- Mudancas em `agents/*.md` devem manter `codex/agents/*.toml` sincronizado
  quando o agente tiver superficie Codex. O nome base do TOML deve acompanhar o
  nome base do Markdown.

### Codex Symlink Installer

- `scripts/install-loki-symlinks.py` e fonte versionada do pacote.
- `install-scopes.json` e a fonte machine-readable dos perfis e escopos de
  instalacao. Mantenha esse arquivo em sincronia com `skills/*/SKILL.md`,
  `agents/*.md` e `codex/agents/*.toml`.
- Escopos validos: `internal-only`, `both`, `consumer-only`.
- Perfis validos: `consumer` (`both` + `consumer-only`), `package-source`
  (`both` + `internal-only`) e `all` (todos os escopos).
- Artefatos `both` devem ser neutros: sem instrucao Loki-only, sem condicional
  package/consumer e sem dependencia obrigatoria de artefato `internal-only`.
- Para comandos, skills e agentes `both`, aplique checklist binaria antes de escrever:
  nao exigir checkout do pacote, `manifest.yaml`, docs internos de autoria,
  `planos/**`, branch guardada, build reports, comandos `internal-only`, skills
  `internal-only` ou condicionais package/consumer como fonte de execucao.
- Quando uma regra util falhar essa checklist, mova para artefato
  `internal-only`; se for historico, remova; se for reutilizavel, reescreva em
  termos neutros; se a decisao nao for objetiva, bloqueie para
  `technical-review`.
- O instalador deve apontar destinos `.agents/**` e `.codex/**` para fontes
  dentro do package root, nunca para artefatos instalados locais.
- Alteracoes em comandos, skills ou agentes instalaveis devem atualizar
  `install-scopes.json` na mesma mudanca.
- Command bundles Codex sao instalados como diretorios em
  `.agents/skills/loki-*`, filtrados pelo perfil ativo.
- Links legados de command só podem ser removidos com
  `--yes --cleanup-legacy-commands`, quando forem symlinks exatos para a antiga
  fonte do mesmo pacote e nenhum parent for symlink. Arquivos reais e links
  divergentes sempre bloqueiam.
- Agentes Markdown e projecoes Codex sao instalados por arquivo em
  `.agents/agents/*.md` e `.codex/agents/*.toml` para respeitar o perfil ativo.
- Destinos legados com `.agents/agents` como symlink de diretorio devem
  bloquear a instalacao por arquivo; nao escreva nem substitua arquivos atraves
  desse symlink.
- Validadores sobre diretorios instalados por symlink devem usar `find -L`
  quando precisarem atravessar o conteudo dos diretorios linkados.
- `--replace` em destino consumidor real exige approval escopado ao destino e
  ao modo de execucao.

### Docs e Manifest

- `manifest.yaml` deve apontar apenas para arquivos existentes dentro do package root.
- `manifest.yaml` deve manter `supported_project_types`,
  `agent_project_tag_policy.base_tag` e `agents[].project_tags` coerentes com o
  contrato de selecao de agentes do `loki-init`; rode o validador estrutural
  quando adicionar, remover ou retaggear agentes.
- Nenhuma fonte normativa do pacote pode apontar para fora deste diretorio.
- `README.md`, `docs/usage-guide.md`, `docs/source-boundaries.md` e docs de politica devem continuar coerentes entre si.
- Se o pacote orientar aplicacao em `docs/**/*.md`, `docs/index.xml`,
  `AGENTS.md` ou `CLAUDE.md` do consumidor, trate esses arquivos como destino de
  aplicacao aprovado, nunca como dependencia normativa do pacote.
- `index.md` do pacote e navegacao interna do framework. `docs/index.xml` do
  consumidor e navegacao da documentacao local do projeto. Nao confundir as
  duas superficies.
- A exclusividade de `catalogador` vale para docs duradouros do consumidor.
  Docs dentro do package root continuam sob autoridade escopada de
  `framework-artifact-writer`; essa autoridade nao se estende ao consumidor.

## Placement Matrix para Promocao de Contexto

Resumo de destino para autoria. O fluxo completo de aprendizado, evidencia,
classificacao e gates esta em
[Workflow de Aprendizado do Loki](loki-learning-workflow.md).

| Tipo de melhoria | Destino correto | Evite usar como destino |
| --- | --- | --- |
| Regra de negocio, lore, fluxo funcional ou contexto factual do projeto consumidor | `docs/**/*.md` + `docs/index.xml` | qualquer arquivo do pacote Loki |
| Regra que deve guiar toda LLM do projeto consumidor | `AGENTS.md` | task, interaction, build, retrospectiva |
| Regra especifica de Claude Code, Codex ou adaptador equivalente | `CLAUDE.md` ou equivalente | `AGENTS.md` generico, task local |
| Procedimento tecnico reutilizavel | `skills/` | doc generico longa ou checklist local |
| Workflow com estado, outputs e gates | command bundle em `skills/loki-*/` | `AGENTS.md`, retrospectiva |
| Papel especialista com julgamento proprio | `agents/` | skill ou task isolada |
| Formato repetivel de contrato ou artefato | `templates/` | copiar texto em varias tasks |
| Politica, validator, gate ou docs normativos do pacote | `docs/`, validator correspondente ou `manifest.yaml` | retrospectiva ou backlog quando a evidencia ja for suficiente |
| Aprendizado ainda insuficiente ou caso isolado | backlog | qualquer superficie normativa |

## Classificacao de Referencias Externas

Ao auditar uma referencia fora do pacote, classifique antes de editar:

| Categoria | Permitida | Exemplo | Observacao |
| --- | --- | --- | --- |
| Fonte normativa externa | Nao | blueprint externo, plano historico, `.agents/` como origem | Deve ser internalizada, resumida ou removida. |
| Destino duradouro do consumidor | Sim | `docs/**/*.md`, `docs/index.xml`, `AGENTS.md`, `CLAUDE.md` | Permitido como alvo de aplicacao ou sincronizacao aprovada; nunca como fonte normativa do pacote. |
| Destino de instalacao | Sim | `.claude/**`, `.codex/**`, `.agents/**` | Permitido como destino, nunca como fonte normativa. |
| Superficie sensivel declarada do consumidor | Sim | caminhos listados no contrato do consumidor, em `declared_consumer_surfaces` ou equivalente | Permitido como alvo futuro de plano, nao como dependencia do pacote. |
| URL oficial de referencia | Sim | docs oficiais | Serve como evidencia externa, nao como dependencia local. |

## Validacoes Minimas

### Qualidade de artefatos para consumo por LLM

Classifique a aplicabilidade LLM-facing separadamente do modo documental e
antes de validar uma mudanca do pacote. A classificacao e positiva somente
quando o artefato exerce ao menos uma destas seis funcoes operacionais:
`agent-facing`, `instruction-bearing`, `routing`, `prompt-assembly`,
`context-hydration` ou `validation-contract`. Um artefato exclusivamente
humano, que nao exerce nenhuma dessas funcoes, recebe `not-applicable` com uma
justificativa concreta; autoria por LLM, Markdown/YAML, densidade tecnica ou
possivel retrieval incidental nao tornam o artefato aplicavel.

A fonte canonica dos schemas, rubrica, prompt, fixtures, derivacao de status e
protocolo de replay e o
[LLM Artifact Quality Validation Contract](../skills/lf-documentation-writing/references/llm-artifact-quality-validation.md).
Nao copie esses detalhes para agents, creators, commands ou docs. Use tambem os
requisitos de autoria LLM-facing roteados por `lf-documentation-writing`:
autoridade e prioridade recuperaveis, instrucao separada de dados, regras
atomicas, restricoes salientes, unidades de retrieval autocontidas, exemplos
nao normativos, output exato quando houver geracao e incerteza normativa
explicita.

Este gate vale somente para criacao, alteracao ou promocao com
`destination_scope: package`:

1. O `framework-artifact-writer` classifica os arquivos reais, aplica os
   requisitos de autoria, emite `llm_artifact_profile`, particiona os dez IDs
   canonicos entre selecionados e skips justificados e executa apenas checks
   mecanicos e de empacotamento.
2. O Writer entrega arquivos, perfil, checks e limitacoes ao
   `framework-artifact-quality-auditor`; ele nunca preenche
   `llm_consumption_quality` nem aprova o proprio artefato.
3. O Auditor permanece read-only e independente. Para artefato aplicavel, usa
   `llm-artifact-quality-v1`, `rubric-v2`, `prompt-v2`, todas as heuristicas,
   fixtures aplicaveis, revisao isolada e bias controls. Para human-only,
   valida a justificativa e retorna `not-applicable` sem executar fixtures
   irrelevantes.
4. Finding, inconclusao, baixa confianca material, fixture aplicavel omitido,
   skip injustificado, bias check falho ou validator falho bloqueiam. Conflito
   entre fontes normativas retorna `needs-human-review` para
   `technical-review`; nunca produz approval condicional.
5. Toda correcao invalida o parecer anterior. Repita checks mecanicos, nove
   criterios, fixtures aplicaveis, bias controls e revisao isolada sobre o
   estado corrigido antes de reutilizar qualquer resultado terminal.

Pare e retorne o bloqueador minimo se a aplicabilidade, classe, prioridade de
fontes, perfil, particao 10/10 ou campo obrigatorio nao puder ser estabelecido;
se a revisao exigir credencial, SDK, automacao de provider, score numerico ou
raciocinio privado; se o pacote isolado revelar diagnostico, autoria, expected
answer ou parecer anterior; se Writer e Auditor forem a mesma autoridade; se
source/projection divergirem; ou se a mudanca ampliar targets, permissoes ou
semantica aprovada. O gate nao altera routing, owners, validators, formatos ou
permissoes de destinos consumer, runtime, backlog ou qualquer outro destino
nao-package.

Ao concluir uma mudanca no pacote, validar pelo menos:

```bash
find "$PACKAGE_ROOT"/skills -maxdepth 2 -name SKILL.md | sort
find "$PACKAGE_ROOT"/skills -maxdepth 1 -type f -name '*.md'
```

Quando `SKILL.md` apontar para arquivos locais em `references/`,
`docs/`, `templates/`, `scripts/` ou outro caminho relativo do pacote, valide
que o alvo existe a partir do arquivo que contem o link. Referencias quebradas
em projeções de comando sao falha de empacotamento: corrija o link, adicione o
arquivo ausente ou registre backlog tecnico antes de tratar o pacote como
instalavel.

Quando a mudanca tocar superficies duraveis do pacote, rode primeiro um scan
focado nos artefatos duraveis alterados ou nas superficies consolidadas
aplicaveis. Esse scan focado e o decisor para a mudanca escopada:

```bash
find skills agents codex scripts templates docs README.md index.md manifest.yaml install-scopes.json -type f \
  ! -path 'docs/package-authoring-guardrails.md' \
  ! -path '*/docs/package-authoring-guardrails.md' \
  ! -path 'skills/lf-skill-creator/references/validation-and-forward-testing.md' \
  ! -path '*/skills/lf-skill-creator/references/validation-and-forward-testing.md' \
  -print0 | xargs -0 rg -n "(Jhonny/|docs/05-Loki-Framework/001-blueprint-aprovado|/Users/|~/|source_plan|canonical_blueprint|operational_plan|historical_reference)"
```

Use o scan amplo abaixo como auditoria bruta do repositorio. Ele pode ser
ruidoso quando incluir `planos/**`, mirrors instalados, referencias externas,
historico local, `.git` ou binarios; nesse caso, registre o ruido e conclua a
validacao da mudanca pelo scan focado nas superficies duraveis afetadas.

```bash
find "$PACKAGE_ROOT" -type f \
  ! -path 'docs/package-authoring-guardrails.md' \
  ! -path '*/docs/package-authoring-guardrails.md' \
  ! -path 'skills/lf-skill-creator/references/validation-and-forward-testing.md' \
  ! -path '*/skills/lf-skill-creator/references/validation-and-forward-testing.md' \
  -print0 | xargs -0 rg -n "(Jhonny/|docs/05-Loki-Framework/001-blueprint-aprovado|/Users/|~/|source_plan|canonical_blueprint|operational_plan|historical_reference)"
```

Tambem validar YAML/frontmatter e paths do manifesto. Quando a mudanca tocar
guidance de modelo ou effort, validar que `docs/model-effort-guidance.md`
continua sendo a referencia central e que IDs concretos de modelos nao foram
duplicados como regra canonica espalhada.

`scripts/validate-install-scopes.py` valida identidade e namespace schema 2.
Todo `skills/loki-*` exige `serialization: skill-bundle`, os tres recursos
minimos locais e roteados, e proibe campos de projection ou contrato pareado.
Chave YAML duplicada e sempre falha.

Para superficies Codex do pacote, validar tambem:

```bash
python3 scripts/validate-install-scopes.py
python3 scripts/install-loki-symlinks.py --dest /tmp/loki-symlink-test --dry-run --profile consumer
python3 scripts/install-loki-symlinks.py --dest /tmp/loki-symlink-test --dry-run --profile package-source
python3 scripts/install-loki-symlinks.py --dest /tmp/loki-symlink-test --dry-run --profile all
python3 - <<'PY'
from pathlib import Path
import tomllib

for path in sorted(Path("codex/agents").glob("*.toml")):
    tomllib.loads(path.read_text(encoding="utf-8"))

agent_names = {path.stem for path in Path("agents").glob("*.md")}
codex_agent_names = {path.stem for path in Path("codex/agents").glob("*.toml")}
missing = sorted(agent_names - codex_agent_names)
if missing:
    raise SystemExit(f"missing Codex agent TOML(s): {', '.join(missing)}")
PY
```

Quando validar um destino instalado por symlink, siga links para inspecionar
conteudo interno:

```bash
find -L /tmp/loki-symlink-test/.agents/skills -maxdepth 2 -name SKILL.md | sort
```

Se uma proposta do Loki apontar para documentacao duradoura do consumidor,
validar tambem:

- o documento-alvo em `/docs` existe ou sera criado explicitamente;
- `docs/index.xml` sera criado ou atualizado na mesma promocao;
- `AGENTS.md` e `CLAUDE.md` recebem apenas roteamento minimo quando houver
  sincronizacao.

## Resultado Esperado

Uma evolucao correta do framework:

- nao depende de memoria da conversa;
- nao reintroduz fontes normativas fora do package root;
- distingue evidencia transitoria de contexto duradouro;
- coloca regras project-wide na superficie certa, inclusive `AGENTS.md`,
  `CLAUDE.md` e `/docs` do consumidor quando aplicavel;
- nao quebra o layout instalavel das skills;
- deixa `manifest.yaml`, docs e contratos coerentes;
- termina com validacao objetiva, nao apenas julgamento subjetivo.
# Session evidence guardrail

Execution evidence is provider-neutral and evidence-first. The orchestrator
owns correlation and may persist only a structurally sanitized snapshot plus a
verified manifest. Raw runtime payloads, private/full chain-of-thought,
automatic agent retrospectives, dual capture and legacy fallback are forbidden.
Adapters must expose `partial`, `pointer-only`, `unavailable`, or `unsupported`
when a capability is not observed. TTL, purge and full PII hardening remain
deferred backlog work, not implemented guarantees.
