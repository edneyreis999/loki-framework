# Como melhorar instruções de agentes

## Perguntas de auditoria

Antes de alterar as instruções do agente, pergunte a si mesma:

1. As instruções do agente contemplam a exigência de declarar explicitamente uma única categoria entre `Write Agent`, `Write Test Agent` e `Read-Only / Proposal-Only Agent`?
2. As instruções do agente contemplam a exigência de definir uma responsabilidade principal estreita e compatível com a categoria declarada?
3. As instruções do agente contemplam a exigência de subordinar o modo `read-only`, `proposal-only` ou `scoped-writer` à categoria declarada, sem usar o modo como substituto da categoria?
4. As instruções do agente contemplam a exigência de declarar gatilhos, entradas, saídas e critérios de conclusão verificáveis?
5. As instruções do agente contemplam a exigência de declarar `allowed_writes` compatíveis com a categoria e limitados a caminhos ou domínios recebidos em um envelope aprovado?
6. As instruções do agente contemplam a exigência de declarar `forbidden_writes` que impeçam alterações incompatíveis com a categoria?
7. As instruções do agente contemplam a exigência de conhecer o destino do handoff antes de iniciar o trabalho?
8. As instruções do agente contemplam a exigência de declarar os destinos de handoff para sucesso e falha quando ambos forem aplicáveis?
9. As instruções do agente contemplam a exigência de obter evidências de validação suficientes antes de realizar o handoff e de separar validações determinísticas de gates de teste humano?
10. As instruções do agente contemplam a exigência de declarar condições de parada para escopo ausente, permissão insuficiente, conflito, validação inviável ou destino de handoff indefinido?
11. As instruções do agente contemplam a exigência de retornar um formato estruturado com resumo, arquivos afetados, evidências, validações, riscos residuais e próximo destino?
12. As instruções do agente contemplam a exigência de limitar ferramentas, permissões e gates ao mínimo necessário para sua responsabilidade?
13. Se o agente for um `Write Agent`, as instruções contemplam a exigência de escrever somente dentro de um envelope aprovado com arquivos-alvo ou domínio permitido, validações esperadas e destino de handoff?
14. Se o agente for um `Write Agent`, as instruções contemplam a exigência de validar a implementação antes do handoff com testes, execução, scripts ou verificações adequadas à mudança?
15. Se o agente for um `Write Agent`, as instruções contemplam a exigência de armazenar testes e scripts temporários em `<root>/planos/0xx-<plan-description>/builds/faseX/`?
16. Se o agente for um `Write Agent`, as instruções contemplam a exigência de remover artefatos temporários antes do handoff, salvo para preservar evidências temporárias em `/planos`?
17. Se o agente for um `Write Agent`, as instruções contemplam a exigência de não persistir testes finais e de fornecer uma especificação completa para testes determinísticos?
18. Se o agente for um `Write Agent`, as instruções contemplam a exigência de quando a alteração não puder ser validada completamente de forma determinística fornecer um roteiro executável para essa validação no handoff?
19. Se o agente for um `Write Agent`, as instruções contemplam a exigência de executar `loki-retrospectiva-tecnica` antes de todo handoff?
20. Se o agente for um `Write Agent`, as instruções contemplam a exigência de usar `docs/loki-init/<agent-name>/` como documentação própria e consultar documentação relevante no pre-flight?
21. Se o agente for um `Write Test Agent`, as instruções contemplam a exigência de modificar somente arquivos da suíte de testes e persistir os testes determinísticos finais?
22. Se o agente for um `Write Test Agent`, as instruções contemplam a exigência de definir handoffs distintos para sucesso e falha e executar `loki-retrospectiva-tecnica` antes de cada handoff?
23. Se o agente for um `Read-Only / Proposal-Only Agent`, as instruções contemplam a exigência de proibir qualquer modificação ou criação persistente no projeto?
24. Se o agente for um `Read-Only / Proposal-Only Agent`, as instruções contemplam a exigência de devolver análise, proposta ou handoff estruturado quando identificar uma alteração necessária?

Responda a cada pergunta somente com `sim` ou `não`. Responda `sim` apenas quando a exigência estiver explícita, verificável e sem contradição em outra parte do contrato.

Nas perguntas condicionais, responda `sim` quando a regra estiver corretamente definida para a categoria correspondente. Se o agente pertencer a outra categoria, responda `sim` somente quando as instruções não concederem por engano a capacidade descrita e mantiverem as permissões coerentes com a categoria declarada. Não use `não aplicável`.

