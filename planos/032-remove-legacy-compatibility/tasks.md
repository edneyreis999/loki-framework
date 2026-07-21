---
title: "Remover compatibilidade legada do Loki Framework"
type: loki-action-plan
status: draft
created: "2026-07-20"
---

# Plano de Ação - Remover compatibilidade legada do Loki Framework

## Overview

Este plano transforma a demanda e a deep analysis do plano 032 em um corte
faseado para manter um único contrato suportado por família de artefato. A
execução restaura primeiro o baseline, introduz rejeições explícitas antes de
remover readers e migrações, elimina a projection Goose por decisão humana e
termina com inventário, packaging e revisão técnica convergentes.

## Sources

- `planos/032-remove-legacy-compatibility/demanda.md`, seções `Escopo`, `Fora de escopo` e `Critérios de aceitação`.
- `planos/032-remove-legacy-compatibility/analise.md`, seções `Achados materiais`, `Estratégia técnica recomendada`, `Validators executados` e `Riscos e gaps`.
- Decisão humana de 2026-07-20: remover `goose/**` como superfície transicional/histórica.
- Approval humano de 2026-07-20 para materializar o plano neste diretório.
- `docs/package-authoring-guardrails.md`, seções `Codex Symlink Installer`, `Docs e Manifest` e `Validações Mínimas`.
- `skills/lf-action-plan-authoring/references/action-plan-contract.md`.

## Derived Allowed Scope And Provenance

```yaml
derived_allowed_scope:
  source:
    - planos/032-remove-legacy-compatibility/demanda.md
    - planos/032-remove-legacy-compatibility/analise.md
  provenance:
    positive_scope: "contratos agentic/evidence/inference, retrospectiva, navegação, instalação, validators, fixtures, templates, projections, inventário e documentação"
    approved_goose_decision: "remove-transitional-surface, user decision 2026-07-20"
    plan_directory_approval: "approved in chat 2026-07-20"
    baseline_plan_gate: "approved in chat 2026-07-20; task-1.2 repairs the existing validator drift before legacy cuts"
  allowed_surfaces:
    - scripts/validate-agentic-run-state.py
    - scripts/install-loki-symlinks.py
    - scripts/validate-install-scopes.py
    - scripts/validate-install-loki-upgrade.py
    - scripts/validate-loki-init-catalogador-contracts.py
    - skills/lf-agentic-orchestration/**
    - skills/lf-agent-execution-evidence/**
    - skills/lf-analytic-inference/**
    - skills/lf-index-navigator/**
    - skills/loki-continuous-improvement/**
    - skills/loki-deep-analysis/**
    - skills/loki-retrospectiva-tecnica/**
    - skills/lf-template-library/references/templates/**
    - templates/**
    - agents/**
    - codex/agents/**
    - goose/**
    - manifest.yaml
    - install-scopes.json
    - README.md
    - docs/**
    - planos/032-remove-legacy-compatibility/**
```

## Scope

- Declarar e verificar o contrato canônico atual de cada família, sem equiparar todo `schema_version=1` a legado.
- Fazer entradas antigas falharem explicitamente antes de qualquer write.
- Remover readers, branches, flags, migrações, fallbacks e fixtures positivas legadas.
- Remover `goose/**` e manter Codex/Claude alinhados ao pacote raiz.
- Preservar mirrors, non-interference, compatibilidade de domínio e fallbacks operacionais atuais.
- Atualizar inventário, scopes, manifest, documentação e validators na mesma sequência.

## Out Of Scope

- Ler, migrar, limpar ou alterar estados e instalações de consumidores.
- Escrever em `.loki/**`, `.agents/**`, `.claude/**` ou `.codex/**`.
- Remover compatibilidade RPG Maker/VisuStella ou outras funcionalidades de domínio externo.
- Alterar `frameworks-de-referencia/**`.
- Implementar migração automática, commit, push, publicação ou Pull Request.

## Assumptions

