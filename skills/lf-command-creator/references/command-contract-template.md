# Command Contract Template

Fonte canônica para criar ou auditar commands Loki. Substitua placeholders
somente com fatos e decisões aprovadas; mantenha regras de tecnologia em skills
especializadas e não dependa de artefatos `internal-only` em commands `both`.

## Loki Skill-Bundle Serialization

```text
skills/loki-<stem>/
├── SKILL.md
├── references/execution.md
├── references/response.md
└── assets/response-template.md
```

O bundle é a unidade única: `SKILL.md` contém metadata/Input, `execution.md` o
contrato operacional, `response.md` o consumidor/formato e o asset a resposta.
Use `name: loki-<stem>`, `type: command`, `serialization: skill-bundle`; não
crie command pareado, projection ou contract paralelo.

## Input

Comece com a frase exata `Entre no modo Plan e peça os parâmetros de entrada para o workflow.` e declare:

```yaml
parameters:
  - key: <required_key>
    input_type: <type>
    requirement: required
    description: <meaning and constraint>
  - key: <optional_key>
    input_type: <type>
    requirement: optional
    default: <safe default>
    description: <meaning and constraint>
```

Valide presença, tipo, formato, paths e combinações; solicite todo obrigatório
ausente, sem inventar escopo, approval, destino ou validator. Normalize objetivo,
parâmetros, escopo, restrições, destinos, writes, gates e lacunas para Execution.
Durante Input não implemente, escreva, execute a tarefa principal, invoque writer
nem declare sucesso.

## Execution

Declare propósito, condição de início, término, resultado verificável e saídas.
Transforme a entrada normalizada em plano com etapas, dependências, owners,
validators, gates e critérios de conclusão; replaneje explicitamente quando um
resultado invalidar etapa posterior. Delegue leitura, pesquisa, implementação,
teste ou revisão ao papel apropriado sempre que possível e acompanhe cada handoff
até sucesso, falha, bloqueio ou parada.

Todo handoff recebe objetivo, unidade, fatos/decisões/restrições, fontes,
dependências, `allowed_writes`, `forbidden_writes`, owner, sucesso/falha,
validators, gates, formato e destino. Handoffs retornam completion record com
resultado, arquivos, validações, gates, riscos e próximo destino; o orquestrador
captura evidência sanitizada ou registra lacuna, sem raciocínio privado.

Escritas são serializadas por arquivo e owner único. Um Write Agent só escreve
com targets, domínios, validators e gates no envelope aprovado. Escrita direta
do orquestrador é exceção após registrar ausência de Write Agent apropriado e,
antes da escrita, target, allowed/forbidden writes, owner, validators, gates,
sucesso/falha; o completion record registra motivo e oportunidade de futuro
writer. Aplique validators, gates e approvals antes da ação dependente.

```yaml
command_contract:
  name: "loki-<stem>"
  purpose: "<observable purpose>"
  start_condition: "<validated normalized input>"
  completion_condition: "<all selected work terminal and gates resolved>"
  outputs: ["<artifacts or response>"]
  allowed_writes: []
  forbidden_writes: [".claude/**", ".agents/**", ".codex/**", "<sensitive_write_patterns>"]
  required_skills: ["<technology_required_skills>"]
  required_commands: []
  validators: ["<validator>"]
  human_gates: ["<interview | approval | human-validation | technical-review>"]
  stop_conditions: ["<missing input, permission, validator, gate, handoff or scope>"]
  resume_contract: "<state sufficient to resume without conversation memory>"
```

## Response

Declare o consumidor primário e responda de acordo com ele: `LLM` usa XML com
`summary`, `status`, `artifacts`, `evidence`, `handoff`, `risks` e `next_steps`;
`Humano` usa Markdown acionável de no máximo 7.000 caracteres; `Both` usa
Markdown recuperável, sem limite rígido. A resposta terminal informa status,
resumo, artefatos, evidências/validators, handoffs, gates/approvals, riscos e
próximos passos. Não declare conclusão com validator, gate, approval ou handoff
material pendente.

## Conditional LLM-Facing Quality Gate

Before delivery, classify the created or revised command with
[lf-documentation-writing](../../lf-documentation-writing/SKILL.md). When the
classification is positively LLM-facing, require a complete
`llm_artifact_profile`, application of the
[canonical LLM artifact quality contract](../../lf-documentation-writing/references/llm-artifact-quality-validation.md),
and an independent `llm_consumption_quality` result in which every applicable
fixture passes. Do not copy the canonical rubric, schemas, or fixture
definitions into this creator contract.

Use these terminal semantics:

- positive LLM-facing classification without the complete profile, canonical
  contract, independent result, or with any non-passing applicable fixture:
  mark checklist item 13 `não` and block delivery;
- positive LLM-facing classification with the complete profile and independent
  result approved: item 13 may be `sim`, and completion remains subject to all
  other checklist items and existing gates;
- exclusively human-facing: record `not-applicable` with a concrete human-only
  reason and do not run irrelevant fixtures.

## Checklist binária 24/24

Marque cada item com `sim|não`, arquivo e heading; todo `não` bloqueia entrega.

1. Orquestrador, agentes, contexto autocontido e handoffs terminais.
2. Propósito, início, término, resultado e saídas observáveis.
3. Fases Input, Execution e Response separadas.
4. Frase de modo Plan e `parameters` YAML.
5. Validação de parâmetros.
6. Solicitação de obrigatórios ausentes.
7. Normalização para Execution.
8. Input sem tarefa principal/escrita/sucesso.
9. Plano de Execution e replanejamento.
10. Agentes, validators, handoffs e envelopes autocontidos.
11. Delegação ao papel apropriado quando disponível.
12. Acompanhamento terminal dos handoffs.
13. Validators, gates e approvals antes de ações dependentes, incluindo o gate
    LLM-facing condicional acima quando aplicável.
14. Escritas serializadas e owner único.
15. Write Agent apropriado para mudanças.
16. Escrita direta só sem Write Agent apropriado.
17. Completion record registra oportunidade de futuro Write Agent.
18. Exceção direta declara escopo, writes, owner, validators e gates.
19. Stop conditions e resume contract.
20. Consumidor LLM, Humano ou Both declarado.
21. LLM em XML estruturado.
22. Humano em Markdown até 7.000 caracteres.
23. Both em Markdown recuperável sem limite rígido.
24. Resposta com status, resumo, artefatos, evidências, handoff, riscos e próximos passos.