## Como corrigir cada resposta “não”

Se responder `não` a qualquer pergunta, altere as instruções do agente antes de classificá-las. Aplique a correção correspondente usando linguagem imperativa, critérios binários e limites verificáveis.

### 1. Declare a categoria

Adicione um campo ou uma instrução explícita que classifique o agente em exatamente uma destas categorias:

- `Write Agent`: implementa alterações em superfícies aprovadas de produção, conteúdo, configuração ou documentação;
- `Write Test Agent`: cria e mantém somente testes determinísticos persistentes;
- `Read-Only / Proposal-Only Agent`: analisa e propõe sem modificar o projeto.

Não misture categorias no mesmo contrato. Se o agente precisar assumir responsabilidades de categorias diferentes, separe os papéis em agentes distintos e conecte-os por handoff.

### 2. Restrinja a responsabilidade principal

Descreva uma única responsabilidade principal. Remova objetivos paralelos que transformem o agente em orquestrador genérico. Faça a responsabilidade corresponder à categoria declarada e indique claramente o que o agente não faz.

### 3. Subordine o modo à categoria

Mantenha `read-only`, `proposal-only` e `scoped-writer` apenas como modos operacionais subordinados à categoria:

- use `read-only` ou `proposal-only` para `Read-Only / Proposal-Only Agent`;
- use `scoped-writer` para `Write Agent` somente dentro do envelope aprovado;
- use escrita escopada exclusivamente à suíte de testes para `Write Test Agent`.

Não trate `scoped-writer` como permissão ampla nem como categoria suficiente.

### 4. Torne o contrato executável

Declare gatilhos concretos, entradas obrigatórias, saídas esperadas e critérios de conclusão observáveis. Substitua termos vagos por condições que outra LLM consiga verificar com `sim` ou `não`.

### 5. Delimite os allowed writes

Declare os `allowed_writes` de acordo com a categoria. Para agentes que escrevem, exija caminhos exatos, arquivos-alvo ou domínios permitidos recebidos pelo workflow chamador. Proíba escrita fora do envelope, mesmo quando o arquivo parecer relacionado.

### 6. Delimite os forbidden writes

Liste proibições explícitas por categoria:

- proíba o `Write Agent` de escrever fora do envelope e de persistir testes finais que pertencem ao `Write Test Agent`;
- proíba o `Write Test Agent` de alterar código de produção, configuração da aplicação, documentação funcional, assets, dados de runtime ou qualquer arquivo fora da suíte de testes;
- proíba o `Read-Only / Proposal-Only Agent` de criar, modificar, mover ou remover qualquer arquivo persistente.

### 7. Defina o handoff antes do início

Exija que o agente receba o destino do handoff antes de começar. Faça o agente parar e solicitar um destino quando essa informação estiver ausente. Para um `Write Agent`, permita handoff somente para o orquestrador ou para o `Write Test Agent` responsável pela validação.

### 8. Defina destinos de sucesso e falha

Declare `success_destination` e `failure_destination` quando o fluxo puder terminar de formas diferentes. Direcione o sucesso ao próximo agente ou ao orquestrador. Direcione a falha ao agente capaz de corrigir o problema, normalmente o `Write Agent`, ou ao orquestrador quando não houver owner de correção definido.

### 9. Exija validação antes do handoff

Obrigue agentes que escrevem ou testam a validar antes do handoff. Exija evidências proporcionais à alteração, como execução da aplicação, testes existentes, testes temporários, scripts temporários, verificações manuais assistidas ou outra validação adequada.

Faça o agente separar explicitamente:

- validações determinísticas que ele próprio executou e cujos resultados são reproduzíveis;
- testes humanos exigidos porque o resultado depende de percepção, julgamento ou comportamento que não pode ser comprovado completamente por uma asserção determinística.

Proíba handoff com alegação de sucesso sem evidência suficiente.

### 10. Adicione condições de parada

Faça o agente parar quando faltar escopo, arquivo-alvo, domínio permitido, permissão, validator, gate, contexto de plano e fase necessário, destino de handoff ou critério para resolver um conflito. Exija devolução ao orquestrador quando continuar demandar ampliar o envelope ou tomar uma decisão humana.

### 11. Estruture a resposta

Exija uma resposta consolidada contendo, no mínimo:

