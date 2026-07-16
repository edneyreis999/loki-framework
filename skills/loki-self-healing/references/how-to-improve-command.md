# Como melhorar instruções de comandos

## Perguntas de auditoria

Antes de alterar as instruções do comando, pergunte a si mesma:

1. As instruções do comando contemplam a exigência de declarar explicitamente que exercer o papel de orquestrador significa coordenar o fluxo, selecionar agentes responsáveis, fornecer a cada subagente o contexto de execução necessário e autocontido, acompanhar seus handoffs até um estado terminal e consolidar a resposta?
2. As instruções do comando contemplam a exigência de definir propósito, início, término e resultado esperado de forma verificável?
3. As instruções do comando contemplam a exigência de dividir o fluxo explicitamente nas fases `Input`, `Execution` e `Response`?
4. As instruções do comando contemplam a exigência de a fase `Input` conter a instrução exata “Entre no modo Plan e peça os parâmetros de entrada para o workflow.” e declarar os parâmetros obrigatórios e opcionais em YAML sob `parameters`?
5. As instruções do comando contemplam a exigência de a fase `Input` validar os parâmetros recebidos?
6. As instruções do comando contemplam a exigência de a fase `Input` identificar informações obrigatórias ausentes e solicitá-las ao usuário?
7. As instruções do comando contemplam a exigência de a fase `Input` normalizar a solicitação em uma entrada clara para a fase `Execution`?
8. As instruções do comando contemplam a exigência de impedir que a fase `Input` execute a tarefa principal?
9. As instruções do comando contemplam a exigência de a fase `Execution` interpretar a solicitação e montar um plano de execução?
10. As instruções do comando contemplam a exigência de a fase `Execution` identificar agentes, validators e handoffs necessários e disponibilizar para cada subagente um contexto autocontido suficiente para executar sua tarefa sem depender do contexto privado do comando orquestrador?
11. As instruções do comando contemplam a exigência de delegar trabalho aos agentes apropriados sempre que possível?
12. As instruções do comando contemplam a exigência de acompanhar os handoffs e seus resultados até a conclusão, parada ou bloqueio do fluxo?
13. As instruções do comando contemplam a exigência de aplicar validators, gates e approvals antes das ações que dependem deles?
14. As instruções do comando contemplam a exigência de serializar escritas em arquivos-alvo compartilhados e impedir múltiplos escritores simultâneos no mesmo arquivo?
15. As instruções do comando contemplam a exigência de delegar alterações no projeto para um `Write Agent` apropriado?
16. As instruções do comando contemplam a exigência de permitir escrita direta pelo comando somente quando não existir um `Write Agent` apropriado?
17. As instruções do comando contemplam a exigência de registrar no completion record a oportunidade de criar um `Write Agent` especializado sempre que o comando escrever diretamente?
18. As instruções do comando contemplam a exigência de declarar `allowed_writes`, `forbidden_writes`, owner, validators e gates aplicáveis a qualquer escrita direta excepcional?
19. As instruções do comando contemplam a exigência de declarar condições de parada e um contrato de retomada?
20. As instruções do comando contemplam a exigência de a fase `Response` identificar explicitamente seu consumidor como `LLM`, `Humano` ou `Both`?
21. As instruções do comando contemplam a exigência de responder em XML estruturado quando o consumidor for `LLM`?
22. As instruções do comando contemplam a exigência de responder em Markdown com no máximo 7.000 caracteres quando o consumidor for `Humano`?
23. As instruções do comando contemplam a exigência de responder em Markdown, sem limite de tamanho e legível por ambos, quando o consumidor for `Both`?
24. As instruções do comando contemplam a exigência de a resposta comunicar status, resumo, artefatos, evidências, handoff, riscos e próximos passos?

Responda a cada pergunta somente com `sim` ou `não`. Responda `sim` apenas quando a exigência estiver explícita, verificável e sem contradição em outra parte das instruções. Não infira cobertura a partir de comportamento implícito, nome de seção genérico ou capacidade presumida do executor.

### Unidade de auditoria para command bundle

Quando o command estiver no schema final com `serialization: skill-bundle` sob
`skills/loki-<stem>/`, audite o bundle inteiro como uma unica unidade. Leia
`SKILL.md`, todos os references roteados e
`assets/response-template.md`. Produza exatamente uma resposta 24/24 por bundle
e separe `bundle_score` de blockers estruturais ou semanticos. Para cada item registre:

```text
item -> sim|não -> arquivo -> heading ou trecho -> contradições
```

Nao conceda `sim` por soma implicita: a evidencia precisa estar explicita e
sem contradicao em qualquer arquivo do bundle. Itens 3–8 devem ser verificaveis
no Input; itens 1–2 e 9–19, no Execution e seus splits; itens 20–24, no
Response e no template. O gate final exige 24 respostas `sim`, mesmo quando a
tabela de classificacao geral considere 23 como Excelente.

