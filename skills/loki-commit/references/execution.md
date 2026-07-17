# Execution — loki-commit

## Purpose And Observable Contract

Este command e o orquestrador que cria um commit Git pequeno, revisavel e
intencional a partir do diff local, com staging explicito, mensagem convencional
e bloqueio contra commits acidentais na branch default.

- Inicio: entrada normalizada e repositorio Git legivel.
- Conclusao: um commit aprovado e validado foi criado, ou existe stop condition.
- Resultado verificavel: SHA curto, mensagem, arquivos incluidos/excluidos,
  validators e estado remanescente.
- Saidas obrigatorias: siga integralmente `references/response.md`.

## Execution Profile

```yaml
execution_profile:
  model_class: coding
  default_effort: medium
  max_effort: high
  escalation_signals:
    - mixed unrelated changes
    - secrets or generated binaries in diff
    - current branch is main, master or default branch
    - staged changes differ materially from unstaged changes
  handoff_effort:
    coding: medium
    validator: low
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha o trabalho; selecione agentes;
forneca contexto autocontido; acompanhe handoffs ate estado terminal; aplique
validators/gates/approvals; consolide evidencias, riscos e proximos passos; e
preserve responsabilidade pelo fluxo depois de delegar.

## Allowed Writes

- Indice Git (`git add`) somente para pathspecs aprovados.
- Um commit local na branch atual aprovada.

## Forbidden Writes

- Staging de arquivo nao revisado ou fora do escopo.
- `.claude/**`, `.agents/**` e `.codex/**`, salvo pedido e escopo aprovados.
- Push, PR, merge, rebase destrutivo, reset ou checkout destrutivo.

## Required Skills And Commands

```yaml
required_skills: [lf-git-workflow]
required_commands: []
```

Carregue `lf-git-workflow` para agrupamento, staging seguro, mensagem, gates e
validators.

## Execution Planning And Replanning

Converta a entrada normalizada em plano com grupos de mudanca, pathspecs,
mensagem, owner, approvals, validators e criterio de conclusao. Replaneje quando
branch, diff, staging existente, segredo/binario ou grupos independentes
invalidarem etapa posterior.

## Agents, Handoffs And Delegation

Delegue analise, teste ou revisao ao agente apropriado quando disponivel. Cada
subagente recebe objetivo, unidade, fatos, paths/diffs permitidos, dependencias,
escopo, writes, criterios, validators/gates, saida e destino. Registre origem,
destino, objetivo, entrada, resultado esperado, status, evidencia e proximo
destino; acompanhe ate sucesso, falha, bloqueio ou parada.

## Workflow

1. Carregue `lf-git-workflow`.
2. Leia branch atual/default, `git status --short`, diff staged e unstaged.
3. Na default, pare e recomende `loki-criar-branch`, salvo pedido explicito.
4. Agrupe mudancas e detecte secrets, binarios grandes, gerados e paths fora do
   escopo.
5. Para grupos nao relacionados, proponha commits separados e peca escolha.
6. Monte pathspecs explicitos; nao use `git add .` como padrao.
7. Gere `<type>(<scope>): <subject>` e corpo com o que/por que quando necessario.
8. Mostre arquivos, diff resumido e mensagem completa para approval.
9. Execute staging aprovado e crie o commit local.
10. Reporte SHA, arquivos incluidos e estado remanescente.

## Write Ownership And Serialization

Mantenha owner unico para indice e commit; nao permita writers concorrentes.
Alteracao de arquivo do projeto exige Write Agent, mas este workflow nao altera
conteudo do working tree. Para indice/objeto Git, use agente autorizado se
disponivel; escrita direta so apos registrar ausencia de Write Agent apropriado
e assumir envelope com pathspecs exatos, allowed/forbidden writes, validators,
approvals, criterios e evidencias.

Se houver escrita direta, registre no completion record tipo, motivo da ausencia
do agente, oportunidade de especializacao, escopo futuro, evidencias e riscos.

## Validators And Human Gates

- `git status --short` antes e depois.
- `git diff --cached --check` antes do commit quando textual.
- `git log -1 --oneline` confirma o commit.
- Arquivos excluidos continuam fora.
- `approval` antes de stage, commit e commit na default.
- Pare se gate/approval estiver pendente ou validator falhar.

## Packaging Checks

Nao escreva no pacote ou destinos instalados e nao transforme commit local em
push/PR. Escopo explicito continua obrigatorio.

## Stop Conditions

- Repositorio ausente; nenhuma mudanca selecionavel; segredo/credencial/binario
  grande nao aprovado; default sem pedido; arquivos ou mensagem nao aprovados.
- Entrada/permissao insuficiente, dependencia indisponivel, handoff sem destino,
  conflito de writers, validator falho ou gate/approval pendente.

## Evidence-First Cutover

Capture somente quando houver subagente ou run state; caso contrário registre
`not-applicable`. Em todos os casos não há CoT privado ou retrospectiva automática.

## Resume Contract

Registre entrada, branch/default, grupos, arquivos incluidos/excluidos,
pathspecs, mensagem, approvals, comandos, SHA, handoffs/owners, validators,
gates, riscos, etapas concluidas, pendencias, proxima acao e condicao de
retomada. Nao reinicie quando o estado permitir continuar.
