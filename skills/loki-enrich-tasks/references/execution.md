# Execution — loki-enrich-tasks

## Purpose And Observable Contract

Este command é o orquestrador que revisa e enriquece somente as tasks da fase
ativa usando evidência transitória, sem mudar o objetivo da fase, expor a fonte
interna ou promover regra duradoura.

- Início: registro normalizado do Input, com quatro parâmetros obrigatórios
  válidos, uma única fase resolvida e fronteiras de escrita conhecidas.
- Conclusão: tasks aplicáveis foram enriquecidas ou preservadas com motivo;
  validators e gates foram processados; cada handoff atingiu estado terminal;
  e não resta condição de parada ativa.
- Resultado verificável: patch aplicado ou proposto apenas para a fase atual,
  resultado do research gate, decisões e pendências humanas, observações locais
  para retrospectiva e backlog fora de escopo.
- Saídas obrigatórias: cumpra integralmente `references/response.md`.

## Execution Profile

```yaml
execution_profile:
  model_class: generalist
  default_effort: medium
  max_effort: high
  escalation_signals:
    - conflicting retrospective or build evidence
    - enrichment changes execution order, scope, or gates
    - durable package policy may be affected
  handoff_effort:
    research: medium
    coding: medium
    documentation_transient: low
    documentation_durable: high
    validator: low
```

## Orchestrator Responsibilities

Coordene as fases Input, Execution e Response. Decomponha o trabalho em
unidades com responsáveis identificáveis, selecione os agentes apropriados,
forneça a cada subagente contexto de execução autocontido, acompanhe todos os
handoffs até sucesso, falha, bloqueio ou parada explícita, aplique validators,
gates e approvals, e consolide status, artefatos, evidências, riscos e próximos
passos. Delegar não transfere a responsabilidade pelo progresso nem pelo estado
global do fluxo.

## Dependencies

```yaml
required_skills: []
required_commands: []
```

Carregue skill de tecnologia somente quando uma task realmente depender dela.
Não transforme essa carga condicional em dependência permanente do command.

## Allowed And Forbidden Writes

Derive do registro normalizado e enumere como `allowed_writes` exatos:

- o path concreto de `TASKS_MD`;
- apenas os `task-N.M.md` pertencentes a `FASE_ATUAL` e referenciados pelo plano;
- apenas arquivos necessários dentro de `interaction/faseN/` da fase resolvida;
- quando houver escrita direta excepcional, um registro de retrospectiva
  técnica da fase ativa, dentro do plano e explicitamente autorizado.

Tudo o mais é proibido. Em especial, `forbidden_writes` inclui:

- tasks de fases anteriores ou futuras;
- as fontes lidas em `DIR_RETROSPECTIVAS`, `DIR_BUILDS` e
  `INTERACTIONS_RELEVANTES`;
- `AGENTS.md`, `CLAUDE.md` e contexto duradouro do consumidor;
- commands, skills, agents, templates, validators, docs consolidados,
  `manifest.yaml` e `install-scopes.json`;
- runtime, engine, framework, `<consumer_runtime_surfaces>` e
  `<sensitive_write_patterns>` fora do escopo aprovado;
- `.claude/**`, `.agents/**` e `.codex/**`.

Não amplie silenciosamente essas fronteiras. Pare quando a melhoria exigir path
ou permissão não autorizada.

## Execution Planning And Replanning

1. Consuma o registro normalizado; não reinterprete o pedido bruto de modo
   ambíguo.
2. Leia `TASKS_MD`, identifique todas as tasks de `FASE_ATUAL` e localize seus
   `task-N.M.md` antes de ler aprendizados antigos.
3. Monte um plano com etapas, dependências, responsáveis, leituras, possíveis
   escritas, validators, gates, handoffs e critérios de conclusão.
4. Antes do fan-out, detecte sobreposição entre arquivos alvo e atribua um único
   owner por arquivo em cada momento.
5. Replaneje explicitamente quando uma evidência invalidar escopo, ordem,
   owner, validator, gate ou etapa posterior. Registre o impacto; não continue
   com um plano obsoleto.

## Context Extraction

Antes das fontes transitórias, entenda para cada task:

- objetivo e escopo técnico;
- dependências e decisões já documentadas;
- arquivos prováveis, `target_files`, `allowed_writes` e
  `scoped_write_domains`;
- write owner e sensibilidade da escrita;
- riscos, validators, critérios de sucesso e human loops.