## Como corrigir cada resposta “não”

Se responder `não` a qualquer pergunta, altere as instruções do comando antes de classificá-las. Aplique a correção de mesmo número usando linguagem imperativa, condições binárias e limites verificáveis.

### 1. Declare o papel de orquestrador

Adicione uma instrução explícita que defina o comando como orquestrador. Defina que exercer esse papel exige:

- coordenar as fases `Input`, `Execution` e `Response`;
- decompor o fluxo em unidades de trabalho com responsáveis identificáveis;
- selecionar agentes responsáveis por cada unidade de trabalho;
- fornecer a cada subagente um contexto de execução autocontido com entrada, objetivo, escopo, limites, fontes relevantes, saída esperada e destino de handoff;
- acompanhar cada handoff até sucesso, falha, bloqueio ou parada explícita;
- aplicar os validators, gates e approvals correspondentes;
- consolidar resultados, evidências, riscos e próximos passos na resposta.

Faça o comando preservar a responsabilidade pelo progresso e pelo estado global do fluxo mesmo depois de delegar. Não considere a seleção ou invocação de um agente como conclusão da unidade de trabalho. Remova instruções que apresentem o comando como executor principal quando houver um agente apropriado para o trabalho.

### 2. Delimite o contrato do comando

Declare:

- propósito;
- condição de início;
- condição de conclusão;
- resultado esperado;
- saídas obrigatórias.

Substitua objetivos vagos por estados observáveis que outra LLM consiga verificar.

### 3. Crie as três fases obrigatórias

Divida as instruções exatamente nestas fases e preserve esta ordem:

1. `Input`;
2. `Execution`;
3. `Response`.

Não misture coleta de entrada, execução da tarefa e composição da resposta na mesma fase.

### 4. Faça a fase Input entrar no modo Plan e declarar os parâmetros em YAML

Faça todo comando iniciar a fase `Input` com esta instrução exata:

```text
Entre no modo Plan e peça os parâmetros de entrada para o workflow.
```

Logo após a instrução, declare os parâmetros obrigatórios e opcionais em um bloco YAML sob a chave `parameters`. Use esta estrutura para cada parâmetro:

```yaml
parameters:
  - key: <nome_do_parametro>
    input_type: <tipo_do_parametro>
    requirement: <required | optional>
    default: <valor default>
    description: <descrição objetiva do parâmetro>
```

Preencha `key`, `input_type`, `requirement` e `description` com valores explícitos. Não substitua o bloco YAML por prosa, tabela ou lista Markdown. Não inicie a fase `Execution` antes de pedir e obter todos os parâmetros marcados como `required`.

### 5. Faça a fase Input validar parâmetros

Defina validações objetivas para presença, tipo, formato, intervalo, existência de caminhos e combinações permitidas. Rejeite entradas inválidas com uma explicação acionável. Não normalize silenciosamente um valor que possa alterar a intenção do usuário.

### 6. Faça a fase Input solicitar informações ausentes

Instrua o comando a identificar cada informação obrigatória ausente e solicitá-la ao usuário. Faça-o interromper o avanço para `Execution` quando a ausência impedir uma execução segura. Não invente valores, aprovações, escopos ou destinos.

### 7. Normalize a entrada para Execution

Exija que a fase `Input` produza um registro normalizado contendo, no mínimo:

- objetivo;
- parâmetros validados;
- escopo;
- restrições;
- destinos de saída;
- approvals e gates conhecidos;
- lacunas ainda abertas.

Faça a fase `Execution` consumir esse registro, e não a solicitação bruta de forma ambígua.

### 8. Isole a fase Input da tarefa principal

Proíba a fase `Input` de implementar, alterar arquivos, executar a tarefa principal ou declarar sucesso. Limite-a à coleta, validação, esclarecimento e normalização da solicitação.

### 9. Faça Execution interpretar e planejar

Instrua a fase `Execution` a transformar a entrada normalizada em um plano com etapas, dependências, responsáveis, validações e critérios de conclusão. Exija replanejamento explícito quando um resultado invalidar uma etapa posterior.

### 10. Identifique os participantes, os controles e o contexto de cada subagente

Parta do princípio de que um subagente não possui automaticamente todo o contexto do comando orquestrador. Antes de invocá-lo, prepare e disponibilize um contexto de execução autocontido, suficiente para que ele execute a tarefa sem depender da memória da conversa ou de informações mantidas apenas pelo orquestrador.

Faça a fase `Execution` identificar:

- agentes necessários e a responsabilidade de cada um;
- validators aplicáveis;
- handoffs de sucesso e falha;
- gates e approvals;
- owner de cada escrita;
- critérios de parada.

Inclua no contexto de execução de cada subagente:

