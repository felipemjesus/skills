# 0005. Framework first

- **Status:** Proposta
- **Data:** {{USUARIO: AAAA-MM-DD}}

## Contexto

Os primeiros desenhos do projeto previam várias peças próprias: relógio e gerador de ID injetáveis, tipo `Result` próprio, publicador de eventos com outbox e relay, interfaces de autorização e de feature flags, entidade e mapper separados mesmo quando o model do ORM já é a entidade idiomática, builders de teste escritos à mão quando a biblioteca de testes ou o ORM oferecem factories. Cada peça é razoável isoladamente, mas o conjunto deixa a aplicação diferente do que a documentação do framework mostra. Isso custa caro para pessoas (que não reconhecem o projeto) e para agentes de código (que conhecem bem o idioma do framework e erram quando o projeto foge dele).

{{AGENTE: FRAMEWORK}} e as bibliotecas adotadas já oferecem a maior parte disso: injeção de dependência, eventos e filas, autorização, flags, cliente HTTP com retry, controle de tempo e fakes em testes, geração de IDs, tratamento de erros HTTP.

## Opções consideradas

1. **Arquitetura independente de framework.** Domínio puro, toda dependência atrás de interface, infraestrutura própria. Portável, mas com muito código de cerimônia e distante do idioma do framework.
2. **Framework first.** Usar os recursos que o framework e as bibliotecas documentam, do jeito que a documentação mostra; solução própria só quando o framework não oferece.
3. **Livre por caso.** Cada pessoa decide. Rápido no início, inconsistente com o tempo.

## Decisão

Opção 2.

- Antes de criar abstração, utilitário, wrapper, camada ou infraestrutura, procure o recurso na documentação oficial do framework e das bibliotecas adotadas e use-o como a documentação mostra.
- Solução própria só quando o framework não oferece, com justificativa no PR ou em ADR.
- A estrutura de pastas e as escolhas de modelagem seguem o idioma do framework: {{AGENTE: ENTIDADE: model do ORM (active record) ou classe de domínio separada — seguir o idioma do framework}}; comandos e eventos por {{AGENTE: MECANISMO_DE_COMANDOS_E_EVENTOS_DO_FRAMEWORK}}; autorização por {{AGENTE: MECANISMO_DE_AUTORIZACAO_DO_FRAMEWORK}}; flags por {{AGENTE: MECANISMO_DE_FEATURE_FLAGS}}.
- Dependências do próprio framework (autorização, flags, cache, filas, cliente HTTP, relógio) **não** ganham interface: use o recurso direto e, nos testes, os fakes e helpers que o framework oferece.
- **Versão estável mais recente.** Frameworks, bibliotecas e runtime usam, sempre que possível, a versão estável mais recente (sem alpha, beta, RC ou canary); no runtime, a versão estável com suporte ativo (LTS ativa, quando houver). A fonte de verdade da versão é o manifesto + lockfile ({{AGENTE: MANIFESTO_E_LOCKFILE}}); os documentos não citam números de versão.
- **Atualizações:** patch e minor automatizadas pela ferramenta de atualização de dependências ([SECURITY.md](../../SECURITY.md#6-dependências-e-cadeia-de-suprimentos)), com CI verde. **Major** em PR próprio, seguindo o guia de migração oficial, sem misturar com funcionalidade; ADR quando houver quebra de contrato ou mudança de abordagem.
- **Exceção** (ficar numa versão anterior): registrada com motivo, critério de saída (o que precisa acontecer para atualizar) e issue.
- **Sintaxe e API da versão instalada:** código novo usa a forma recomendada pela documentação da versão instalada, mesmo quando a antiga ainda funciona; nada de API marcada como obsoleta ([CODING_GUIDELINES.md](../../CODING_GUIDELINES.md#versões-e-sintaxe-atual)).
- A regra de interfaces da [ADR-0004](0004-interfaces-so-em-fronteiras.md) continua: `Port` só para sistema externo, LLM, mais de uma implementação real e API pública entre módulos.
- O código de negócio pode usar os recursos do framework que fazem parte do modelo idiomático (ex.: models do ORM, decorators de handlers e eventos). Continua proibido: chamar sistema externo ou LLM sem `Port` e escrever regra de negócio em controller.
- Framework first **não** relaxa a separação de responsabilidades: o recurso do framework é usado no artefato responsável por ele ([ARCHITECTURE.md](../../ARCHITECTURE.md#41-responsabilidades)). Consultas e persistência do ORM só no repository (concreto, sem interface), mesmo quando o model do ORM é a entidade; controller e request não recebem repository; regra de negócio só em entidade, VO, enum e serviço de domínio.

## Consequências

- **Positivas:** menos código próprio para manter; o projeto parece um projeto típico do framework; agentes e pessoas novas aplicam o que já sabem da documentação; testes usam os helpers oficiais.
- **Negativas:** o código de negócio fica acoplado ao framework e trocar de framework fica mais caro (evento raro, aceito); atualizações de versão do framework afetam mais código e precisam ser acompanhadas.
- **Mitigação:** regra de negócio continua concentrada no domínio (entidade, serviço de domínio), fronteiras externas continuam atrás de `Port` e as regras de dependência entre fatias e módulos continuam verificadas no CI.
- **Quando revisitar:** o framework deixar de ser mantido, ou um recurso dele se mostrar insuficiente de forma recorrente (registrar a exceção em ADR).
