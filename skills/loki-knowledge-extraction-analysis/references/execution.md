# Execution — loki-knowledge-extraction-analysis

## Execution

Use este contrato para a fase de execução.

## Purpose And Observable Contract

Este command orquestra extração externa, auditoria de impacto Loki e
consolidação rastreável sem forçar recomendações. Inicia com Input normalizado;
termina quando `external_extraction` e `impact_audit` estão terminais, cada ponto
foi classificado e o relatório contém as 16 seções ou o caso explícito sem
aprendizado útil. O resultado verificável separa observação, interpretação e
recomendação, inclui origem, delta, risco, prioridade, custo, ganho e teste, e
nunca promove mudança duradoura diretamente.

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha o fluxo, selecione responsáveis,
forneça contexto autocontido a cada subagente, acompanhe handoffs até sucesso,
falha, bloqueio ou parada, aplique validators, gates e approvals e consolide
artefatos, evidências, riscos e próximos passos. Delegação não transfere a
responsabilidade pelo estado global.

## Canonical Specialized Contracts

Leia integralmente, nesta ordem:

1. [knowledge-extraction-analysis-contract.md](knowledge-extraction-analysis-contract.md),
   que preserva fontes, taxonomia, processo, auditorias e as 16 seções;
2. [output-contract.md](output-contract.md), que fixa consolidação, valores,
   learning entry, buckets e o caso sem aprendizado útil.

Em conflito, preserve não-forçamento e a saída mais específica; registre o
conflito em vez de inferir silenciosamente.

## Dependencies

Carregue `lf-external-knowledge-extraction` primeiro e produza
`external_extraction`. Só depois carregue `lf-framework-impact-audit`, leia
`docs/operational-inventory.md` ou declare sua ausência e produza
`impact_audit`. `loki-continuous-improvement` é apenas o próximo handoff depois
da análise, nunca executor implícito desta etapa.

## Planning, Agents And Self-Contained Handoffs

Transforme a entrada normalizada em plano com etapas, dependências, responsáveis,
validators e critérios. Replaneje se extração, inventário, conflito ou auditoria
invalidar uma etapa posterior. Delegue pesquisa read-only a `source-researcher`
quando as fontes forem numerosas, conflitantes, incompletas ou dependerem de
pesquisa aprovada; use `standards-curator` proposal-only para possível mudança
normativa. Se paralelismo não existir, mantenha auditorias individuais separadas.

Antes de qualquer subagente, forneça objetivo e motivo, unidade, fatos,
decisões, restrições, fontes, dependências, allowed/forbidden writes, owner,
critérios, validators, gates, formato esperado e destino do handoff. Registre
origem, destino, objetivo, entrada, resultado esperado, status, evidência e
próximo destino; acompanhe até estado terminal. Não delegue com contexto
implícito.

## Non-Forcing Workflow

1. Extraia observações externas sem decidir mudança Loki.
2. Audite individualmente os artefatos e workflows Loki potencialmente afetados.
3. Consolide handoffs sem duplicar recomendações equivalentes.
4. Classifique cada ponto como `adotar`, `adaptar`, `rejeitar`,
   `ja contemplado`, `investigar` ou `sem aprendizado util`.
5. Recomende somente quando houver problema real, compatibilidade ou rejeição
   consciente, mudança concreta, origem rastreável e ganho não redundante.
6. Registre pontos rejeitados, já contemplados, lacunas e conflitos.
7. Produza as 16 seções e encaminhe candidatos validados para
   `loki-continuous-improvement`.

Não invente cobertura Loki, não transforme semelhança em recomendação e não
preencha seções com recomendações artificiais.

## Allowed And Forbidden Writes

Allowed: relatório Markdown transitório no plano/destino aprovado e registros de
perguntas/decisões na interaction do plano ativo. Forbidden: alterações diretas
em command bundles, skills, agents, templates, validators, docs consolidados,
manifest, contexto consumidor, runtime ou superfícies sensíveis; `.claude/**`,
`.codex/**` e `.agents/**` sem approval explícito. Não amplie o envelope.

## Write Ownership And Direct-Write Exception

Leituras independentes podem ser paralelas; serialize toda escrita e atribua um
owner único por arquivo. Delegue qualquer criação/modificação a Write Agent com
targets, alteração, allowed/forbidden writes, validators, gates e evidência.
Escrita direta só após registrar que nenhum Write Agent apropriado existe;
conveniência não justifica. Nesse caso, declare o envelope completo e registre
na retrospectiva tipo de implementação, ausência, oportunidade do futuro writer,
escopo, evidências e riscos. Pare diante de overlap ou permissão insuficiente.

## Validators

- observação, interpretação e recomendação estão separadas;
- cada recomendação tem origem externa e delta Loki rastreáveis;
- `external_extraction` precede `impact_audit`, que precede consolidação;
- inventário operacional foi lido ou sua ausência declarada;
- pontos contemplados, rejeitados, incompatíveis ou fracos não viram mudança;
- cada candidato implementável inclui teste; as 16 seções estão completas;
- nenhuma cobertura foi inventada e nenhuma promoção duradoura foi aplicada;
- writers/handoffs estão terminais e evidenciados.

## Human Gates

Use `interview` para fonte, escopo ou destino insuficiente; `technical-review`
para recomendação que afete artefato Loki duradouro; `approval` para promoção,
instalação ou escrita sensível; e consentimento explícito para pesquisa externa.
Pare quando qualquer controle obrigatório estiver ausente, pendente, rejeitado
ou falho. Validator não substitui decisão humana.

## Packaging Checks

Classifique explicitamente se cada recomendação posterior tocaria o pacote
Loki, o contexto duradouro do consumidor ou backlog. Se tocar o pacote, o
handoff para `loki-continuous-improvement` deve carregar e aplicar
`docs/package-authoring-guardrails.md` antes de qualquer patch. Esta análise não
concede autorização de promoção.

## Stop Conditions

Pare sem artefato externo; sem contexto para distinguir Loki da fonte; quando o
pedido exigir aplicar mudança antes da análise; diante de pesquisa externa não
autorizada, dependência indisponível, handoff sem destino, conflito de writers,
validator falho, gate/approval pendente, escopo insuficiente ou saída sem
evidência. Não declare conclusão com condição ativa.

## Resume Contract

Registre fontes externas, Loki artifacts, inventário/limitação, etapas e
auditorias concluídas, handoffs e estados, aprendizados, rejeições, lacunas,
conflitos, owner/writes, validators, gates, decisões, próxima ação e condição de
retomada. Retome desse estado sem reiniciar quando ele for suficiente.