Depois analise retrospectivas, builds e interactions por arquivo ou lote
pequeno. Leituras independentes podem ocorrer em paralelo. Para cada fonte,
consolide internamente aprendizados técnicos, relação com a fase, tasks
afetadas, instrução concreta sugerida, leitura adicional necessária e
confiança. Investigue arquivos locais adicionais somente quando necessários
para provar a aplicabilidade no escopo atual.

## Agents, Handoffs And Delegation

Delegue leitura, pesquisa, proposta, escrita e validação ao agente com a
responsabilidade correspondente sempre que houver agente apropriado. Use
`source-researcher` em modo read-only somente quando o Research Gate autorizar
pesquisa externa ou quando compatibilidade atual, contrato upstream, conflito
entre fontes ou lacuna multifonte exigir análise especializada. Para alterações
do plano, prefira um Write Agent `scoped-writer` aplicável.

Antes de invocar qualquer subagente, forneça um envelope autocontido contendo:

- objetivo e motivo da unidade de trabalho;
- unidade atribuída, fatos, decisões e restrições relevantes;
- paths, documentos, evidências e fontes que deve consultar;
- dependências e resultados anteriores necessários;
- escopo, `allowed_writes` e `forbidden_writes`;
- owner e arquivos alvo quando houver escrita;
- critérios de sucesso, falha e conclusão;
- validators, gates e approvals;
- formato da saída e evidências esperadas;
- destino e condições do handoff.

Não delegue com referências implícitas como “continue”, “use o contexto acima”
ou “faça o restante”. Registre para cada handoff origem, destino, objetivo,
entrada, resultado esperado, status, evidência recebida e próximo destino.
Acompanhe até estado terminal; a mera invocação não conclui a unidade.

## Research Gate

Pesquisa externa é condicional e ocorre somente depois de mapear contexto e
fontes locais. Execute-a apenas quando:

- o usuário pedir internet ou contexto externo atual;
- a decisão depender de documentação atual de biblioteca, framework, engine,
  API, plugin, segurança, licença ou compatibilidade;
- fontes locais explicarem o estado atual, mas não o contrato upstream;
- uma skill técnica exigir documentação oficial atual.

Quando necessário, formule perguntas externas precisas, prefira documentação
oficial, repositórios primários e release notes, e registre fonte, versão/data
quando relevante, fato extraído e impacto na task. Se não necessário, registre
“não necessário” ou “pulado” com motivo verificável.

Pesquisa externa nunca substitui o estado local do consumidor. Se houver
conflito, registre-o e transforme-o em validator, stop condition ou decisão
humana antes de editar.

## Ambiguity Resolution

Pergunte ao usuário somente quando todas estas condições forem verdadeiras:

- existe divergência real entre fontes relevantes;
- a divergência afeta edição ou execução da fase atual;
- as fontes conflitantes parecem aplicáveis ao mesmo escopo;
- não há evidência suficiente para escolher com segurança;
- prosseguir pode causar retrabalho, implementação incorreta ou alteração
  indevida.

Não pergunte quando a divergência não afeta a fase, pertence a outro escopo, é
apenas terminológica, pode ser resolvida lendo artefatos disponíveis ou quando
evidência validada de execução corrige claramente fonte anterior no mesmo
escopo.

| Conflito | Ação |
| --- | --- |
| Task diz X; aprendizado validado e aplicável diz Y | Usar Y sem perguntar |
| Task diz X; aprendizado diz Y, mas o escopo de Y é incerto | Perguntar |
| Aprendizados A e B divergem e ambos são aplicáveis | Perguntar |
| Aprendizado e documento atual divergem; ambos são aplicáveis e plausíveis | Perguntar |
| Aprendizado atual diverge de documento antigo | Usar o aprendizado sem perguntar |
| Dois documentos atuais e aplicáveis divergem | Perguntar |
| A divergência pertence a outro escopo | Ignorar na fase ou registrar fora de escopo |
| A divergência não altera a execução | Não perguntar |

Quando resolver sem perguntar, mantenha registro interno da divergência, fonte
mais confiável, motivo e impacto na edição.

## Editing Rules

- Edite somente os `allowed_writes` enumerados da fase atual.
- Não adicione task, requisito ou objetivo fora da fase, exceto o mínimo
  necessário para impedir erro técnico diretamente ligado à execução aprovada.
- Edite apenas quando a melhoria for clara, aplicável e tecnicamente
  justificada. Não faça reescrita cosmética, de estilo ou reorganização.
- Se a task já refletir corretamente a evidência, preserve-a sem mudança.
- Evite duplicação e preserve a estrutura existente.
- Converta evidência em instrução direta, restrição técnica, owner,
  `target_files`, validator, cuidado de implementação, critério de aceite ou
  nota de compatibilidade.