- objetivo da tarefa e motivo pelo qual ela é necessária;
- unidade de trabalho atribuída ao subagente;
- fatos, decisões e restrições relevantes;
- arquivos, caminhos, documentos, evidências e outras fontes que devem ser consultados;
- dependências e resultados anteriores necessários para a tarefa;
- escopo permitido, `allowed_writes` e `forbidden_writes`, quando houver escrita;
- critérios de sucesso, falha e conclusão;
- validators, gates e approvals aplicáveis;
- formato da saída esperada;
- destino e condições do handoff.

Forneça somente o contexto relevante, mas não omita informação necessária para decidir ou executar corretamente. Não invoque um subagente sem contexto, entrada, escopo, saída e destino de handoff definidos. Proíba delegações que dependam de referências implícitas como “conforme discutido”, “continue o trabalho”, “use o contexto acima” ou “faça o restante” sem disponibilizar o conteúdo correspondente.

### 11. Delegue o trabalho apropriado

Instrua o comando a delegar análise, implementação, teste ou revisão ao agente que possua a responsabilidade correspondente. Mantenha no comando a coordenação, o acompanhamento e a consolidação. Permita execução direta apenas nas exceções declaradas pelas próprias instruções.

### 12. Acompanhe os handoffs

Exija que o comando registre para cada handoff:

- origem;
- destino;
- objetivo;
- entrada entregue;
- resultado esperado;
- status;
- evidência recebida;
- próximo destino.

Faça o comando acompanhar cada handoff até sucesso, falha, bloqueio ou parada explícita. Não considere a mera delegação como conclusão.

### 13. Aplique validators, gates e approvals

Associe cada ação sensível ao validator, gate ou approval correspondente. Instrua o comando a verificar o resultado antes de continuar. Faça-o parar quando um controle obrigatório estiver ausente, pendente, rejeitado ou falhar. Não trate validação automática como substituta de decisão humana quando um gate humano for exigido.

### 14. Serialize escritas compartilhadas

Defina um único owner de escrita por arquivo em cada momento. Permita leituras independentes em paralelo, mas serialize operações que possam tocar o mesmo arquivo ou superfície compartilhada. Instrua o comando a detectar sobreposição de escopo antes de delegar e a interromper escritores concorrentes quando houver conflito.

### 15. Delegue alterações para Write Agent

Quando a tarefa exigir criação, modificação, movimentação ou remoção de arquivos do projeto, faça o comando selecionar um `Write Agent` apropriado e entregar-lhe um envelope com:

- arquivos-alvo ou domínio permitido;
- alteração autorizada;
- `allowed_writes` e `forbidden_writes`;
- validators e gates;
- evidências esperadas;
- destino de handoff.

Não transforme o comando no executor principal da mudança quando esse agente existir.

### 16. Restrinja a escrita direta à exceção

Permita que o comando escreva diretamente somente após verificar e registrar que nenhum `Write Agent` apropriado está disponível. Proíba usar conveniência, velocidade ou tamanho da alteração como justificativa para ignorar um agente existente.

Quando a exceção for acionada, faça o comando assumir explicitamente o envelope, os limites, as validações e os gates que seriam exigidos do escritor delegado.

### 17. Registre a lacuna no completion record

Sempre que o comando escrever diretamente, obrigue-o a registrar no completion
record:

- tipo de implementação executada;
- motivo da ausência de um `Write Agent` apropriado;
- oportunidade de criar ou especializar um agente para esse trabalho;
- escopo que o futuro agente deveria assumir;
- evidências e riscos observados.

Não encerre o fluxo sem esse registro. O orquestrador captura o evidence
manifest sanitizado ou declara um gap explícito; não dispare retrospectiva como
fallback automático.

### 18. Proteja qualquer escrita direta

Declare previamente, mesmo para a exceção:

- `allowed_writes` exatos;
- `forbidden_writes` explícitos;
- owner único;
- validators;
- gates e approvals;
- critérios de sucesso e falha;
- evidências obrigatórias.

Proíba escrita fora do envelope e ampliação silenciosa do escopo. Faça o comando parar e solicitar decisão quando a implementação exigir arquivos ou permissões não autorizados.

### 19. Defina parada e retomada

Adicione condições de parada para, no mínimo:

- entrada obrigatória ausente;
- escopo ou permissão insuficiente;
- gate ou approval pendente;
- validator ausente ou falho;
- conflito entre escritores;
- handoff sem destino;
- dependência indisponível;
- decisão humana necessária.

Defina um contrato de retomada com estado atual, etapas concluídas, pendências, evidências preservadas, próxima ação e condição necessária para continuar. Não reinicie o fluxo do zero quando o estado puder ser retomado com segurança.

### 20. Declare o consumidor da Response

Faça a fase `Response` declarar um único consumidor principal:

- `LLM`;
- `Humano`;
- `Both`.

