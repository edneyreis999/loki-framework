# Como melhorar instruções de skills

## Perguntas de auditoria

Antes de alterar as instruções da skill, pergunte a si mesma:

1. As instruções da skill contemplam a exigência de declarar explicitamente que a skill encapsula conhecimento especializado reutilizável para executar ou orientar uma tarefa específica?
2. As instruções da skill contemplam a exigência de definir uma única capacidade principal, com escopo e não escopo verificáveis?
3. As instruções da skill contemplam a exigência de não atuar como orquestradora nem coordenar um fluxo completo com múltiplos agentes, handoffs e estado retomável?
4. As instruções da skill contemplam a exigência de usar uma pasta própria com `SKILL.md` como ponto de entrada e `references/` como local de materiais de apoio?
5. As instruções da skill contemplam a exigência de possuir frontmatter YAML válido com, no mínimo, `name` e `description`?
6. As instruções da skill contemplam a exigência de manter o valor de `name` igual ao nome da pasta e compatível com a convenção de nomenclatura do pacote?
7. As instruções da skill contemplam a exigência de fazer `description` declarar o que a skill faz e os contextos concretos que devem acioná-la?
8. As instruções da skill contemplam a exigência de declarar quando usar e quando não usar a skill por meio de gatilhos e exclusões observáveis?
9. As instruções da skill contemplam a exigência de declarar metadados multi-adapter coerentes, sem ramificar o contrato conforme o executor atual?
10. As instruções da skill contemplam a exigência de apresentar um propósito objetivo e diretamente ligado à capacidade especializada?
11. As instruções da skill contemplam a exigência de declarar entradas obrigatórias, entradas opcionais e como tratar informações ausentes?
12. As instruções da skill contemplam a exigência de fornecer um procedimento essencial, ordenado e escrito no imperativo?
13. As instruções da skill contemplam a exigência de declarar saídas esperadas e critérios de conclusão verificáveis?
14. As instruções da skill contemplam a exigência de declarar limites essenciais, proibições e condições de parada?
15. As instruções da skill contemplam a exigência de definir validações essenciais, evidências proporcionais ao risco e gates de revisão ou aprovação aplicáveis?
16. As instruções da skill contemplam a exigência de ajustar o grau de liberdade das instruções à fragilidade, repetição e risco da execução?
17. As instruções da skill contemplam a exigência de manter `SKILL.md` objetivo e restrito ao conteúdo necessário para ativar e executar a capacidade?
18. As instruções da skill contemplam a exigência de mover documentação detalhada, exemplos extensos, variações condicionais, templates, checklists, notas de plataforma e pesquisa para `references/`?
19. As instruções da skill contemplam a exigência de informar em `SKILL.md` exatamente quando cada referência deve ser lida?
20. As instruções da skill contemplam a exigência de colocar comportamento determinístico ou repetitivo em `scripts/` e testar os scripts adicionados?
21. As instruções da skill contemplam a exigência de usar `assets/` somente para arquivos consumidos pela saída, e não para instruções que a LLM deva ler?
22. As instruções da skill contemplam a exigência de evitar duplicação e contradição entre `SKILL.md` e os materiais de apoio?
23. As instruções da skill contemplam a exigência de ser autocontida no pacote, sem depender de memória da conversa, caminhos locais absolutos, arquivos de plano externos ou fontes de instalação como autoridade normativa?
24. As instruções da skill contemplam a exigência de concluir com validação estrutural e, quando a skill for complexa ou de alto risco, teste prospectivo em contexto limpo?

Responda a cada pergunta somente com `sim` ou `não`. Responda `sim` apenas quando a exigência estiver explícita, verificável e sem contradição em outra parte das instruções ou dos recursos da skill. Não infira cobertura a partir do nome do arquivo, de uma capacidade presumida da LLM ou de contexto externo não disponibilizado.

## Como corrigir cada resposta “não”

Se responder `não` a qualquer pergunta, altere as instruções da skill antes de classificá-las. Aplique a correção de mesmo número usando linguagem imperativa, critérios binários e limites verificáveis.

### 1. Declare o papel da skill

Adicione uma instrução explícita que defina a skill como conhecimento especializado reutilizável para executar ou orientar uma tarefa específica. Identifique a capacidade que ela oferece e o resultado que essa capacidade produz.

Remova descrições que apresentem a skill como um fluxo genérico capaz de assumir qualquer responsabilidade. Faça o conteúdo permanecer reutilizável em tarefas que compartilhem a mesma necessidade especializada.