- A matriz canônica observada na análise será confirmada contra o source atual antes do primeiro corte.
- O validator de upgrade será restaurado sem mudar comportamento legacy; remoções virão somente nas fases posteriores.
- A decisão de remover Goose cobre os 20 arquivos rastreados em `goose/**`; arquivos locais ignorados não são fonte normativa.
- A invocação futura de `loki-run-plan` é o approval de execução; ampliação de targets exige novo approval.
- A execução ocorrerá em uma worktree derivada da branch `loki-upgrade-v3`; o estado atual desta worktree não é fonte nem baseline do plano.

## Open Questions

- none

## Downstream Execution Profile

```yaml
downstream_execution_profile:
  model_class: frontier_reasoning
  execution_effort: high
  escalation_reason: "breaking change transversal em contratos persistidos, instalação, validators, projections e documentação normativa"
  recommended_handoffs:
    research: source-researcher somente para lacuna material localizada
    context: execution-context-reader para demanda e análise por fase
    implementation: technical-implementer para código/validators; framework-artifact-writer para contratos/docs/projections
    runtime_validation: none
  scoped_writers:
    - agent: technical-implementer
      domains: [validators, package-templates, installation-code, configuration]
      target_files: [declarados por task]
    - agent: framework-artifact-writer
      domains: [package-contracts, package-documentation, package-manifest, install-scopes, codex-projections]
      target_files: [declarados por task]
  validator_effort: high
```

## Phases

### Fase 1 - Baseline e contrato canônico

**Objective:** congelar a matriz canônica e restaurar um baseline verde sem antecipar remoções.
**Observable Validation:** matriz revisada e `validate-install-loki-upgrade.py` verde contra contagens derivadas do estado atual.

| Task | Title | Dependencies | Write Owner | Estimate | Human Loop | Validators | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| task-1.1 | Confirmar matriz canônica e inventário de rejeições | none | technical-implementer | 2-4h | approval, technical-review | source map e scan classificado | completed |
| task-1.2 | Restaurar baseline do validator de upgrade | task-1.1 | technical-implementer | 2-4h | approval, technical-review | 17 testes e dry-runs | completed |

### Fase 2 - Agentic state, evidence e retrospectiva

**Objective:** cortar readers e campos legados nos contratos agentic/evidence sem enfraquecer as proibições atuais.
**Observable Validation:** apenas manifest 4, report 5, digest 4 e schemas atuais por família passam; shapes antigos e `operational_trace` falham.

| Task | Title | Dependencies | Write Owner | Estimate | Human Loop | Validators | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| task-2.1 | Fechar schemas agentic e sincronizar templates | task-1.2 | technical-implementer | 2-4h | approval, technical-review | agentic self-test e mirror parity | completed |
| task-2.2 | Fechar política de session evidence | task-2.1 | technical-implementer | 2-4h | approval, technical-review | evidence positive/negative fixtures | completed |
| task-2.3 | Remover input retrospectivo legado | task-2.2 | framework-artifact-writer | 2-4h | approval, technical-review | bundle contract e rejeição de input | completed |

### Fase 3 - Analytic inference e navegação documental

**Objective:** eliminar a leitura v1/copy migration e o fallback de `index.md` do consumidor, preservando schemas 1 atuais.
**Observable Validation:** somente o layout XML v2 é lido; `migration-dry-run`, schemas JSON legados e fallback do consumidor não existem.

| Task | Title | Dependencies | Write Owner | Estimate | Human Loop | Validators | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| task-3.1 | Classificar fixtures de inferência | task-2.3 | technical-implementer | 2-4h | approval, technical-review | fixture map completo | completed |
| task-3.2 | Remover reader e operação de migração v1 | task-3.1 | technical-implementer | 2-4h | approval, technical-review | catalog validator e CLI negatives | completed |
| task-3.3 | Remover contratos e roteamentos de copy migration | task-3.2 | framework-artifact-writer | 2-4h | approval, technical-review | link/contract scan | completed |
| task-3.4 | Remover fallback consumer `index.md` | task-3.3 | framework-artifact-writer | 2-4h | approval, technical-review | navigator contract negatives | completed |

### Fase 4 - Instalação schema 2 sem cleanup

