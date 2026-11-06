# Mapa do código

> Onde fica cada coisa e como adicionar coisas novas. Se você criou, moveu ou removeu uma pasta relevante, atualize este arquivo no mesmo PR. Este mapa não lista itens que mudam a cada demanda (migrações, endpoints): aponta para onde estão. Uma lista assim fica desatualizada no primeiro PR que esquece dela.

## Visão geral

```
.
├── src/
│   ├── bootstrap/                 # inicialização do framework, uma entrada por processo: HTTP, worker de fila, CLI/lote, agendador
│   ├── modules/                   # um diretório por bounded context (ver docs/DOMAIN.md)
│   │   └── <modulo>/              # ex.: vendas
│   │       ├── features/          # uma pasta por caso de uso (fatia vertical)
│   │       │   ├── criar-venda/
│   │       │   │   ├── CriarVendaController                # adapta HTTP; sem repository nem regra
│   │       │   │   ├── CriarVendaRequest                   # valida o formato da entrada; sem consulta ao banco
│   │       │   │   ├── CriarVendaCommand                   # dados da intenção de escrita
│   │       │   │   ├── CriarVendaHandler                   # orquestra; sem ORM nem regra
│   │       │   │   └── CriarVendaHandlerTest               # integração, banco real
│   │       │   └── listar-vendas/
│   │       │       ├── ListarVendasController
│   │       │       ├── ListarVendasQuery
│   │       │       ├── ListarVendasHandler                 # chama um método de leitura do repository
│   │       │       └── VendaResumoResource                 # (opcional) formato da resposta
│   │       ├── entities/          # agregado, entidades e value objects
│   │       │   ├── Venda                                   # entidade/agregado com regras ({{AGENTE: ENTIDADE}})
│   │       │   ├── ItemVenda                               # entidade (sem sufixo)
│   │       │   └── Dinheiro                                # value object (sem sufixo)
│   │       ├── enums/
│   │       │   └── VendaStatusEnum
│   │       ├── events/
│   │       │   └── VendaCriadaEvent
│   │       ├── exceptions/
│   │       │   └── VendaNaoEncontradaException
│   │       ├── services/          # serviços de domínio
│   │       │   └── CalculoFreteService
│   │       ├── policies/
│   │       │   └── VendaPolicy                             # classe injetada (ou método do agregado, se só depende do estado)
│   │       ├── dtos/              # DTOs de leitura usados por repository e query (DTO público fica em api/)
│   │       ├── ports/             # interfaces de fronteira externa: única forma de interface no domínio
│   │       │   └── ConsultaCreditoPort
│   │       ├── repositories/
│   │       │   └── VendaRepository                         # concreto; ÚNICO lugar com ORM/SQL (escrita e leitura)
│   │       ├── mappers/
│   │       │   └── VendaMapper                             # registro do ORM ↔ entidade; só se a entidade for classe separada do model
│   │       ├── clients/
│   │       │   └── ErpConsultaCreditoClient                # implementa a porta; ÚNICO lugar com HTTP/SDK do ERP (ACL)
│   │       ├── jobs/
│   │       │   └── GerarNotaFiscalJob                      # delega a handler
│   │       ├── listeners/         # reações a eventos, delegando a handlers
│   │       │   ├── EnviarComprovanteListener               # evento do próprio módulo
│   │       │   └── PagamentoAprovadoSubscriber             # evento de outro módulo
│   │       ├── api/               # API pública do módulo: a ÚNICA coisa que outros módulos importam
│   │       │   ├── VendasApi                               # interface com métodos de negócio (e token de injeção)
│   │       │   ├── VendaDto                                # DTOs públicos; nunca entidades
│   │       │   └── VendasFacade                            # implementa VendasApi; só delega aos handlers
│   │       ├── index              # exporta só o registro do módulo e api/
│   │       └── <modulo>.module    # registro do módulo no framework; liga Ports às implementações
│   ├── platform/                  # configuração dos recursos do framework e o que ele não oferece (com justificativa)
│   └── shared/                    # só o que o framework não oferece e mais de um módulo usa; crie quando precisar
├── tests/
│   ├── unit/                      # só se a linguagem preferir testes separados (ver abaixo)
│   ├── integration/               # repositories, clients, listeners com banco e fila reais
│   ├── acceptance/                # cenários BDD (.feature) + step definitions
│   └── support/                   # fakes de Port e fixtures; dados de teste pelas factories do ORM/biblioteca
├── migrations/                    # migrações de banco, uma pasta por módulo (ou o local que o framework usa)
├── docs/                          # documentação de design
├── scripts/                       # automações de desenvolvimento e CI; verificação que falha imprime o quê · por quê · faça isto · seção (ARCHITECTURE.md §9)
└── {{AGENTE: ARQUIVOS_DE_CONFIG}}         # ex.: manifesto de pacotes, config de lint, docker-compose
```

