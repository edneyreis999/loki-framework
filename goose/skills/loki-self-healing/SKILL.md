---
name: loki-self-healing
description: Use como conhecimento especializado de self-healing do pacote Loki: critérios de auditoria, classificação de achados, limites de escrita, validadores e neutralidade de artefatos, enquanto a Goose Recipe/command orquestra input, execução, handoffs e resposta.
---

# loki-self-healing

## Papel da skill

Esta skill encapsula o conhecimento especializado de self-healing do pacote Loki. Ela **não** deve substituir a Goose Recipe/command como orquestrador.

Use a Goose Recipe para coordenar:

- coleta e validação de parâmetros;
- resolução de escopo;
- decisão de delegar ou escrever diretamente;
- handoffs;
- execução de validadores;
- resposta final ao usuário.

Use esta skill para aplicar critérios consistentes de auditoria, classificação de achados, correção conservadora, limites de escrita e validação.

## Quando usar

Use quando o usuário pedir self-healing, auditoria ou correção automática de artefatos internos do Loki a partir de:

- arquivo do pacote;
- diretório do pacote;
- workflow Loki;
- arquivos staged;
- conjunto explícito de artefatos internos.

## Leitura mínima antes de corrigir

Antes de qualquer patch, leia contexto suficiente para entender o todo:

- `install-scopes.json`;
- `docs/operational-inventory.md`;
- `manifest.yaml`;
- `docs/package-authoring-guardrails.md`;
- `docs/model-effort-guidance.md` quando houver `model`, `effort`, `execution_profile` ou `adapter_projection` no escopo;
- contratos de commands, skills, agents, templates, docs, scripts e instalador relacionados ao escopo.

## Classificação de install scope

Antes de escrever em `commands/**` ou `skills/**`, classifique cada arquivo via `install-scopes.json`:

- `internal-only`;
- `both`;
- `consumer-only`;
- `unclassified-blocker`.

Não edite arquivo `unclassified-blocker`. Para artefatos `both`, aplique checklist de neutralidade antes de qualquer correção.

## Checklist de auditoria

Avalie cada arquivo selecionado contra:

- propósito, triggers, entradas, saídas, limites, validators, gates e resume behavior;
- consistência com convenções de command, skill, agent, template, doc ou script;
- metadados obrigatórios e orientação provider-neutral para modelo/esforço;
- referências internas resolvíveis por progressive disclosure;
- sincronização com manifest, inventário, install scopes, instalador e referências;
- ausência de dependência normativa em `planos/**`, `.agents/**`, `.claude/**`, `.codex/**`, paths absolutos de usuário ou runtime de consumidor;
- limites de autonomia, gates humanos, escrita serializada e validação proporcional;
- ausência de duplicidade, ruído, conflito ou instrução ambígua;
- resposta final acionável e testável.

## Classificação de achados

Classifique cada achado como:

- `corrigir agora`: claro, escopado, verificável, coerente com regras do pacote e baixo risco;
- `nao alterar`: já coberto ou mudança adicionaria ruído;
- `investigar`: promissor, mas com evidência insuficiente ou escopo amplo demais;
- `fora de escopo`: fora do escopo e não obrigatório para consistência;
- `bloqueado`: requer decisão humana, pesquisa externa ou forbidden write.

Aplique somente achados `corrigir agora`.

## Política de correção

- Consolide achados antes de escrever.
- Escreva serialmente usando o menor patch coerente.
- Não permita escrita paralela no mesmo arquivo.
- Preserve o estilo do pacote.
- Não amplie silenciosamente o escopo, exceto arquivos obrigatórios de consistência quando o orquestrador permitiu.
- Se a Goose Recipe escrever diretamente por falta de Write Agent especializado, registre isso como exceção e oportunidade de melhoria na resposta/retrospectiva.
- Se a correção for catalogação documental em `docs/**`, considere delegar a um agente `catalogador` pós-approval quando existir handoff aprovado suficiente; não trate `catalogador` como proposal-only.

## Validadores recomendados

- `find skills -maxdepth 2 -name SKILL.md | sort`
- `find skills -maxdepth 1 -type f -name '*.md'`
- Validação de frontmatter de skills: `name`, `description` e nome da pasta.
- Validação de paths do `manifest.yaml`.
- `python3 scripts/validate-install-scopes.py` quando tocar `commands/**`, `skills/**` ou superfícies instaláveis.
- `python3 scripts/install-loki-symlinks.py --dest /tmp/loki-symlink-test --dry-run --profile package-source` quando tocar skills, commands, agents, templates, scripts ou instalador.
- Validadores específicos do artefato corrigido quando houver.

## Limites

- Não edite fora do package root.
- Não edite `.claude/**`, `.codex/**`, `.agents/**` nem destinos instalados.
- Não altere índice git, stage ou commit.
- Não edite runtime, engine, framework externo ou projeto consumidor.
- Não aplique reescritas especulativas; marque como `investigar` ou `bloqueado`.
- Não use self-healing para aprender diretamente de fontes externas atuais; quando necessário, pare ou use workflow de pesquisa/análise apropriado.

## Gates e parada

Não há approval prévio por arquivo dentro de um escopo claro recebido do usuário, mas revisão humana posterior via diff/staging manual é obrigatória.

Pare quando:

- o escopo não puder ser resolvido;
- o escopo apontar para fora do package root;
- a única correção possível exigir forbidden write;
- a correção depender de informação externa atual ou decisão de produto ausente;
- houver conflito interno sem critério claro;
- uma edição em `commands/**` ou `skills/**` depender de install scope ausente.