**Objective:** aceitar somente install-scopes schema 2 e rejeitar instalações antigas sem migrar ou remover seus artefatos.
**Observable Validation:** schema 1, commands legados, manifests antigos e flag de cleanup falham com zero writes; os três profiles atuais passam.

| Task | Title | Dependencies | Write Owner | Estimate | Human Loop | Validators | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| task-4.1 | Tornar install-scopes estritamente schema 2 | task-3.4 | technical-implementer | 2-4h | approval, technical-review | install-scopes positives/negatives | completed |
| task-4.2 | Remover cleanup e converter testes para rejeição | task-4.1 | technical-implementer | 2-4h | approval, technical-review | upgrade suite e non-interference | completed |
| task-4.3 | Alinhar manifest e documentação de instalação | task-4.2 | framework-artifact-writer | 2-4h | approval, technical-review | manifest/scopes/docs/dry-runs | completed |

### Fase 5 - Remoção Goose e paridade dos adapters restantes

**Objective:** remover a superfície Goose aprovada e fechar paridade semântica observável de Codex/Claude.
**Observable Validation:** nenhum arquivo ou referência normativa Goose permanece; projections Codex custom e instalação Claude têm cobertura explícita.

| Task | Title | Dependencies | Write Owner | Estimate | Human Loop | Validators | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| task-5.1 | Remover a árvore Goose rastreada | task-4.3 | orchestrator | 2-4h | approval, technical-review | tracked-file e forbidden-reference scans | completed |
| task-5.2 | Alinhar artefatos Codex e cobertura Claude | task-5.1 | framework-artifact-writer | 2-4h | approval, technical-review | TOML parse e inventory parity | completed |
| task-5.3 | Fechar validators de paridade dos adapters | task-5.2 | technical-implementer | 2-4h | approval, technical-review | agent parity e install profiles | completed |

### Fase 6 - Convergência documental e aceite integral

**Objective:** publicar o contrato final do pacote e reunir evidência mecânica e revisão independente.
**Observable Validation:** scans, parsing, mirrors, manifest, instalação, validators focados e auditoria independente terminam sem finding material.

| Task | Title | Dependencies | Write Owner | Estimate | Human Loop | Validators | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| task-6.1 | Consolidar inventário, guardrails e documentação | task-5.3 | framework-artifact-writer | 2-4h | approval, technical-review | links, manifest e source boundaries | completed |
| task-6.2 | Executar aceite integral e revisão independente | task-6.1 | orchestrator | 2-4h | technical-review | matriz completa de package checks | completed |

## Execution Order

1. task-1.1
2. task-1.2
3. task-2.1
4. task-2.2
5. task-2.3
6. task-3.1
7. task-3.2
8. task-3.3
9. task-3.4
10. task-4.1
11. task-4.2
12. task-4.3
13. task-5.1
14. task-5.2
15. task-5.3
16. task-6.1
17. task-6.2

## Human Loops

- `approval` de execução antes de cada handoff de Write Agent; o approval deste diretório não autoriza writes no pacote.
- `technical-review` em cada task que muda contrato, template, validator, instalação, projection ou política durável.
- `human-validation` dos handoffs `technical-implementer` deve ser registrado como `not-applicable` enquanto a task usar apenas fixtures/dry-runs e não alegar runtime ou comportamento de consumidor; torna-se obrigatório se esse boundary mudar.
- Novo approval é obrigatório se a execução ampliar targets, tocar consumidor, instalar, migrar, limpar ou escrever fora do package root e do plano.
- A remoção de `goose/**` está decidida; a execução ainda deve confirmar targets rastreados e passar revisão técnica antes da deleção.
- `human-validation` não se aplica: nenhuma task pode alegar comportamento de consumidor ou runtime instalado validado.

## Review State Authority

`skills/lf-run-plan-execution/SKILL.md` é a autoridade canônica para
`write_test_review_policy`, materialidade, checkpoints, resume e semântica
consultiva. O estado inicia sem checkpoints ou evidence fabricada.

## Resume State