### 2. Restrinja a skill a uma capacidade principal

Declare:

- capacidade principal;
- escopo incluído;
- escopo excluído;
- exemplos concretos de uso;
- sinais de que outra capacidade é necessária.

Divida o artefato quando suas instruções reunirem responsabilidades independentes que possuam gatilhos, entradas ou resultados diferentes. Não use um objetivo amplo como substituto de um escopo verificável.

### 3. Proíba orquestração

Instrua a skill a ensinar ou aplicar conhecimento especializado sem coordenar um fluxo completo. Remova responsabilidades de:

- selecionar e coordenar múltiplos agentes;
- acompanhar uma cadeia de handoffs;
- manter estado retomável de um workflow completo;
- controlar do início ao fim uma execução composta por papéis independentes;
- consolidar o estado global de várias unidades de trabalho.

Permita que a skill seja usada por uma LLM ou por um agente dentro de um fluxo maior, mas não faça a skill assumir a coordenação desse fluxo. Se o comportamento depender dessas responsabilidades, retire-o da skill e preserve nela somente o conhecimento especializado reutilizável.

### 4. Corrija a estrutura da pasta

Organize a skill nesta estrutura mínima:

```text
<skill-name>/
├── SKILL.md
└── references/
```

Use exatamente `SKILL.md` como ponto de entrada. Mantenha `references/` para materiais de apoio carregados sob demanda. Crie `scripts/`, `assets/` e `agents/` somente quando possuírem função operacional explícita.

Não deixe instruções da skill em arquivos Markdown soltos diretamente sob `skills/`.

### 5. Adicione o frontmatter obrigatório

Inicie `SKILL.md` com frontmatter YAML válido. Declare, no mínimo:

```yaml
---
name: <skill-name>
description: <o que a skill faz e quando deve ser usada>
---
```

Não esconda `name` ou `description` no corpo. Verifique se o delimitador de abertura e o de fechamento existem e se o YAML pode ser interpretado sem erro.

### 6. Alinhe nome, pasta e namespace

Faça o valor de `name` corresponder exatamente ao nome da pasta. Use letras minúsculas, números e hífens. Aplique o namespace definido pelo pacote e não invente prefixos incompatíveis com a função da skill.

Renomeie a pasta ou o campo quando houver divergência. Atualize o inventário do pacote se a skill for adicionada, removida, renomeada ou movida.

### 7. Torne description acionável

Escreva `description` como a superfície principal de acionamento. Inclua:

- o que a skill faz;
- os contextos concretos em que deve ser usada;
- os tipos de tarefa, artefato ou sintoma que indicam seu uso.

Não dependa apenas de uma seção posterior para explicar quando usar a skill, pois o corpo pode ser carregado somente depois da seleção.

### 8. Declare gatilhos e exclusões

Liste condições observáveis para usar e para não usar a skill. Prefira tipos de solicitação, objetivos, artefatos e situações concretas a palavras-chave isoladas.

Inclua exclusões sempre que houver risco de acionamento indevido. Faça a LLM escolher outra capacidade ou interromper a execução quando a solicitação estiver fora do escopo declarado.

### 9. Preserve um contrato multi-adapter

Declare no frontmatter o conjunto multi-adapter adotado pelo pacote:

```yaml
name: <skill-name>
description: <capacidade e contextos concretos de uso>
when_to_use: []
argument-hint: <resumo dos argumentos>
arguments:
  required: []
  optional: []
disable-model-invocation: false
user-invocable: true
allowed-tools: []
disallowed-tools: []
model: inherit
effort: medium
model_class: <classe provider-neutral>
adapter_projection:
  codex: <semântica da projeção>
  claude_code: <semântica da projeção>
escalation_signals: []
context: standard
agent: main
hooks: []
paths: {}
shell: {}
```

Substitua os placeholders por valores coerentes com a capacidade. Use valores neutros quando um campo não for aplicado diretamente por todos os ambientes. Preserve uma única semântica para propósito, argumentos, ferramentas, modelo, esforço, contexto e política de invocação.

Quando a skill também possuir uma superfície Codex app/plugin aprovada, mantenha os metadados de interface, prompt padrão, política de invocação e dependências em `agents/openai.yaml`. Não crie esse arquivo quando essa superfície não fizer parte do pacote.

Não crie corpos de instrução diferentes conforme o executor atual. Não declare suporte, ferramenta, campo ou comportamento que o pacote não reconheça.

### 10. Explicite o propósito

