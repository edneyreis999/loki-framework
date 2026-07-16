# loki-tech-analysis — Execution Contract

## Execution

## Evidence-First Cutover

Cada subagente devolve completion record; o orquestrador captura evidence
sanitizada após o handoff ou registra `partial`, `unavailable` ou `unsupported`.
Não registrar CoT privado nem invocar retrospectiva automaticamente.

### Propósito e estado verificável

Produza uma análise técnica baseada em evidências antes de plano ou execução.
O workflow começa somente quando `Input` entrega um registro normalizado e
validado. Ele termina quando a análise Markdown contém todos os campos exigidos,
passa nos validators aplicáveis e recomenda, com justificativa, o próximo
handoff; ou termina em estado `blocked` com retomada suficiente.

O resultado verificável inclui: mapa de fontes; fatos, inferências, hipóteses e
perguntas abertas separados; superfícies e integrações afetadas; contratos de
estado; research gate; matriz de decisão; recomendação; riscos; validators;
gates humanos; impacto documental e de pacote; decisão explícita sobre
`human_decision_preflight.required`; próximo comando; perfil de execução
downstream; e resume state.

### Papel do orquestrador

Atue como orquestrador das fases `Input`, `Execution` e `Response`: coordene o
fluxo, decomponha o trabalho, selecione agentes responsáveis, forneça a cada
subagente contexto autocontido, acompanhe todos os handoffs até sucesso, falha,
bloqueio ou parada explícita, aplique validators, gates e approvals e consolide
resultados, evidências, riscos e próximos passos. Preserve responsabilidade pelo
estado global após delegar; invocar um agente não conclui a unidade de trabalho.

Antes de qualquer ação, transforme o registro normalizado em um plano com
etapas, dependências, responsáveis, validators e critérios de conclusão.
Replaneje explicitamente quando nova evidência invalidar uma etapa posterior.

### Dependências e roteamento

- Carregue a skill obrigatória `lf-tech-analysis-authoring` e leia integralmente
  o contrato que ela exigir.
- Carregue `lf-template-library` e use seu roteamento para o template de análise
  técnica. Quando a wrapper não estiver disponível, use diretamente
  `templates/technical-analysis-template.md` dentro do package root; não invente
  headings substitutos.
- Carregue `lf-index-navigator` somente quando a análise depender de documentação
  duradoura do consumidor em `/docs` e ele estiver disponível.
- Carregue `<technology_required_skills>` somente por pedido do usuário, contexto
  detectado ou retrospectiva que indique uma skill especializada aprovada.
- `required_commands` é vazio: recomendações de próximo comando são handoffs,
  não dependências necessárias para produzir a análise.

### Plano de agentes e contexto autocontido

Identifique agentes, validators, gates, approvals, owner de cada escrita,
handoffs de sucesso e falha e critérios de parada. Delegue trabalho ao agente
apropriado sempre que disponível:

- `source-researcher`, read-only, para fontes múltiplas, desconhecidas, ruidosas,
  conflitantes, pesquisa externa aprovada ou hipótese material que exija mais
  que uma ou duas leituras locais simples;
- `bibliotecario`, read-only, quando for necessário navegar documentação
  duradoura por `docs/index.xml`;
- `technical-implementer`, proposal-only, para propor abordagem sobre superfície
  técnica sem aplicar alterações;
- `runtime-qa`, proposal-only, para propor checklist especializado de validators,
  riscos e gate humano sem declarar runtime validado.

Execute em paralelo apenas handoffs read-only ou proposal-only independentes.
`technical-implementer` e `runtime-qa` podem trabalhar em paralelo depois que as
superfícies ou hipóteses técnicas forem conhecidas. Consolide fontes, conflitos,
riscos e gates antes da matriz de decisão. O `source-researcher` entrega
evidência e não escolhe a solução.

Para cada subagente, entregue explicitamente: objetivo e motivo; unidade de
trabalho; fatos e decisões; arquivos, documentos e evidências a consultar;
dependências e resultados anteriores; escopo; `allowed_writes` e
`forbidden_writes`; critérios de sucesso, falha e conclusão; validators, gates e
approvals; formato de saída; destino e condições do handoff. Não use referências
implícitas como “conforme discutido” ou “use o contexto acima”. Não invoque um
subagente sem contexto, entrada, escopo, saída e destino definidos.

Registre cada handoff com origem, destino, objetivo, entrada entregue, resultado
esperado, status, evidência recebida e próximo destino. Acompanhe-o até um estado
terminal; handoff aberto impede conclusão.

### Escritas, owners e limites

`allowed_writes`:

- o `destination` Markdown exato dentro do plano ativo;
- arquivo de interação exato sob `interaction/faseN/` do plano ativo quando uma
  pergunta humana precisar ser persistida.

`forbidden_writes`:

- runtime, engine, framework, código, configuração, schemas, dados gerados,
  assets ou superfícies sensíveis do consumidor;
- qualquer caminho fora de `allowed_scope` ou não listado em `allowed_writes`;
- docs consolidados sem task e approval de promoção;
- `.claude/**`, `.agents/**` e `.codex/**`;
- qualquer superfície declarada em `forbidden_surfaces`.

Defina um único owner por arquivo. Permita leituras independentes em paralelo,
mas detecte sobreposição e serialize toda escrita em alvo compartilhado.
Interrompa escritores concorrentes ao detectar conflito.

