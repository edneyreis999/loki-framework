# Execution — loki-criar-branch

## Purpose And Observable Contract

Este command e o orquestrador que cria uma branch Git segura e revisavel para
novo trabalho, com nome derivado do objetivo ou diff local, sem trocar base ou
publicar estado sem gate humano.

- Inicio: entrada normalizada e repositorio Git legivel.
- Conclusao: branch local aprovada criada e validada, ou stop condition.
- Resultado verificavel: branch anterior/nova, base, decisoes e validators.
- Saidas obrigatorias: siga integralmente `references/response.md`.

## Execution Profile

```yaml
execution_profile:
  model_class: coding
  default_effort: medium
  max_effort: high
  escalation_signals:
    - detached HEAD
    - uncommitted changes while changing base branch
    - existing local or remote branch name
    - ambiguous default branch or remote
  handoff_effort:
    coding: medium
    validator: low
```

## Orchestrator Responsibilities

Coordene Input, Execution e Response; decomponha trabalho; selecione agentes;
forneca contexto autocontido; acompanhe handoffs ate terminal; aplique
validators/gates/approvals; consolide evidencias/riscos/proximos passos; e
mantenha responsabilidade global depois da delegacao.

## Allowed Writes

- Referencias Git locais necessarias para criar/trocar para a branch nova.
- Stash temporario somente com approval quando mudancas bloquearem troca de base.

## Forbidden Writes

- Working tree, exceto restauracao de stash aprovada.
- `.claude/**`, `.agents/**` e `.codex/**`.
- Push, commit, PR, merge, rebase destrutivo, reset ou checkout destrutivo.

## Required Skills And Commands

```yaml
required_skills: [lf-git-workflow]
required_commands: []
```

Carregue `lf-git-workflow` para preflight, nomeacao, gates e validators.

## Execution Planning And Replanning

Converta entrada em plano com estado minimo, nome, base, owner, approvals,
validators e conclusao. Replaneje diante de detached HEAD, colisao, base
ambigua, remote divergente ou mudancas que inviabilizem troca segura.

## Agents, Handoffs And Delegation

Delegue analise/teste/revisao ao agente apropriado quando disponivel. Forneca a
cada subagente objetivo, unidade, fatos, paths/fontes, dependencias, escopo,
writes, criterios, validators/gates, saida e destino. Registre origem, destino,
objetivo, entrada, resultado esperado, status, evidencia e proximo destino; siga
ate estado terminal.

## Workflow

1. Carregue `lf-git-workflow`.
2. Leia branch atual, `git status --short`, remotes e default detectavel.
3. Use descricao como fonte principal; sem ela, derive do diff; sem sinal
   suficiente, pergunte objetivo.
4. Gere `<autor>/<tipo>/<descricao-curta>` quando houver autor; caso contrario,
   `<tipo>/<descricao-curta>` ou pergunte prefixo.
5. Valide caracteres, tamanho, colisao local/remota e base.
6. Se branch atual divergir da base, explique delta e obtenha approval. Com
   mudancas locais, ofereca stash aprovado ou branch a partir da atual.
7. Mostre branch, base e comando; obtenha approval final.
8. Crie branch local e restaure stash aprovado, se houver.
9. Reporte sem executar commit, push ou PR.

## Write Ownership And Serialization

Mantenha owner unico para refs/stash; serialize todas as operacoes Git. Mudanca
de arquivo do projeto exige Write Agent, mas e proibida fora da restauracao de
stash aprovada. Para refs/stash, use agente autorizado se disponivel; escrita
direta somente apos registrar ausencia de Write Agent e envelope com branch,
base, allowed/forbidden writes, validators, approvals, criterios e evidencias.

Se houver escrita direta, registre no completion record tipo, motivo da ausencia
do agente, oportunidade de especializacao, escopo futuro, evidencias e riscos.

## Validators And Human Gates

- `git branch --show-current` retorna branch nova.
- `git show-ref --verify refs/heads/<branch>` confirma a ref.
- Mudancas preexistentes continuam visiveis em `git status --short`.
- Nenhum push, commit ou PR foi executado.
- `approval` antes de criar branch, trocar base e stash/restore.
- Pare quando gate estiver pendente ou validator falhar.

## Packaging Checks

Nao escreva em pacote/destinos instalados e nao amplie para commit/push/PR.

## Stop Conditions

- Repositorio ausente; base ambigua; nome colide; detached HEAD sem base;
  mudancas impedem troca e usuario nao aprova alternativa.
- Entrada/permissao insuficiente, dependencia indisponivel, handoff sem destino,
  conflito de writers, validator falho ou gate/approval pendente.

## Evidence-First Cutover

Capture somente quando houver subagente ou run state; caso contrário registre
`not-applicable`. Em todos os casos não há CoT privado ou retrospectiva automática.

## Resume Contract

Registre entrada, objetivo, branch atual, base, nome, colisoes, mudancas locais,
stash, approvals, comandos, estado final, handoffs/owners, validators, gates,
riscos, etapas concluidas, pendencias, proxima acao e condicao de retomada.