```yaml
loki_plan_state:
  schema_version: 1
  current_phase: fase6
  current_task: null
  status: completed
  approvals:
    plan_directory: approved-2026-07-20
    goose_decision: remove-transitional-surface-2026-07-20
    baseline_plan_gate: approved-2026-07-20
    task_1_1_technical_review: approved-in-chat-2026-07-21
    task_1_2_technical_review: completed-by-orchestrator-2026-07-21
    task_2_1_technical_review: completed-by-orchestrator-2026-07-21
  write_test_review:
    policy:
      schema_version: 1
      requested_frequency: task
      effective_frequency: task
      source: default
      terminal_scope: task
      selected_agent:
        name: framework-artifact-quality-auditor
        selection_reason: "independent read-only Write Test Agent for durable package patches"
      policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
    checkpoints:
      - schema_version: 1
        checkpoint_id: "review-checkpoint-v1:d54d2a45ab162df2d8f92d1a7443c661f3abec9e37b42f6c0cdd9d6679623545"
        execution_id: "plan-032-task-1.1-20260720"
        policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
        boundary_type: task
        boundary_ref: task-1.1
        coverage_digest: "sha256:21774c9634857ca04862934c43b3def34177351f14f3852c9b6dd337b8513b4b"
        coverage_manifest:
          schema_version: 1
          handoffs:
            - handoff_id: "handoff-task-1.1-writer-20260720"
              completion_ref: "builds/fase1/canonical-contract-matrix.md#execution-completion"
              evidence_ref: "builds/fase1/canonical-contract-matrix.md#focused-validation-evidence"
              changed_files:
                - path: "planos/032-remove-legacy-compatibility/builds/fase1/canonical-contract-matrix.md"
                  sha256: "sha256:30fc78395bf34c91c540d5c6ee26f4bab52c642bd09971f2bdd15a2ccd773c01"
          reviewer:
            name: framework-artifact-quality-auditor
            contract_version: draft-write-test
            selection_configuration_digest: "sha256:6d3277165555efd9f7ebf9f5dbd194d97c44e3d90a3c29862c9b39657905ba34"
        covered_write_handoff_ids: ["handoff-task-1.1-writer-20260720"]
        status: completed-clean
        review_agent_run_id: "task-1.1-write-test-review-20260720"
        review_handoff_id: "review-handoff-v1:d54d2a45ab162df2d8f92d1a7443c661f3abec9e37b42f6c0cdd9d6679623545"
        review_agent_raw_status: no_findings
        execution_status_effect: none
        evidence_ref: "builds/fase1/canonical-contract-matrix.md#execution-completion"
        findings: []
        risk_refs: []
        backlog_refs: []
        reason: null
      - schema_version: 1
        checkpoint_id: "review-checkpoint-v1:79447b64b2f0d077446e3eb2fa087faeaa06d4b37cbbced37e6308ee13c204b8"
        execution_id: "plan-032-task-2.1-20260721"
        policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
        boundary_type: task
        boundary_ref: task-2.1
        coverage_digest: "sha256:39e821f868d50f7f7604f1a7fef21871ee28c61bd7a7b070652cc6f6e84a5cb6"
        coverage_manifest:
          schema_version: 1
          handoffs:
            - handoff_id: "handoff-task-2.1-writer-20260721"
              completion_ref: "task-2.1.md#resume-notes"
              evidence_ref: "task-2.1.md#resume-notes"
              changed_files:
                - path: "scripts/validate-agentic-run-state.py"
                  sha256: "sha256:f366ab58fd4ed6e679c468e29a8418da15b64dbc1f6f258a2e94882f0880d430"
                - path: "skills/lf-agentic-orchestration/SKILL.md"
                  sha256: "sha256:0b234c0a596491fff32c8cd4c8e4a9de0ed2e02cccc1b9f92bf4221f5c4d79ef"
                - path: "skills/lf-agentic-orchestration/references/agentic-orchestration-contract.md"
                  sha256: "sha256:2d06dbee4a3b9ef715094ef03151344bda986abf8d4691d624c7b7e6f65d83a7"
                - path: "skills/lf-template-library/references/templates/agent-run-report-template.xml"
                  sha256: "sha256:cae63e0b6c8dac0348b9df6dc89b500ee6548ec2057dd01710c0fe62c9b067ca"
                - path: "skills/lf-template-library/references/templates/agentic-run-digest-template.xml"
                  sha256: "sha256:72fbd24d58882e6faf90d0b007e58cd4053844c38f8edffc5fda6cdf810121cb"
                - path: "skills/lf-template-library/references/templates/agentic-run-manifest-template.xml"
                  sha256: "sha256:7d2f39b42b0d7c2df27dc6f14a26ef645de77871a70b5ee5e4b6b54ee3c669d0"
                - path: "templates/agent-run-report-template.xml"
                  sha256: "sha256:cae63e0b6c8dac0348b9df6dc89b500ee6548ec2057dd01710c0fe62c9b067ca"
                - path: "templates/agentic-run-digest-template.xml"
                  sha256: "sha256:72fbd24d58882e6faf90d0b007e58cd4053844c38f8edffc5fda6cdf810121cb"
                - path: "templates/agentic-run-manifest-template.xml"
                  sha256: "sha256:7d2f39b42b0d7c2df27dc6f14a26ef645de77871a70b5ee5e4b6b54ee3c669d0"
          reviewer:
            name: framework-artifact-quality-auditor
            contract_version: draft-write-test
            selection_configuration_digest: "sha256:6d3277165555efd9f7ebf9f5dbd194d97c44e3d90a3c29862c9b39657905ba34"
        covered_write_handoff_ids: ["handoff-task-2.1-writer-20260721"]
        status: completed-clean
        review_agent_run_id: "task-2.1-write-test-review-20260721"
        review_handoff_id: "review-handoff-v1:79447b64b2f0d077446e3eb2fa087faeaa06d4b37cbbced37e6308ee13c204b8"
        review_agent_raw_status: clean
        execution_status_effect: none
        evidence_ref: "task-2.1.md#resume-notes"
        findings: []
        risk_refs: []
        backlog_refs: []
        reason: null
      - schema_version: 1
        checkpoint_id: "review-checkpoint-v1:1c3632d45b44e675deff6be31dbd595770652d136a428b477ef7a2e9ed3b17de"
        execution_id: "plan-032-task-1.2-20260721"
        policy_digest: "sha256:f20d4a696758626195dea8b4f4b3959e7fcd89435fd0a1691770fb5574a69085"
        boundary_type: task
        boundary_ref: task-1.2
        coverage_digest: "sha256:d931e9b6af01c3e0a3b2de6c6de13d32ed5dbad600ea6f55336e5be5c00135c7"
        coverage_manifest:
          schema_version: 1
          handoffs:
            - handoff_id: "handoff-task-1.2-writer-20260721"
              completion_ref: "task-1.2.md#resume-notes"
              evidence_ref: "task-1.2.md#resume-notes"
              changed_files:
                - path: "scripts/validate-install-loki-upgrade.py"
                  sha256: "sha256:bd1a675d7f1c996ccc06eac73bf16e9b5f2814409305256d8c8601028c1b1264"
          reviewer:
            name: framework-artifact-quality-auditor
            contract_version: draft-write-test
            selection_configuration_digest: "sha256:6d3277165555efd9f7ebf9f5dbd194d97c44e3d90a3c29862c9b39657905ba34"
        covered_write_handoff_ids: ["handoff-task-1.2-writer-20260721"]
        status: completed-clean
        review_agent_run_id: "task-1.2-write-test-review-20260721"
        review_handoff_id: "review-handoff-v1:1c3632d45b44e675deff6be31dbd595770652d136a428b477ef7a2e9ed3b17de"
        review_agent_raw_status: approved
        execution_status_effect: none
        evidence_ref: "task-1.2.md#resume-notes"
        findings: []
        risk_refs: []
        backlog_refs: []
        reason: null
    state_errors: []
    risks:
      - "consultive review does not replace validators or technical-review"
      - "existing upgrade validator drift must be repaired before compatibility cuts"
    next_action: "Run task-2.2 and persist session-evidence policy-cut evidence."
  next_action: "Invoke task-2.2 in the execution worktree."
  blocked_by: []
```