Adicione no início do corpo uma frase objetiva que responda:

- qual capacidade a skill fornece;
- para qual tipo de tarefa;
- qual resultado especializado é esperado.

Remova introduções históricas, promocionais ou narrativas que não alterem a execução.

### 11. Defina as entradas

Declare cada entrada com nome, obrigatoriedade, tipo, significado e restrições. Diferencie entradas obrigatórias de opcionais. Defina valores padrão somente quando forem seguros e não alterarem silenciosamente a intenção.

Instrua a LLM a solicitar ou localizar uma entrada ausente quando ela for necessária. Faça-a parar quando a ausência impedir execução segura. Proíba a invenção de fatos, caminhos, decisões, permissões ou aprovações.

### 12. Escreva o procedimento essencial

Converta orientações vagas em etapas ordenadas e imperativas. Para cada etapa, declare a ação, a condição de avanço e o resultado intermediário relevante.

Mantenha no corpo somente o caminho essencial e as decisões frequentes. Mova variantes raras, explicações longas e exemplos extensos para uma referência condicional.

### 13. Defina saídas e conclusão

Declare:

- artefatos ou respostas esperados;
- formato obrigatório;
- campos ou conteúdo mínimo;
- evidências que acompanham a saída;
- condições observáveis de sucesso;
- estados de falha ou conclusão parcial.

Proíba a declaração de conclusão quando uma saída obrigatória, validação ou decisão necessária estiver pendente.

### 14. Declare limites e parada

Adicione limites explícitos para ações fora do escopo, escrita, instalação, acesso a fontes não autorizadas, ampliação de permissões e decisões humanas. Declare o que a skill nunca deve fazer.

Faça a execução parar quando faltar entrada obrigatória, permissão, fonte necessária, gate, validator ou condição segura de continuidade. Exija que a saída informe a causa da parada e o que é necessário para prosseguir.

### 15. Torne a validação objetiva

Associe cada resultado relevante a uma validação e à evidência esperada. Use, conforme o caso:

- verificações estruturais;
- parsers ou validadores;
- testes existentes;
- execução de scripts;
- inspeção de diffs;
- revisão técnica;
- gate humano quando o resultado não puder ser comprovado deterministicamente.

### 17. Mantenha SKILL.md objetivo

Retenha em `SKILL.md` somente:

- propósito;
- quando usar e quando não usar;
- entradas essenciais;
- procedimento essencial;
- saídas;
- limites;
- validações essenciais;
- regras para carregar recursos adicionais.

Remova histórico de discussão, pesquisa bruta, documentação enciclopédica, exemplos repetitivos e detalhes condicionais extensos.

### 18. Mova detalhes para references

Transfira para `references/` o conteúdo consultado apenas em situações específicas, incluindo:

- documentação detalhada;
- exemplos extensos;
- variações condicionais;
- templates e checklists longos;
- referências técnicas;
- notas de plataforma;
- materiais de pesquisa;
- instruções detalhadas sobre ferramentas auxiliares.

Mantenha cada referência autocontida para a situação que atende. Não use `references/` como depósito de conteúdo sem função na execução.

### 19. Defina quando carregar cada referência

Para cada arquivo de `references/`, adicione em `SKILL.md` uma instrução que declare a condição exata de leitura. Use o padrão:

```markdown
- Leia [<arquivo>.md](references/<arquivo>.md) quando <condição observável>.
```

Não instrua a LLM a carregar todas as referências por padrão. Não crie links sem explicar quando o conteúdo é necessário.

### 20. Extraia comportamento determinístico para scripts

Coloque em `scripts/` operações determinísticas, frágeis ou repetitivas que seriam reescritas com frequência. Declare no corpo ou em uma referência:

- quando executar o script;
- entradas aceitas;
- saída esperada;
- códigos ou condições de falha;
- limites de escrita e efeitos colaterais.

Execute cada script adicionado ou uma amostra representativa quando houver muitos scripts equivalentes. Registre a cobertura e não declare o script validado sem evidência de execução.

### 21. Restrinja assets a recursos de saída

Use `assets/` para templates, imagens, fontes, boilerplates ou outros arquivos consumidos na saída. Mova para `SKILL.md` ou `references/` qualquer instrução que a LLM precise ler para decidir ou executar.

Não esconda regras normativas em assets. Não crie assets decorativos que não participem do resultado.

### 22. Elimine duplicação e contradição

