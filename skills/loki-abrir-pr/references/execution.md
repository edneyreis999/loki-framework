# Execution — loki-abrir-pr

## Purpose And Observable Contract

Este command e o orquestrador que prepara ou abre um Pull Request revisavel a
partir da branch atual, preferindo GitHub MCP e usando `gh` autenticado como
fallback, com titulo/corpo derivados do diff entre base e head.

- Inicio: entrada normalizada e repositorio Git legivel.
- Conclusao: PR criado apos approvals, ou proposta completa pronta para approval,
  ou stop condition explicita.
- Resultado verificavel: URL quando criado, base/head, titulo, corpo, commits,
  estado draft e validators.
- Saidas obrigatorias: siga integralmente `references/response.md`.

## Execution Profile

```yaml
execution_profile:
  model_class: coding
  default_effort: medium
  max_effort: high
  escalation_signals:
    - branch has uncommitted changes
    - branch is not pushed or upstream is ambiguous
    - provider is not GitHub
    - PR body depends on issue tracker or release policy
    - repository has a required PR template
  handoff_effort:
    coding: medium
    validator: medium
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha o trabalho; selecione agentes
responsaveis; forneca contexto autocontido; acompanhe handoffs ate estado
terminal; aplique validators, gates e approvals; e consolide evidencias, riscos
e proximos passos. Delegacao nao transfere a responsabilidade global.

## Allowed Writes

- Push da branch atual para o remote aprovado.
- Criacao do PR no provedor remoto aprovado.

## Forbidden Writes

- Alteracoes no working tree.
- Commits automaticos; use `loki-commit`.
- Merge, auto-merge, labels, reviewers, milestones ou assignees sem pedido.
- `.claude/**`, `.agents/**` e `.codex/**`.

## Required Skills And Commands

```yaml
required_skills: [lf-git-workflow]
required_commands: []
```

Carregue `lf-git-workflow` para preflight, composicao, provider tooling, gates e
validators.

## Tooling

- Prefira GitHub MCP quando houver ferramenta compativel e repo/head/base
  resolvidos.
- Use `gh pr create` apenas como fallback instalado e autenticado.
- Se o remote nao for GitHub, pare; nao assuma GitHub para provider generico.

## Execution Planning And Replanning

Converta a entrada normalizada em plano com leitura de estado, dependencias,
responsaveis, approvals, validators e criterio de conclusao. Replaneje se status,
base, upstream, commits, diff, template ou provider invalidarem etapa posterior.

## Agents, Handoffs And Delegation

Delegue analise/teste/revisao ao agente apropriado quando disponivel; mantenha
no orquestrador a coordenacao e a acao provider-specific aprovada. Cada
subagente recebe objetivo, unidade, fatos, paths/fontes, dependencias, escopo,
allowed/forbidden writes, criterios, validators/gates, saida e destino. Registre
origem, destino, objetivo, entrada, resultado esperado, status, evidencia e
proximo destino; acompanhe ate estado terminal.

## Workflow

1. Carregue `lf-git-workflow`.
2. Leia branch atual, default/base, remote, upstream, `git status --short`,
   commits `BASE..HEAD` e diff `BASE...HEAD`.
3. Havendo mudancas nao commitadas, pare e recomende `loki-commit` ou exclusao
   consciente delas.
4. Confirme que a branch atual nao e base/default.
5. Confirme ou detecte base; pergunte se ambigua.
6. Se a branch nao estiver publicada, mostre remote e obtenha approval antes de
   `git push -u`.
7. Gere titulo convencional a partir dos commits ou argumento.
8. Gere corpo com resumo, motivacao, mudancas, validators e referencias.
9. Mostre titulo e corpo completos para approval.
10. Crie via GitHub MCP; se indisponivel, use `gh pr create` com os mesmos dados.
11. Reporte URL, base/head e draft/ready.

## Write Ownership And Serialization

Detecte sobreposicao e mantenha owner unico para cada side effect. Alteracoes de
arquivo do projeto exigem Write Agent, mas sao proibidas por este workflow. Para
push/PR, selecione agente autorizado se existir; escrita direta pelo orquestrador
so ocorre apos registrar ausencia de Write Agent apropriado e um envelope com
remote/base/head, allowed/forbidden writes, validators, approvals, sucesso/falha
e evidencias. Serialize push e criacao de PR.

Se houver escrita direta, registre no completion record tipo, motivo da ausencia
do agente, oportunidade de especializacao, escopo futuro, evidencias e riscos.

## Validators And Human Gates

- `git status --short` limpo ou apenas mudancas explicitamente excluidas.
- `git log BASE..HEAD --oneline` com ao menos um commit.
- `git diff BASE...HEAD --stat` revisado.
- Branch remota existe antes do PR.
- PR usa base/head aprovadas.
- `approval` antes de push, criacao de PR e de ignorar/adaptar template.
- Pare se qualquer gate/validator estiver pendente ou falhar.

## Packaging Checks

Nao escreva no pacote, configuracoes instaladas ou working tree. Mudancas
relacionadas devem usar workflow posterior aprovado.

## Stop Conditions

- Repositorio Git ausente; branch atual e base/default; nenhum commit; mudancas
  nao commitadas relevantes; provider/remote ambiguo ou nao suportado.
- Branch nao publicada sem approval; titulo/corpo nao aprovados; template
  obrigatorio sem decisao.
- Entrada/permissao insuficiente, dependencia indisponivel, handoff sem destino,
  writer conflitante, validator falho ou gate/approval pendente.

## Evidence-First Cutover

Capture somente quando houver subagente ou run state; caso contrário registre
`not-applicable`. Em todos os casos não há CoT privado ou retrospectiva automática.

## Resume Contract

Registre entrada, branch/default/base, remote/upstream, commits/diff, titulo,
corpo, template, approvals, comandos/ferramentas, push, PR/URL, handoffs, owner,
validators, gates, riscos, etapas concluidas, pendencias, proxima acao e condicao
de retomada. Nao reinicie quando esse estado permitir continuar.
