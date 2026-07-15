# Execution — loki-self-healing

## Execution

Use este contrato para a fase de execução.

## Purpose And Observable Contract

Este command orquestra auditoria e correção interna do pacote Loki no working
tree. Inicia com escopo normalizado dentro do package root; termina com análises
individuais consolidadas, correções de baixo risco aplicadas serialmente,
validators proporcionais executados e relatório revisável. Produz source map,
achados classificados, patches, arquivos alterados, validações e riscos; nunca
faz stage, commit, reset ou checkout.

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha unidades, selecione agentes,
forneça contexto autocontido, acompanhe handoffs até sucesso, falha, bloqueio ou
parada, aplique validators/gates e consolide achados, evidências, riscos e
próximos passos. Delegação não transfere responsabilidade pelo estado global.

## Classification And Required Audit References

Classifique pela identidade operacional, não pelo diretório:

- bundle `skills/loki-<stem>/` com `type: command` e
  `serialization: skill-bundle`: command; audite a unidade inteira;
- `lf-*` e skills de domínio/tecnologia: skill;
- `agents/**` e projeções: agent.

Para command bundle, leia [how-to-improve-command.md](how-to-improve-command.md)
e avalie SKILL, todos os references roteados e o response template como uma
unidade 24/24. Para skill, leia
[how-to-improve-skills.md](how-to-improve-skills.md). Para agent, leia
[how-to-improve-agents.md](how-to-improve-agents.md). Não exija command físico
pareado e não classifique bundle command como knowledge skill.

## Scope Resolution And Global Context

Resolva arquivo, diretório, workflow ou staged. Encontre o package root por
`manifest.yaml`, `skills/`, `agents/` e `docs/`. Para workflow, mapeie bundle, helper skills,
references, assets, templates, docs, manifest, inventory, routers e installer.
Leia `README.md`, `install-scopes.json`, `docs/operational-inventory.md`,
`manifest.yaml`, `docs/package-authoring-guardrails.md` e artefatos relacionados.
Classifique cada command/skill como internal-only, both, consumer-only ou
unclassified-blocker; não edite blocker e aplique neutralidade a `both`.

## Plan, Analysis And Handoffs

Monte source map com escopo, candidatos, install scopes, fontes, relações,
validators e forbidden writes. Planeje análises, responsáveis e critérios;
replaneje quando achado ou validator invalidar etapa posterior. Delegue análise
read-only por arquivo/grupo independente quando possível; cada handoff retorna
somente achados/propostas.

Antes do subagente, forneça objetivo/motivo, unidade, fatos, decisões,
restrições, fontes, dependências, allowed/forbidden writes, owner, critérios,
validators, gates, formato e destino. Registre origem, destino, objetivo,
entrada, resultado esperado, status, evidência e próximo destino; acompanhe até
terminal. Se não houver paralelismo, mantenha subseções independentes.

## Findings And Corrections

Avalie clareza, contrato, metadata, refs, sincronização, autonomia, gates,
validators, neutralidade, redundância, conflito e actionability. Classifique
como `corrigir agora`, `nao alterar`, `investigar`, `fora de escopo` ou
`bloqueado`. Corrija somente mudança clara, escopada, verificável, coerente e de
baixo risco. Consolide primeiro; aplique o menor patch coerente serialmente;
preserve estilo e não amplie escopo. Arquivo obrigatório de consistência só
entra quando a correção realmente o exigir.

## Allowed And Forbidden Writes

Allowed dentro do escopo: `skills/**`, `agents/**`, `codex/agents/**`,
`templates/**`, `docs/**`, `README.md`, `index.md`, `manifest.yaml`, `scripts/**`
e artefatos de consistência obrigatórios. Forbidden:
qualquer alteração de índice Git, `.claude/**`, `.codex/**`, `.agents/**`, fora
do package root, runtime/engine/framework/consumidor e mudança desnecessária fora
do escopo.

## Write Ownership And Direct-Write Exception

Leituras independentes podem ser paralelas; toda escrita é serial e tem owner
único. Delegue patch a Write Agent com targets, allowed/forbidden writes,
validators, gates e evidência. Escrita direta só após registrar inexistência de
writer apropriado; conveniência não justifica. Declare envelope completo e
registre na retrospectiva tipo de implementação, motivo, oportunidade/escopo do
futuro writer, evidências e riscos. Pare diante de overlap ou permissão ausente.

## Validators And Human Gates

Execute checks estruturais, frontmatter/nome de pasta, paths do manifest,
forbidden-reference scan, dry-run do installer quando tocar superfícies
instaláveis e validators específicos. Para command bundle, registre exatamente
24 respostas `sim|não`, arquivo, heading/trecho e contradições; corrija todo
`não` antes de classificar como aprovado. Não há approval por arquivo dentro do
escopo solicitado; há revisão humana posterior obrigatória do diff. Pergunte
somente quando o escopo não resolve, sair do root ou regras conflitarem. Pare se
validator/gate estiver ausente, pendente ou falhar.

## Stop Conditions

Pare sem escopo/staged; fora do root; com única correção proibida; dependência
de pesquisa externa/decisão ausente; conflito interno sem desempate; install
scope ausente; handoff sem destino; conflito de writers; validator falho; ou
correção que exija ampliar o envelope. Não declare conclusão com condição ativa.

## Resume Contract

Registre escopo, candidatos, fontes, install scopes, source map, análises por
arquivo/bundle, score 24/24 quando aplicável, achados, correções, owners,
handoffs, arquivos alterados, validators/falhas, gates, itens não alterados,
riscos e próximo passo do usuário. Retome desse estado sem reiniciar.