Quando houver criação ou alteração de arquivo, selecione um `Write Agent`
apropriado e entregue envelope com arquivos-alvo, alteração autorizada,
`allowed_writes`, `forbidden_writes`, owner único, validators, gates, approvals,
evidências esperadas e destino de handoff. Não escreva diretamente quando esse
agente existir e estiver autorizado para o destino.

Escreva diretamente apenas depois de verificar e registrar que nenhum `Write
Agent` apropriado está disponível. Conveniência, velocidade ou tamanho não são
justificativas. Antes da exceção, assuma e registre: alvo exato, owner único,
allowed e forbidden writes, validators, gates, approvals, critérios de sucesso
e falha e evidências obrigatórias. Pare se a escrita exigir escopo ou permissão
adicional. Quando escrever diretamente, registre no completion record o tipo
de implementação, a ausência do agente, a oportunidade e o escopo de um futuro
`Write Agent`, as evidências e os riscos; não conclua sem esse registro.

### Fluxo de análise

1. Confirme objetivo, fontes, escopo, fora de escopo, destino, forbidden writes
   e instruções do projeto (`AGENTS.md`, `CLAUDE.md` ou equivalente).
2. Carregue as dependências e o template pelos roteamentos acima. Não torne
   skills de tecnologia obrigatórias por default.
3. Leia fontes locais primárias antes de docs interpretativos: arquivos-alvo,
   configuração runtime, schemas, IDs, contratos, dados gerados e integrações.
4. Construa o mapa de fontes com caminho/identificador, tipo, evidência extraída
   e uso. Separe cada afirmação material como fato, inferência, hipótese ou
   pergunta aberta.
5. Para cada hipótese material, faça uma ou duas leituras ou buscas locais que
   possam confirmá-la ou rejeitá-la. Descarte hipótese rejeitada; mantenha a não
   resolvida apenas como risco, pergunta ou condição de parada.
6. Aplique o research gate somente depois do mapa local. Pesquise externamente
   se o usuário pedir ou se a decisão depender de informação atual de biblioteca,
   framework, engine, API, plugin, segurança, licença ou compatibilidade. Prefira
   documentação oficial, repositórios primários e release notes. Registre fonte,
   versão/data quando relevante, fato e impacto. Não substitua estado local por
   fonte externa; registre conflitos e associe validator ou decisão humana.
7. Compare em matriz as alternativas aplicáveis: solução local/nativa,
   dependência/plugin/framework, implementação customizada e defer/bloqueio.
   Associe evidência, trade-offs, riscos e validators a cada opção.
8. Declare superfícies afetadas, integrações, contratos de estado, dados,
   schema, IDs ou persistência, validators, gates humanos, riscos e docs afetados.
9. Escreva a análise usando o template técnico. Inclua frontmatter, source
   request, objetivo, esforço, escopo, fontes, evidências classificadas,
   research gate, matriz, recomendação, mitigação, validators, human gates,
   stop conditions, handoff, perfil downstream e resume state.
10. Se a mudança tocar o próprio pacote, declare impacto em `manifest.yaml`,
    docs, templates, commands, agents, scripts e skills aplicáveis; aplique
    `docs/package-authoring-guardrails.md`. Atualize `manifest.yaml` somente
    quando artefatos forem adicionados, removidos, renomeados ou movidos, e
    valide que referências normativas continuam internas ao package root.
11. Decida explicitamente `human_decision_preflight.required`. Recomende
    `loki-human-decision-preflight` quando decisões humanas pré-plano permanecerem;
    caso contrário, justifique e recomende `loki-generate-action-plan`.
12. Rode todos os validators e gates antes de declarar o artefato pronto.

### Validators, gates e approvals

Valide objetivamente que:

- toda recomendação tem fonte, cadeia de inferência ou assumption explícita;
- hipóteses não confirmadas estão marcadas e não aparecem como fatos;
- superfícies afetadas, forbidden writes, integrações e contratos estão declarados;
- research foi realizado com citações ou pulado com motivo, sem substituir
  evidência local;
- validators e gates humanos correspondem às superfícies afetadas;
- a decisão de preflight, o próximo comando e o handoff estão explícitos;
- a análise alimenta o próximo comando e pode ser retomada sem memória do chat;
- referências e caminhos citados existem, ou aparecem como `TODO: localizar`
  com risco/stop condition explícito;
- mudanças no pacote declaram os artefatos normativos impactados e passam pelos
  checks de autoria aplicáveis.

Aplique `interview` para lacunas de requisito, `technical-review` para mudança
de política ou contrato e `human-validation` apenas como gate futuro para
execução que afete comportamento perceptível, runtime, integração ou estado
persistido. Verifique o resultado antes de continuar. Pare quando validator,
gate ou approval obrigatório estiver ausente, pendente, rejeitado ou falhar;
validação automática não substitui gate humano.

### Condições de parada e retomada

Pare quando houver: `analysis_input` ausente; fonte mínima insuficiente; escopo
ou permissão insuficiente; pedido para implementar antes de aprovação; gate ou
approval pendente; validator ausente ou falho; risco blocker sem alternativa;
conflito entre escritores; handoff sem destino ou ainda aberto; dependência
indisponível; pesquisa externa conflitante sem validator; decisão humana
necessária; ou impossibilidade de definir validators e gates para as superfícies.

Ao parar ou concluir, preserve no artefato ou registro de interação: estado
atual, entrada normalizada, etapas concluídas, fontes lidas, research gate,
fatos, hipóteses, riscos, handoffs, pendências, evidências, validators, gates,
próxima ação e condição para continuar. Retome desse estado; não reinicie o
fluxo quando a continuação segura for possível.