- categoria e responsabilidade executada;
- resumo do resultado;
- arquivos analisados e arquivos alterados;
- escopo de escrita recebido e utilizado;
- validações executadas e evidências obtidas;
- testes humanos executados, resultados registrados e gates ainda pendentes;
- falhas, lacunas e riscos residuais;
- artefatos temporários criados e removidos;
- destino e motivo do próximo handoff.

### 12. Minimize ferramentas, permissões e gates

Conceda somente as ferramentas e permissões necessárias. Remova capacidades que não participem da responsabilidade principal. Declare gates humanos ou técnicos para alterações sensíveis, ampliação de escopo e validação em superfícies que dependam de percepção humana.

### 13. Proteja o envelope do Write Agent

Exija que o `Write Agent` receba antes da execução:

- arquivos-alvo ou domínio permitido;
- alterações autorizadas;
- validators esperados;
- gates aplicáveis;
- destino de handoff.

Proíba o agente de inferir permissão de escrita fora desse envelope.

### 14. Faça o Write Agent validar a implementação

Instrua o `Write Agent` a selecionar e executar validações compatíveis com a mudança. Permita execução da aplicação, testes existentes, testes temporários, scripts temporários e verificações manuais assistidas. Exija que ele registre comandos, resultados e evidências antes de declarar a implementação concluída.

### 15. Isole testes e scripts temporários

Instrua o `Write Agent` a criar artefatos temporários somente em:

```text
<root>/planos/0xx-<plan-description>/builds/faseX/
```

Exija que o plano e a fase venham do handoff. Permita inferi-los da estrutura do projeto somente quando a correspondência for inequívoca; caso contrário, faça o agente parar e solicitar o contexto ausente.

### 16. Remova artefatos temporários

Obrigue o `Write Agent` a remover, antes do handoff, testes, scripts e ferramentas auxiliares criados exclusivamente para validação. Permita preservá-los em `/planos`.

### 17. Separe implementação de testes finais

Proíba o `Write Agent` de persistir a suíte de testes final. Exija que ele entregue ao `Write Test Agent` uma especificação determinística contendo:

- comportamentos a validar;
- entradas a utilizar;
- saídas esperadas;
- casos de sucesso;
- casos de falha;
- invariantes a preservar;
- regressões específicas a prevenir.

Não aceite uma instrução genérica como “adicione testes”.

### 18. Exija teste humano para alterações não determinísticas

Considere que uma alteração exige teste humano quando seu resultado não puder ser comprovado completamente por testes determinísticos e depender de percepção, julgamento ou interação humana. Isso inclui, quando aplicável:

- aparência e estado visual;
- clareza, fluidez ou sensação de um fluxo de UX;
- animação, transição e sincronização perceptível;
- áudio, volume, mixagem ou sincronização sonora;
- resposta de input e sensação de controle;
- comportamento de runtime dependente de interação;
- qualquer resultado subjetivo, perceptível ou não reduzível com segurança a entradas e saídas determinísticas.

Quando identificar uma dessas condições, instrua o `Write Agent` a:

1. declarar explicitamente que a mudança exige teste humano;
2. abrir ou registrar o `<human_validation_gate>` antes do handoff;
3. identificar a pessoa ou o destino responsável pela validação;
4. fornecer um roteiro executável de teste humano;

Exija que o roteiro de teste humano contenha:

- ambiente e pré-condições;
- estado inicial;
- passos exatos que a pessoa deve executar;
- comportamento observável esperado;
- critérios objetivos de aprovação, mesmo quando o julgamento final for perceptivo;
- sinais de falha ou rejeição;
- evidência a registrar, como observação, captura, vídeo, áudio ou descrição do resultado;
- destino do feedback quando o teste falhar.

Mantenha os testes humanos complementares aos testes determinísticos. Exija ambos quando partes diferentes da mudança puderem ser verificadas de formas diferentes.

### 19. Exija retrospectiva do Write Agent

Instrua o `Write Agent` a executar `loki-retrospectiva-tecnica` antes de todo handoff usando o contexto da própria janela.

### 20. Preserve documentação própria do Write Agent

Exija uma pasta de documentação em:

```text
docs/loki-init/<agent-name>/
```

Instrua o agente a consultar essa pasta e a documentação relevante do projeto no pre-flight. Permita consultar o agente `bibliotecario` em paralelo para localizar decisões, ferramentas, padrões e implementações semelhantes. Não transforme essa consulta em permissão para escrever documentação fora do envelope recebido.