- Preserve o `Scoped Write Plan`. Altere owner, `target_files`,
  `allowed_writes` ou `scoped_write_domains` somente com evidência concreta de
  redução de risco ou correção de ambiguidade.
- Quando houver `target_files` claros, escrita pesada ou sensível e evidência de
  desperdício/risco por centralizar escrita, selecione `scoped-writer`
  aplicável ou registre justificativa explícita para manter o orquestrador.
- Nunca cite, linke, nomeie ou insinue retrospectivas, builds, arquivos
  analisados, datas de fonte interna ou frases como “foi aprendido
  anteriormente”, “na fase passada” ou “no build anterior” nos artefatos
  editados. Fontes transitórias são contexto interno.
- Não faça handoff normativo direto. Aprendizado aparentemente duradouro vira
  somente observação local para futura `loki-retrospectiva-tecnica`.

## Write Ownership And Serialization

Antes de criar, modificar, mover ou remover arquivo, selecione um Write Agent
apropriado e entregue o envelope completo de escrita. Serialize operações no
mesmo arquivo ou superfície compartilhada; permita apenas leituras realmente
independentes em paralelo. Detecte sobreposição antes do fan-out e interrompa
escritores concorrentes.

O orquestrador pode escrever diretamente somente depois de verificar e
registrar que nenhum Write Agent apropriado está disponível. Conveniência,
velocidade ou tamanho da alteração não justificam a exceção. Antes da escrita
direta, declare paths exatos em `allowed_writes`, `forbidden_writes`, owner
único, alteração autorizada, validators, gates/approvals, critérios de sucesso
e falha e evidências obrigatórias; assuma esse envelope e pare se ele for
insuficiente.

Sempre que escrever diretamente, registre antes de concluir, em retrospectiva
técnica local e autorizada da fase ativa: tipo da implementação, motivo da
ausência de Write Agent, oportunidade de criar/especializar agente, escopo que
o futuro agente deveria assumir, evidências e riscos. Se esse registro não
estiver dentro dos `allowed_writes` ou não tiver autorização, pare e solicite a
decisão necessária; não encerre o fluxo omitindo-o.

## Validators And Human Gates

Execute e verifique cada controle antes da ação dependente:

- paths obrigatórios foram resolvidos e continuam acessíveis;
- somente `FASE_ATUAL` e seus `allowed_writes` foram alterados;
- nenhum texto editado expõe fonte interna sensível;
- nenhuma passagem correta foi reescrita apenas por estilo;
- cada mudança reduz risco real ou ambiguidade concreta e é específica o
  bastante para orientar implementação;
- toda mudança de owner, `target_files`, `allowed_writes` ou
  `scoped_write_domains` tem evidência concreta e não amplia escopo;
- escrita pesada/sensível com `target_files` claros não permanece com o
  orquestrador sem justificativa quando existe `scoped-writer` aplicável;
- pesquisa externa foi citada ou pulada com motivo, sem substituir evidência
  local;
- toda dúvida que mude escopo, ordem, human loop ou critério de sucesso passou
  pelo gate `interview`;
- mudança de política ou artefato duradouro exige `approval`, interrompe a
  edição local e vira observação para retrospectiva, não promoção direta.

Validator automático não substitui gate humano. Pare quando um validator,
gate ou approval obrigatório estiver ausente, pendente, rejeitado ou falhar.

## Stop Conditions

- entrada obrigatória ausente, inválida, inacessível ou ambígua;
- `FASE_ATUAL` não resolve uma única fase ou suas tasks não são determináveis;
- escopo ou permissão insuficiente;
- fontes aplicáveis conflitam sem evidência segura para escolha;
- a edição revelaria fonte interna sensível;
- a melhoria pertence a superfície duradoura do projeto ou pacote;
- gate/approval pendente, ausente ou rejeitado;
- validator ausente ou falho;
- conflito entre escritores ou handoff sem destino;
- dependência indisponível;
- decisão humana necessária;
- pesquisa externa revela conflito material sem validator ou decisão possível.

## Resume Contract

Preserve e comunique: entrada normalizada; fase e tasks alvo; plano atual;
etapas concluídas; arquivos alterados/propostos; fontes usadas apenas em alto
nível e sem exposição sensível; resultado do Research Gate; decisões e
ambiguidades; handoffs e status; owners; validators; gates/approvals;
evidências; observações para retrospectiva; backlog; riscos; pendências;
próxima ação, responsável e condição necessária para continuar. Retome desse
estado, sem reiniciar do zero quando ele for suficiente.
