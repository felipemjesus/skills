# 0002. Monolito modular com fatias verticais e domínio rico

- **Status:** Proposta
- **Data:** {{USUARIO: AAAA-MM-DD}}

## Contexto

O produto está no início, com domínio ainda sendo descoberto e um time de {{USUARIO: N}} pessoas, que trabalha em grande parte com agentes de IA. Precisamos de:
- velocidade de entrega e operação simples;
- fronteiras claras para que mudanças fiquem locais (bom para pessoas e para agentes, que trabalham melhor com contexto delimitado);
- possibilidade de extrair partes para serviços no futuro, se necessário;
- uma organização interna do módulo em que uma tarefa típica (um caso de uso) fique em poucos arquivos próximos, sem perder um modelo de domínio que concentre as regras de negócio.

## Princípio

A organização interna do módulo é escolhida pelo custo de achar e ler um caso de uso:
- **um nome de negócio em toda a cadeia** (rota, Request, Command, Handler, transição, evento), para que uma busca textual ache tudo;
- **localização dedutível:** mesmo gabarito em todo caso de uso, papel no sufixo, árvore rasa, sem pasta de camada técnica dentro da fatia;
- **o arquivo do caso de uso é o roteiro real**, lido de cima para baixo, sem terceirizar a sequência para um service do agregado.

## Opções consideradas

1. **Microsserviços desde o início.** Isolamento forte, mas custo operacional alto (deploy, rede, consistência distribuída, observabilidade) e fronteiras erradas caras de corrigir enquanto o domínio ainda muda. Por que não: o domínio ainda muda.
2. **Monolito em camadas tradicional.** Simples, mas sem fronteiras de negócio; tende a virar uma "grande bola de lama". Por que não: não há fronteira de módulo.
3. **Monolito modular com módulos hexagonais em camadas** (`domain`, `application/{commands,queries,ports,event-handlers}`, `infrastructure`, `interface`). Por que não: até 5 níveis de pasta; um caso de uso espalhado por 4 ou 5 diretórios.
4. **Fatias verticais puras**, sem domínio compartilhado. Por que não: a regra de negócio se espalha e se duplica entre fatias (domínio anêmico).
5. **Organização por conceito:** uma pasta por agregado com os casos de uso dentro e o papel no sufixo. Conceito inteiro numa pasta e estrutura rasa. Por que não: tende a juntar todos os casos de uso do agregado num `*Service` que cresce até misturar tudo, o maior custo de leitura observado; rejeitada.
6. **Pastas por tipo do framework com subcaminho `Conceito/Verbo` espelhado** (controllers, requests e ações em árvores separadas). Idiomático para quem conhece o framework; funciona quando o nome se repete igual em todas as árvores. Contra: um caso de uso fica em 3 a 5 árvores e o espelhamento quebra fácil (singular × plural).
7. **Fatias verticais com domínio rico:** uma pasta por caso de uso em `features/` (controller, request, command/query, handler), uma pasta plana por tipo de arquivo no módulo (`entities/` com entidades com comportamento, `events/`, `exceptions/`, `ports/`, `repositories/` com repositories concretos, únicos com ORM, `clients/` com as implementações dos Ports, ...) e `listeners/` para reações. O sufixo do nome indica a pasta; nada de gavetas genéricas como `domain/` e `infra/`.

## Decisão

Opção 7 como padrão; opção 6 como **variante aceita** para bases que já seguem as pastas do framework, com duas regras: mesmo subcaminho e mesmo número gramatical em todas as árvores, e verificação automática do espelhamento no CI.

Um deploy único; código dividido em `src/modules/<contexto>/` com `features/<caso-uso>/`, uma pasta por tipo de arquivo (`entities/`, `enums/`, `events/`, `exceptions/`, `services/`, `specifications/`, `policies/`, `dtos/`, `ports/`, `repositories/`, `mappers/`, `clients/`, `jobs/`; cada uma só quando houver arquivo para ela) e `listeners/`, mais `api/` (API pública: interface `<Modulo>Api` + `<Modulo>Facade` que só delega aos handlers do módulo), `index` (exporta só o registro do módulo e `api/`) e `<modulo>.module` (registro do módulo no framework). Os nomes de pasta seguem a capitalização do idioma do framework; onde ele tem pasta convencional para uma peça (ex.: `Models/` quando o model do ORM é a entidade), use a dele dentro do módulo e mantenha `features/` como pasta das fatias ([ADR-0005](0005-framework-first.md)). Cada transição de estado é uma fatia. Nomes em português do Brasil com sufixos técnicos em inglês (`CriarVendaHandler`, `VendaCriadaEvent`). Comunicação entre módulos pela interface `<Modulo>Api` injetada ou por eventos; outro módulo só importa `api/`. Regras de dependência verificadas no CI:

- as pastas de domínio (`entities/`, `enums/`, `events/`, `exceptions/`, `services/`, `specifications/`, `policies/`, `dtos/`, `ports/`) não importam `repositories/`, `mappers/`, `clients/`, `jobs/`, `features/`, `listeners/` nem ORM, HTTP ou SDKs de sistemas externos; podem usar os recursos do framework que fazem parte do modelo idiomático (ex.: model do ORM como entidade);
- uma fatia não importa outra fatia;
- ORM e SQL só no repository (concreto, em `repositories/`), inclusive leituras; controller e request não recebem repository ([ARCHITECTURE.md](../../ARCHITECTURE.md#41-responsabilidades));
- fronteira externa (sistema externo, LLM) só via Port ([ADR-0004](0004-interfaces-so-em-fronteiras.md));
- `clients/` contém as implementações dos Ports; `repositories/`, `mappers/` e `clients/` não importam `features/` nem `listeners/`;
- lógica de negócio fica na entidade ou no serviço de domínio; o handler é o roteiro e só orquestra; o controller não tem regra.

## Consequências

- **Positivas:** operação simples; transações locais; menos níveis de pasta; uma tarefa corresponde a uma pasta, o que reduz o contexto que um agente precisa carregar; o service do agregado não tem onde crescer; CQRS natural (fatias de comando passam pelo agregado, fatias de consulta usam métodos de leitura do repository); refatorar fronteiras é barato.
- **Custo aceito:** o ciclo de vida do agregado fica espalhado em N fatias; a tabela de transições ([ARCHITECTURE.md](../../ARCHITECTURE.md#54-estados-e-transições)) é o lugar que o reúne.
- **Negativas:** risco de domínio anêmico (regra escrita no handler) e de duplicação entre fatias. Mitigação: as regras "fatia não importa fatia" e "handler só orquestra" são verificadas no CI e na revisão; código usado por duas fatias sobe para a pasta do seu tipo no módulo (`entities/`, `services/`, `repositories/`, ...). Controller e handler finos são deliberados (separação de responsabilidades) e não devem ser fundidos por parecerem só "passagem". Exige disciplina: checagem automática de dependências é obrigatória. Escala é do sistema inteiro, não por módulo.
- **Quando revisitar:** um módulo precisa de escala, ciclo de deploy ou isolamento de falhas próprio de forma recorrente (a extração segue o padrão *strangler fig*); ou uma pasta por tipo de um módulo (ex.: `entities/`) cresce a ponto de pedir subpastas por agregado.
