# Remover compatibilidade legacy do Loki Framework

## Contexto

O pacote Loki Framework acumula compatibilidade com contratos, schemas,
instalações, projeções e estados antigos. Essa compatibilidade aumenta a
complexidade dos validadores, mantém caminhos de fallback e dificulta a
evolução do contrato canônico.

## Demanda

Remover toda compatibilidade legacy do pacote Loki Framework e consolidar um
único formato, contrato e fluxo operacional suportado.

## Escopo

- definir o schema e contrato único atualmente suportado;
- remover leitores, branches, flags, fixtures e fallbacks legacy;
- simplificar a instalação, removendo fluxos de migração e limpeza de comandos
  antigos;
- atualizar validadores, templates, mirrors, skills, commands e workflows;
- remover campos e caminhos legacy de evidência, retrospectiva e inferência;
- alinhar projeções Goose, Codex e Claude ao contrato canônico;
- atualizar `manifest.yaml`, `install-scopes.json`, README e documentação;
- substituir testes de retrocompatibilidade por testes de rejeição explícita de
  formatos antigos;
- preservar apenas usos de “compatibilidade” que sejam de domínio do produto,
  como diagnóstico de plugins RPG Maker, quando não forem compatibilidade do
  próprio Loki Framework.

## Fora de escopo

- alterações em projetos consumidores sem autorização explícita;
- remoção de compatibilidade funcional de domínios externos ao framework;
- migração automática de planos, evidências ou instalações antigas;
- commit, publicação ou abertura de Pull Request.

## Critérios de aceitação

1. Existe um único contrato/schema suportado e documentado.
2. Entradas legacy falham explicitamente, sem fallback silencioso.
3. Não restam branches de leitura, migração ou fallback legacy no pacote.
4. Templates raiz e mirrors permanecem idênticos quando aplicável.
5. Manifesto, inventário operacional, instalação e documentação estão alinhados.
6. Os validadores cobrem apenas o formato novo e rejeitam formatos antigos.
7. O pacote passa nas verificações de integridade, parsing, paridade e
   instalação previstas nos guardrails.

## Estimativa preliminar

- mínimo: 3–5 dias, limitado a contratos agentic/WTR e instalação;
- provável: 1–2 semanas, incluindo skills, templates, evidência, inferência,
  Goose e documentação;
- completo: 2–4 semanas, caso seja necessário verificar consumidores,
  persistência e todas as projeções de adapters.

## Riscos principais

- quebrar instalações existentes;
- invalidar planos ou evidências persistidos;
- remover compatibilidade de domínio que não pertence ao framework;
- deixar divergências entre templates, mirrors ou adapters;
- remover apenas ocorrências literais de `legacy` e manter fallbacks semânticos.

## Próximo passo

Executar um inventário read-only classificando cada ocorrência como
compatibilidade do framework, compatibilidade de domínio ou uso semântico não
relacionado, antes de gerar o plano executável.