Escolha uma única fonte para cada regra. Mantenha a instrução essencial em `SKILL.md` e o detalhe condicional na referência correspondente. Substitua cópias por links com condição de leitura.

Revise nomes, limites, formatos, defaults e critérios de validação em todos os recursos. Corrija qualquer regra que permita ações proibidas em outra parte da skill.

### 23. Torne a skill autocontida

Remova dependências normativas de:

- memória da conversa;
- caminhos absolutos de uma estação de trabalho;
- planos ou blueprints externos ao pacote;
- documentação de um projeto consumidor;
- destinos de instalação usados como fonte de autoridade.

Inclua na própria pasta da skill o conhecimento necessário ou aponte para uma fonte normativa estável dentro do pacote. Use placeholders explícitos para superfícies que devem ser resolvidas pelo projeto consumidor. Não invente caminhos ou presuma que outra LLM conhece o contexto de criação da skill.

### 24. Valide a skill e faça teste prospectivo quando necessário

Conclua a revisão verificando, no mínimo:

- existência de `SKILL.md`;
- frontmatter YAML válido;
- presença de `name` e `description`;
- correspondência entre `name` e pasta;
- validade dos caminhos citados;
- ausência de Markdown solto diretamente sob `skills/`;
- coerência do inventário do pacote;
- ausência de dependências normativas externas proibidas;
- ausência de contradições entre corpo e recursos.

Quando a skill for complexa, de alto risco ou destinada a uso recorrente, teste-a com contexto limpo e uma tarefa realista. Forneça ao avaliador a skill e a tarefa, sem revelar o diagnóstico ou a resposta esperada. Verifique se a skill é acionada corretamente, carrega apenas os recursos necessários, produz a saída contratada e funciona sem contexto oculto.

## Checklist de classificação

Depois de aplicar as correções, responda novamente às 24 perguntas e marque cada item:

- [ ] 1. Papel de conhecimento especializado reutilizável declarado.
- [ ] 2. Capacidade principal, escopo e não escopo definidos.
- [ ] 3. Orquestração, fluxo multiagente, handoffs e estado retomável excluídos.
- [ ] 4. Pasta própria com `SKILL.md` e `references/`.
- [ ] 5. Frontmatter YAML com `name` e `description`.
- [ ] 6. Nome, pasta e namespace coerentes.
- [ ] 7. `description` com capacidade e gatilhos concretos.
- [ ] 8. Condições de uso e exclusões observáveis.
- [ ] 9. Metadados multi-adapter coerentes.
- [ ] 10. Propósito objetivo.
- [ ] 11. Entradas obrigatórias e opcionais definidas.
- [ ] 12. Procedimento essencial, ordenado e imperativo.
- [ ] 13. Saídas e critérios de conclusão verificáveis.
- [ ] 14. Limites, proibições e condições de parada.
- [ ] 15. Validações, evidências e gates proporcionais ao risco.
- [ ] 16. Grau de liberdade adequado à tarefa.
- [ ] 17. `SKILL.md` objetivo e essencial.
- [ ] 18. Detalhes condicionais movidos para `references/`.
- [ ] 19. Condição de leitura declarada para cada referência.
- [ ] 20. Comportamento determinístico em scripts testados.
- [ ] 21. `assets/` restrito a recursos consumidos pela saída.
- [ ] 22. Ausência de duplicação e contradição.
- [ ] 23. Conteúdo autocontido e sem dependência normativa externa proibida.
- [ ] 24. Validação estrutural e teste prospectivo quando necessário.

Conte somente as respostas `sim`. Classifique as instruções da skill pela quantidade obtida:

| Quantidade de “sim” | Classificação | Interpretação |
| ---: | --- | --- |
| 0 a 12 | Ruim | A skill não possui contrato suficiente para oferecer uma capacidade especializada de forma segura e reutilizável. Reescreva as instruções antes de usá-la. |
| 13 a 18 | Boa | A skill possui uma base utilizável, mas ainda deixa lacunas relevantes de escopo, acionamento, estrutura ou validação. |
| 19 a 22 | Muito boa | A skill atende à maior parte dos critérios, mas ainda deve corrigir todas as respostas `não`. |
| 23 a 24 | Excelente | A skill é especializada, objetiva, autocontida, progressivamente carregável e validável. |

Apresente o resultado final neste formato:

```markdown
Classificação: <Ruim | Boa | Muito boa | Excelente>
Respostas “sim”: <quantidade>/24
Respostas “não”: <números das perguntas>
Correções necessárias: <lista das correções correspondentes>
```