A árvore mostra os nomes das classes. Os nomes de arquivo seguem o estilo {{AGENTE: kebab-case.sufixo / PascalCase}} da linguagem: por exemplo, `criar-venda.handler` (kebab-case com sufixo após ponto) ou `CriarVendaHandler` (PascalCase). O nome da classe é o mesmo em qualquer stack.

Testes ficam **junto do código** sempre que a linguagem permitir: o unitário do domínio junto do arquivo testado (`entities/venda.test`) e o teste de integração do handler, com banco real, na fatia (`features/criar-venda/criar-venda.handler.int.test`, com um sufixo que separa integração de unitário). Se a linguagem ou a ferramenta de testes preferir uma árvore separada (ex.: PHP com Pest e PSR-4), use `tests/unit/<modulo>/` (espelhando `entities/`, `enums/`, ...) e `tests/integration/<modulo>/features/`. Outros testes de integração, aceitação e suporte ficam em `tests/`. Detalhes em [TESTING.md](TESTING.md).

**Uma pasta por tipo de arquivo** dentro do módulo, sem gavetas genéricas (`domain/`, `infra/`): a localização se deduz pelo sufixo do nome (`*Exception` → `exceptions/`, `*Repository` → `repositories/`), cada pasta tem menos arquivos e a forma é a mesma em todas as stacks. Os nomes acima, em minúsculas, são o padrão deste kit; cada stack adapta a capitalização ao idioma de {{AGENTE: FRAMEWORK}} (ex.: `Enums/`, `Events/`, `Policies/`, `Jobs/` em PascalCase) e, se o framework tem pasta convencional para uma peça (ex.: `Models/` quando o model do ORM é a entidade), usa a dele e registra aqui a correspondência. `features/` continua sendo a pasta das fatias. "Domínio" continua sendo o conceito: as pastas de domínio são `entities/`, `enums/`, `events/`, `exceptions/`, `services/`, `specifications/`, `policies/`, `dtos/` e `ports/`. Quem faz o quê está na [matriz de responsabilidades](ARCHITECTURE.md#41-responsabilidades).

**Pasta só existe quando há arquivo para ela.** Módulo pequeno pode ter só `features/`, `entities/` e `repositories/`; as demais nascem com o primeiro arquivo.

## Frontend

Fica em `{{AGENTE: RAIZ_DO_FRONTEND}}` e espelha os módulos e as fatias do backend, com os mesmos nomes. Detalhes, convenção de nomes e receitas em [docs/FRONTEND.md](docs/FRONTEND.md).

```
{{AGENTE: RAIZ_DO_FRONTEND}}/
├── app/                           # rotas, providers, layout raiz
├── modules/
│   └── <modulo>/                  # mesmo nome do módulo do backend
│       ├── features/<caso-uso>/ # criar-venda-form, use-criar-venda, criar-venda.schema
│       ├── components/            # usados por 2+ fatias do módulo
│       ├── pages/                 # compõem fatias; sem lógica
│       ├── api/                   # <modulo>.api: chamadas HTTP do módulo
│       ├── model/                 # <entidade>.types, <nome>.enum
│       └── index                  # API pública do módulo
└── shared/
    ├── ui/                        # design system
    ├── api/generated/             # tipos gerados do contrato da API: não editar
    ├── hooks/
    └── lib/
tests/e2e/<modulo>/                # cenários de ponta a ponta ({{AGENTE: FERRAMENTA_E2E}})
```

## Módulos

| Módulo | Bounded context | Responsabilidade | Publica eventos | Consome eventos |
|---|---|---|---|---|
| `{{AGENTE: modulo-a}}` | {{AGENTE: Contexto A}} | {{AGENTE: o que faz}} | {{AGENTE: EventoX}} | {{AGENTE: EventoY}} |
| `{{AGENTE: modulo-b}}` | {{AGENTE: Contexto B}} | {{AGENTE: o que faz}} | | |

## Onde está...

| Procuro | Caminho |
|---|---|
| Regras de negócio de X | `src/modules/<modulo>/entities/` (entidade/agregado, VO), `enums/`, `services/` (serviço de domínio), `specifications/` (conceito usado em memória e em consulta) |
| O que acontece quando o usuário faz Y | `src/modules/<modulo>/features/<caso-uso>/`: controller → command → handler |
| Como uma tela ou endpoint lê dados | `features/<listar-ou-obter-algo>/`: query → handler → método de leitura do repository → resource |
| O que acontece depois de um evento | `src/modules/<modulo>/listeners/` |
| Integração com sistema externo Z | interface `Port` em `src/modules/<modulo>/ports/`; `Client` em `src/modules/<modulo>/clients/` |
| Persistência e consultas de um agregado | `Repository` concreto em `src/modules/<modulo>/repositories/` (único lugar com ORM/SQL) |
| O que um módulo oferece aos outros | `src/modules/<modulo>/api/` (interface `<Modulo>Api`) |
| Variáveis de ambiente aceitas | {{AGENTE: MECANISMO_DE_CONFIGURACAO_DO_FRAMEWORK}} (validadas na inicialização) |
| Registro de rotas, listeners, policies e bindings de `Port` | `src/modules/<modulo>/<modulo>.module`; o resto é resolvido pelo container do framework |
| De onde para onde X pode ir | tabela de transições no enum de estado em `enums/` ([ARCHITECTURE.md](ARCHITECTURE.md#54-estados-e-transições)) |
| O que acontece depois de X | mapa evento → reações no registro do módulo (`<modulo>.module`) |
| Lista de eventos | [docs/EVENTS.md](docs/EVENTS.md) |

## Convenção de nomes

Nomes em português do Brasil (linguagem ubíqua do [docs/DOMAIN.md](docs/DOMAIN.md)) com sufixo técnico em inglês, sem abreviações. Regras de composição, que valem para tipos, arquivos, pastas, métodos, propriedades, variáveis, parâmetros, constantes e rotas nomeadas:
- **Sem artigo e sem a preposição "de"** (de, do, da, dos, das): juntam-se os substantivos. `ItemPedido`, `AnaliseCreditoService`, `LimiteCreditoExcedidoException`, `limiteCredito`, arquivo `item-pedido`, pasta `features/listar-pedidos-pendentes/`.
- **Papel técnico sempre por último** (sufixo): `PedidoRepository`, `PedidoPolicy`, `PedidoDto`, `VendaStatusEnum`.
- **Atributo ou aspecto de um conceito → conceito dono primeiro.** Quando o tipo representa uma característica de outro conceito (id, status, categoria, tipo, transição, nome, detalhe, resumo): `PedidoId`, `VendaStatusEnum`, `PedidoTransicaoEnum`, `AgregadoNome`, `VendaDetalhePage`; arquivos `pedido-id`, `venda-status.enum`.
- **Uma coisa em si → núcleo primeiro, dono depois.** Quando o tipo é um conceito próprio que pertence a outro (item, histórico, anexo, análise, cálculo, consulta, caixa de entrada, filtro): `ItemVenda`, `HistoricoPedido`, `AnaliseCreditoService`, `ConsultaCreditoPort`, `FiltroVendasBar`. Se ficar ambíguo, use o conceito do negócio.
- **Porta: a capacidade é o núcleo:** `ConsultaCreditoPort`, `NotificadorClientePort`; instância `consultaCreditoPort`.
- **Preposições com sentido continuam** (por, para, com, sem, entre) quando dizem algo que a junção perderia: `listarPendentesPorCliente`, `PedidoElegivelParaDescontoSpecification`, `PeriodoEntre`.
- **Fábrica estática usa `de` para dizer a origem**: `PedidoId.de(valor)`, `Dinheiro.deCentavos(1500)` criam o valor a partir de outra representação. Aqui o "de" diz de onde o valor vem, não liga dois substantivos; sem ele, `Dinheiro.centavos(1500)` pareceria um getter. Vale só para fábricas, nunca para tipo, arquivo, pasta ou propriedade.
- Prosa, descrições de teste, mensagens ao usuário e o glossário continuam em português normal ("item do pedido"); a coluna "nome no código" do glossário mostra a forma sem preposição.

Por quê: o nome fica mais curto sem perder clareza; os aspectos de um conceito ficam juntos na ordenação e no autocompletar (`Pedido…`), e cada coisa própria é achada pelo seu núcleo (`Historico…`); e é o que as aplicações de referência fazem. **O mesmo nome de negócio, com o mesmo número gramatical, se repete em toda a cadeia do caso de uso:** rota (`/pedidos/{id}/cancelar`), Request, Command, Handler, permissão, transição (`CANCELAR`) e evento (`PedidoCanceladoEvent`). Uma busca textual pelo verbo acha tudo.

| Tipo | Padrão | Exemplo | Onde |
|---|---|---|---|
| Controller | verbo + substantivo + `Controller` | `CriarVendaController` | fatia |
| Request | verbo + substantivo + `Request` | `CriarVendaRequest` | fatia |
| Resource | substantivo + `Resource` | `VendaResumoResource` | fatia |
| Command | **verbo no infinitivo** + `Command` | `CriarVendaCommand` | fatia |
| Query | `Listar`/`Obter`/`Buscar` + `Query` | `ListarVendasQuery` | fatia |
| Handler | nome do command/query + `Handler` | `CriarVendaHandler` | fatia |
| Ação invocável (variante) | verbo do caso de uso, para projetos que já usam ações invocáveis; a instância leva o verbo (`criar: Criar`) e o nome continua único na cadeia | `Criar` | fatia |
| DTO | substantivo + `Dto` | `VendaDto` | `api/` (público), `dtos/` (leitura usada por repository e query) ou fatia |
| API do módulo | módulo + `Api` (interface) | `VendasApi` | `api/` |
| Facade | módulo + `Facade` (implementa a `Api`, só delega) | `VendasFacade` | `api/` |
| Dependência injetada | nome do tipo em camelCase; por interface, nome da interface | `vendaRepository`, `consultaCreditoPort`, `estoqueApi` | construtor |
| Entity / aggregate / VO | **sem sufixo** (linguagem ubíqua) | `Venda`, `Dinheiro` | `entities/` |
| Enum | substantivo + `Enum` | `VendaStatusEnum` | `enums/` |
| Event | **substantivo + particípio** + `Event` | `VendaCriadaEvent` | `events/` |
| Exception | o que deu errado + `Exception` | `VendaNaoEncontradaException` | `exceptions/` |
| Domain service | capacidade + `Service` | `CalculoFreteService` | `services/` |
| Specification | condição + `Specification` | `VendaElegivelParaDescontoSpecification` | `specifications/` |
| Policy | substantivo + `Policy`, no mecanismo de autorização do framework | `VendaPolicy` | `policies/` (ou pasta do framework) |
| Permissão | módulo + agregado + verbo do caso de uso | `vendas.pedido.cancelar` | registro de permissões do módulo |
| Transição | verbo do caso de uso, como ação na tabela de transições | `CANCELAR` | enum de estado |
| Port (interface externa) | capacidade + `Port` | `ConsultaCreditoPort` | `ports/` |
| Repository | substantivo + `Repository` (classe concreta, sem prefixo de tecnologia); `QueryRepository` se as leituras crescerem | `VendaRepository`, `VendaQueryRepository` | `repositories/` |
| Mapper | substantivo + `Mapper` (só se a entidade for classe separada do model do ORM) | `VendaMapper` | `mappers/` |
| Client | sistema + capacidade + `Client` | `ErpConsultaCreditoClient` | `clients/` |
| Job | ação + `Job` | `GerarNotaFiscalJob` | `jobs/` |
| Listener | ação executada + `Listener` | `EnviarComprovanteListener` | `listeners/` |
| Subscriber | evento de outro módulo + `Subscriber` | `PagamentoAprovadoSubscriber` | `listeners/` |
| Notification | fato + `Notification` | `VendaConfirmadaNotification` | `notifications/` |
| Console command | ação + `ConsoleCommand` | `ReprocessarVendasConsoleCommand` | `console/` |
| Teste | classe + sufixo de teste da linguagem | `CriarVendaHandlerTest`, `criar-venda.handler.test` | junto do arquivo testado (fatia, `entities/`, ...) ou `tests/` |
| Fake de Port | conceito da porta + `Fake` | `ConsultaCreditoFake` | `tests/support/` |
| Factory de teste | conforme o ORM ou a biblioteca de testes | {{AGENTE: ex.: factory do model Venda}} | local que o framework usa |

**Onde colocar:** siga a [matriz de responsabilidades](ARCHITECTURE.md#41-responsabilidades). Usado por uma fatia só → na fatia; regra de negócio → `entities/`, `enums/` ou `services/`; `Port` → `ports/`; ORM/SQL → repository em `repositories/`; HTTP/SDK externo → client em `clients/`; reação a evento → `listeners/`; em geral, o sufixo do nome indica a pasta; exigido pelo framework no nível do módulo → raiz do módulo.

### Verbos com contrato de retorno

O verbo do método diz o que ele devolve e o que acontece quando não há resultado. Vale para repository, query handler e `<Modulo>Api`:

| Verbo | Devolve | Sem resultado |
|---|---|---|
| `obter*` | exatamente um | lança `<Conceito>NaoEncontradoException` (categoria "não encontrado", 404) |
| `buscar*` | um ou vazio | devolve vazio; só quando a ausência é resultado normal do negócio |
| `existe*` | booleano | `falso` |
| `listar*` | lista (paginada quando o caso de uso pede) | lista vazia |
| `contar*` | número | `0` |

Por quê: com o contrato no verbo, quem chama não testa vazio depois de `obter` (o `se não existe, lança` repetido em cada handler é uma segunda definição do desfecho) e não esquece de testar depois de `buscar`. Na dúvida entre os dois, `obter`: a ausência costuma ser erro.

```
pedido = this.pedidoRepository.obter(command.pedidoId)       // não encontrado → PedidoNaoEncontradoException → 404
cupom = this.cupomRepository.buscarPorCodigo(command.codigo) // vazio é normal: pedido sem cupom
```

## Exemplos de referência

Uma fatia nomeada por tipo de operação. Código novo imita a referência do seu tipo, não o padrão mais frequente; se houver duas formas no código, vale a da referência. Mantenha estas fatias exemplares e atualize a tabela quando uma delas mudar.

| Tipo de operação | Fatia de referência |
|---|---|
| Escrita (criar ou alterar) | `{{AGENTE: src/modules/vendas/features/criar-venda/}}` |
| Leitura (listar ou obter) | `{{AGENTE: src/modules/vendas/features/listar-vendas/}}` |
| Transição de estado | `{{AGENTE: src/modules/vendas/features/cancelar-venda/}}` |
| Integração com sistema externo | `{{AGENTE: src/modules/vendas/clients/ErpConsultaCreditoClient}}` |
| Reação a evento | `{{AGENTE: src/modules/vendas/listeners/EnviarComprovanteListener}}` |
| API pública do módulo | `{{AGENTE: src/modules/vendas/api/VendasFacade}}` |

## Arquivos gerados: não editar à mão

| Caminho | Gerado por |
|---|---|
| {{AGENTE: ex.: src/**/generated/}} | {{AGENTE: comando}} |

## Receitas

### Adicionar um caso de uso
1. Escreva o teste de aceitação ou o teste de integração do handler (banco real, Ports com fake) descrevendo o comportamento.
2. Se houver regra nova, implemente-a na entidade ou no VO (`entities/`), no enum (`enums/`) ou em um serviço de domínio (`services/`), com teste unitário.
3. Se precisar de consulta ou persistência nova, adicione um método com nome de negócio no repository do agregado.
4. Crie a pasta da fatia em `features/<caso-uso>/` (ex.: `features/cancelar-venda/`) com `Controller`, `Request`, `Command` (ou `Query`) e `Handler`, usando os recursos do framework para validação, autorização e despacho. O controller não recebe repository; o handler usa repository e domínio e só orquestra.
5. Se precisar de algo de outra fatia, mova esse código para a pasta do tipo dele no módulo (`entities/`, `services/`, `repositories/`, ...) em vez de importar a outra fatia.
6. Registre a rota (e o handler, se o barramento do framework exigir) em `<modulo>.module`.
7. Se outro módulo precisa chamar, siga a receita [Expor algo para outro módulo](#expor-algo-para-outro-módulo).

### Adicionar um comando de lote, CLI ou tarefa agendada
1. A regra já existe num handler (com teste); se não, crie a fatia primeiro.
2. Crie o ponto de entrada como borda: lê argumentos, monta o command, chama o handler e entrega o resultado a um formatter com teste (CSV, texto); sem regra, sem ORM e sem formatação em funções soltas ([matriz](ARCHITECTURE.md#41-responsabilidades)).
3. A entrada sobe só o que precisa (`src/bootstrap/<entrada>`), sem consumidores de fila nem a aplicação HTTP.
4. Agendamento declarado num só lugar ({{AGENTE: MECANISMO_DE_AGENDAMENTO_DO_FRAMEWORK}}).
5. Idempotente: rodar duas vezes não duplica efeito; registra no log o que processou.

### Adicionar um módulo
1. Confirme em [docs/DOMAIN.md](docs/DOMAIN.md) que é um bounded context novo e não parte de um existente.
2. Crie `src/modules/<modulo>/` com a primeira fatia em `features/`, `entities/`, `repositories/`, `api/` (se outros módulos forem usá-lo), `index` e `<modulo>.module`. As demais pastas por tipo (`enums/`, `events/`, `clients/`, `listeners/`, ...) nascem com o primeiro arquivo.
3. Crie o schema/prefixo de banco em `migrations/<modulo>/`.
4. Registre o módulo no framework, como a documentação dele mostra.
5. Atualize a tabela de módulos acima e o mapa de contextos em `docs/DOMAIN.md`.

### Expor algo para outro módulo
1. Confirme que o caso de uso existe como fatia no módulo dono (handler com teste).
2. Acrescente o método de negócio à interface `<Modulo>Api` em `api/`, recebendo e devolvendo só DTOs públicos.
3. Implemente-o na `<Modulo>Facade`, que só delega ao handler (direto ou pelo barramento do framework); sem regra, sem ORM.
4. Ligue a interface à facade no registro do módulo (é um dos poucos bindings).
5. No módulo consumidor, injete a interface pelo nome dela (`vendasApi: VendasApi`); nunca a facade, handlers ou entidades do outro módulo.

### Integrar um sistema externo
1. Defina a interface `Port` em `ports/` com tipos do seu domínio (ex.: `ConsultaCreditoPort`) e documente nela os erros possíveis, já no vocabulário do domínio (ex.: `ClienteErpNaoEncontradoException`).
2. Implemente o `Client` em `clients/` (ex.: `ErpConsultaCreditoClient`) com {{AGENTE: CLIENTE_HTTP_DO_FRAMEWORK}}, traduzindo o modelo externo (anticorruption layer).
3. Configure timeout e retry pelos recursos do cliente HTTP; circuit breaker só por biblioteca documentada, se necessário.
4. Ligue o `Port` ao client em `<modulo>.module` (é um dos poucos bindings do módulo).
5. Crie o fake da porta em `tests/support/` (ex.: `ConsultaCreditoFake`), usado nos testes de integração dos handlers, e um teste de contrato que roda contra o fake e o client.
6. O handler recebe o `Port`, nunca o client nem o SDK.

### Adicionar uma transição de estado
1. Acrescente a transição (ação → origem → destino) à tabela do enum de estado; se for preciso, um estado novo no conjunto fechado.
2. Escreva os testes da matriz: a transição a partir de cada origem válida e a recusa (exceção de "estado não permite") a partir das demais.
3. A entidade aplica a transição pelo método único de transição, com as guardas e o motivo de bloqueio; o histórico é gravado na mesma transação.
4. Crie a fatia da transição em `features/<verbo>-<agregado>/`, com o mesmo verbo na rota, no command, no handler, na permissão e no evento.
5. Confira que as ações permitidas devolvidas pela API passam a incluir a nova ação.

### Publicar um evento novo
1. Crie o evento em `events/` com sufixo `Event` (ex.: `VendaCanceladaEvent`) no formato do mecanismo de eventos do framework e registre-o no agregado.
2. Siga o restante do passo a passo em [docs/EVENTS.md](docs/EVENTS.md#como-adicionar-um-evento).