Assuma que o comando foi iniciado por uma pessoa, mas não presuma que a resposta final será consumida somente por ela. Se o consumidor não estiver definido e essa escolha alterar o formato, faça o comando resolvê-lo antes de responder.

### 21. Estruture a resposta para LLM em XML

Quando o consumidor for `LLM`, exija XML válido, estável e parseável. Use no mínimo esta estrutura:

```xml
<command_response>
  <summary></summary>
  <status></status>
  <artifacts></artifacts>
  <evidence></evidence>
  <handoff></handoff>
  <risks></risks>
  <next_steps></next_steps>
</command_response>
```

Permita extensões específicas do comando, mas preserve nomes previsíveis, fechamento correto das tags e ausência de prosa solta fora do elemento raiz.

### 22. Limite a resposta para Humano

Quando o consumidor for `Humano`, exija Markdown claro, conciso e acionável com no máximo 7.000 caracteres. Priorize resultado, estado, decisões necessárias, riscos e próximos passos. Remova detalhes internos que não ajudem a pessoa a agir.

### 23. Formate a resposta para Both

Quando o consumidor for `Both`, exija Markdown legível por humanos e estruturado o suficiente para outra LLM recuperar campos e decisões. Não aplique o limite de 7.000 caracteres. Use títulos, listas, tabelas ou blocos estruturados apenas quando melhorarem a recuperação e a leitura.

### 24. Complete o conteúdo da Response

Exija que toda resposta, independentemente do consumidor, comunique:

- resumo do resultado;
- status final ou atual;
- artefatos criados, alterados ou analisados;
- evidências e validações;
- handoffs concluídos ou pendentes;
- gates e approvals pendentes;
- falhas, lacunas e riscos residuais;
- próximos passos e responsável esperado.

Proíba a declaração de conclusão quando houver gate pendente, validação falha, handoff aberto ou condição de parada ainda ativa.

## Checklist de classificação

Depois de aplicar as correções, responda novamente às 24 perguntas e marque cada item:

- [ ] 1. Papel de orquestrador definido por coordenação do fluxo, seleção de agentes responsáveis, fornecimento de contexto autocontido, acompanhamento de handoffs e consolidação da resposta.
- [ ] 2. Propósito, início, término e resultado verificáveis.
- [ ] 3. Fases `Input`, `Execution` e `Response` separadas.
- [ ] 4. Instrução para entrar no modo Plan e parâmetros obrigatórios e opcionais declarados em YAML sob `parameters`.
- [ ] 5. Parâmetros validados.
- [ ] 6. Informações obrigatórias ausentes solicitadas.
- [ ] 7. Entrada normalizada para execução.
- [ ] 8. Fase `Input` sem execução da tarefa principal.
- [ ] 9. Interpretação e plano na fase `Execution`.
- [ ] 10. Agentes, validators e handoffs identificados, com contexto de execução autocontido disponibilizado para cada subagente.
- [ ] 11. Trabalho delegado aos agentes apropriados.
- [ ] 12. Handoffs acompanhados até estado terminal.
- [ ] 13. Validators, gates e approvals aplicados.
- [ ] 14. Escritas compartilhadas serializadas.
- [ ] 15. Alterações delegadas para `Write Agent`.
- [ ] 16. Escrita direta restrita à ausência de `Write Agent` apropriado.
- [ ] 17. Lacuna de `Write Agent` registrada no completion record.
- [ ] 18. Escrita direta protegida por envelope e controles.
- [ ] 19. Condições de parada e contrato de retomada.
- [ ] 20. Consumidor da resposta declarado.
- [ ] 21. Resposta para `LLM` em XML.
- [ ] 22. Resposta para `Humano` em Markdown com até 7.000 caracteres.
- [ ] 23. Resposta para `Both` em Markdown sem limite de tamanho.
- [ ] 24. Resposta completa e coerente com o estado do fluxo.

Conte somente as respostas `sim`. Classifique as instruções do comando pela quantidade obtida:

| Quantidade de “sim” | Classificação | Interpretação |
| ---: | --- | --- |
| 0 a 12 | Ruim | O comando não possui contrato suficiente para orquestrar com segurança. Reescreva as instruções antes de usá-lo. |
| 13 a 18 | Boa | O comando possui uma base utilizável, mas ainda deixa lacunas relevantes no fluxo, na delegação ou nos controles. |
| 19 a 22 | Muito boa | O comando atende à maior parte dos critérios, mas ainda deve corrigir todas as respostas `não`. |
| 23 a 24 | Excelente | O comando é explícito, orquestrável, validável e adequado ao consumidor declarado. |

Apresente o resultado final neste formato:

```markdown
Classificação: <Ruim | Boa | Muito boa | Excelente>
Respostas “sim”: <quantidade>/24
Respostas “não”: <números das perguntas>
Correções necessárias: <lista das correções correspondentes>
```