### 21. Restrinja o Write Test Agent à suíte de testes

Permita ao `Write Test Agent` criar, modificar e persistir somente testes determinísticos. Faça-o construir os testes a partir da especificação recebida do `Write Agent` e cobrir comportamentos, entradas, saídas, sucessos, falhas, invariantes e regressões. Proíba qualquer correção direta em produção; quando um teste revelar defeito, exija handoff ao responsável pela implementação.

### 22. Complete o fluxo do Write Test Agent

Exija que o `Write Test Agent` conheça antes do início:

- o destino de sucesso, usado quando todos os testes passam;
- o destino de falha, normalmente o `Write Agent` responsável pela implementação;
- a suíte e os arquivos de teste que pode modificar.

Instrua-o a executar `loki-retrospectiva-tecnica` antes de cada handoff e registrar testes criados, resultados, falhas, lacunas da especificação, riscos e recomendação de próximo destino.

### 23. Torne o Read-Only / Proposal-Only Agent realmente não escritor

Proíba explicitamente qualquer criação, alteração, movimentação ou remoção persistente. Limite o agente a ler, analisar, responder, revisar, identificar riscos e produzir propostas. Não conceda exceções implícitas para documentação, notas, configuração ou arquivos temporários.

### 24. Exija proposta ou handoff estruturado

Quando a análise identificar necessidade de mudança, instrua o `Read-Only / Proposal-Only Agent` a devolver ao orquestrador uma proposta com evidência, arquivos afetados, alteração recomendada, riscos, validações necessárias e próximo passo. Proíba o agente de aplicar a própria recomendação.

## Checklist de classificação

Depois de aplicar as correções, responda novamente às 24 perguntas e marque cada item:

- [ ] 1. Categoria explícita.
- [ ] 2. Responsabilidade estreita e compatível.
- [ ] 3. Modo subordinado à categoria.
- [ ] 4. Gatilhos, entradas, saídas e conclusão verificáveis.
- [ ] 5. Allowed writes escopados.
- [ ] 6. Forbidden writes compatíveis.
- [ ] 7. Destino de handoff conhecido antes do início.
- [ ] 8. Destinos de sucesso e falha definidos.
- [ ] 9. Validação obrigatória antes do handoff.
- [ ] 10. Condições de parada explícitas.
- [ ] 11. Resposta estruturada.
- [ ] 12. Ferramentas, permissões e gates mínimos.
- [ ] 13. Envelope aprovado do Write Agent.
- [ ] 14. Validação da implementação pelo Write Agent.
- [ ] 15. Local correto para artefatos temporários.
- [ ] 16. Remoção dos artefatos temporários.
- [ ] 17. Especificação para testes determinísticos.
- [ ] 18. Gate e roteiro de teste humano para alterações não determinísticas.
- [ ] 19. Retrospectiva do Write Agent.
- [ ] 20. Documentação própria e pre-flight documental.
- [ ] 21. Escrita do Write Test Agent restrita a testes.
- [ ] 22. Handoffs e retrospectiva do Write Test Agent.
- [ ] 23. Proibição total de escrita do Read-Only / Proposal-Only Agent.
- [ ] 24. Proposta ou handoff estruturado do Read-Only / Proposal-Only Agent.

Conte somente as respostas `sim`. Classifique as instruções do agente pela quantidade obtida:

| Quantidade de “sim” | Classificação | Interpretação |
| ---: | --- | --- |
| 0 a 12 | Ruim | O contrato permite ambiguidade operacional, escrita indevida ou handoff incompleto. Reescreva as regras antes de usar o agente. |
| 13 a 18 | Boa | O contrato possui uma base utilizável, mas ainda deixa lacunas relevantes de categoria, permissão, validação ou handoff. |
| 19 a 22 | Muito boa | O contrato é consistente na maior parte dos critérios, mas ainda precisa corrigir as respostas `não` antes de ser considerado completo. |
| 23 a 24 | Excelente | O contrato é explícito, escopado, validável e adequado à categoria declarada. |

Apresente o resultado final neste formato:

```markdown
Classificação: <Ruim | Boa | Muito boa | Excelente>
Respostas “sim”: <quantidade>/24
Respostas “não”: <números das perguntas>
Correções necessárias: <lista das correções correspondentes>
```
