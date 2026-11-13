# Mapa do código

> Onde fica cada coisa e como adicionar coisas novas. Aponta, não lista. Mudou uma pasta relevante: atualize no mesmo PR.

## Estrutura

<!-- se: estrutura-projeto -->
{{AGENTE: árvore real curta, até o nível da pasta que o agente imita (ex.: a pasta de um caso de uso ou de uma tela), com comentário só onde a pasta não é óbvia}}

**Fluxo de uma requisição ou tela:** {{AGENTE: os passos reais da entrada até a persistência (ou da tela até a API), um `arquivo` real por passo}}

**Um exemplo por tipo:** {{AGENTE: 1 `arquivo` real de cada tipo que o projeto tem (entrada, validação, caso de uso, entidade, acesso a dados, integração externa, tela, teste)}}
<!-- fim: estrutura-projeto -->
<!-- se: estrutura-kit -->
```
src/
├── bootstrap/                # uma entrada por processo
├── modules/<modulo>/         # um por bounded context (docs/DOMAIN.md); ex.: vendas
│   ├── features/<caso-uso>/  # fatia: Controller, Request, Command|Query, Handler, teste
│   ├── entities/             # agregado, entidades e VOs (sem sufixo)
│   ├── enums/  events/  exceptions/  services/  specifications/  policies/  dtos/
│   ├── ports/                # interfaces de fronteira externa: única interface no domínio
│   ├── repositories/         # concreto; ÚNICO lugar com ORM/SQL
│   ├── clients/              # implementa a porta; ÚNICO lugar com HTTP/SDK externo
│   ├── jobs/  listeners/
│   ├── api/                  # <Modulo>Api, DTOs, Facade: ÚNICA coisa que outro módulo importa
│   └── <modulo>.module       # registro no framework; liga Ports às implementações
├── platform/                 # configuração do framework e o que ele não oferece
└── shared/                   # só o que o framework não oferece e 2+ módulos usam
tests/  {{AGENTE: ARQUIVOS_DE_CONFIG}}
```

**Fluxo de uma requisição:** rota → `Controller` (delega) → `Request` (validação de forma) → `Handler` (orquestra; transação) → entidade (regra) → `Repository`.

- **Nome de arquivo** no estilo {{AGENTE: kebab-case.sufixo / PascalCase}} da linguagem; o nome da classe é o mesmo em qualquer stack.
- **Uma pasta por tipo**, sem gavetas genéricas (`domain/`, `infra/`): o sufixo indica a pasta. Pasta do framework para a mesma peça (`Models/`) vale; registre aqui.
- **Pasta só existe quando há arquivo.** Usado por uma fatia só fica na fatia; o resto segue a [matriz de responsabilidades](ARCHITECTURE.md#41-responsabilidades).
<!-- fim: estrutura-kit -->
<!-- se: frontend -->

**Frontend:** fica em `{{AGENTE: RAIZ_DO_FRONTEND}}`. Estrutura, nomes e receitas em [docs/FRONTEND.md](docs/FRONTEND.md).
<!-- fim: frontend -->

Onde ficam os testes: [TESTING.md](TESTING.md). Como chegar a cada funcionalidade rodando o sistema: [docs/VERIFICACAO.md](docs/VERIFICACAO.md).

## Módulos

| Módulo | Bounded context | Responsabilidade |
|---|---|---|
| `{{AGENTE: modulo}}` | {{AGENTE: contexto}} | {{AGENTE: o que faz}} |

## Onde está...

| Procuro | Caminho |
|---|---|
| Variáveis de ambiente aceitas | {{AGENTE: MECANISMO_DE_CONFIGURACAO_DO_FRAMEWORK}} (validadas na inicialização) |
| Registro de rotas, listeners, permissões e bindings | {{AGENTE: onde o framework registra}} |
<!-- se: backend -->
| Migrações e schema do banco | {{AGENTE: pasta das migrações}} |
<!-- fim: backend -->
<!-- se: frontend -->
| Rotas ou páginas do frontend | {{AGENTE: onde as telas são registradas}} |
<!-- fim: frontend -->
<!-- se: estados -->
| De onde para onde um estado pode ir | tabela de transições no enum de estado ([ARCHITECTURE.md](ARCHITECTURE.md#54-estados-e-transições)) |
<!-- fim: estados -->
<!-- se: eventos -->
| O que acontece depois de um evento | mapa evento → reações em {{AGENTE: registro do módulo}}; lista em [docs/EVENTS.md](docs/EVENTS.md) |
<!-- fim: eventos -->

## Convenção de nomes

Português do Brasil (termos do [docs/DOMAIN.md](docs/DOMAIN.md)) com sufixo técnico em inglês, sem abreviação, em tipos, arquivos, pastas, métodos, variáveis e rotas:
- **Sem artigo e sem a preposição "de":** `ItemPedido`, `listarPedidosPendentes`, arquivo `item-pedido`.
- **Papel técnico por último:** `PedidoRepository`, `VendaStatusEnum`.
- **Atributo de um conceito → dono primeiro** (id, status, tipo): `PedidoId`.
- **Coisa em si → núcleo primeiro** (item, histórico): `ItemPedido`, `HistoricoPedido`.
- **Fronteira externa: a capacidade é o núcleo:** `PagamentoPort`, instância `pagamentoPort`.
- **Preposição com sentido fica** (por, para, com, sem, entre): `listarPedidosPorStatus`.
- **Fábrica estática usa `de` para a origem:** `PedidoId.de(valor)`. Só em fábrica, nunca em tipo, arquivo ou propriedade.
- **O mesmo verbo, no mesmo número, em toda a cadeia:** rota `/pedidos/{id}/cancelar`, entrada, caso de uso, permissão `vendas.pedido.cancelar`, transição `CANCELAR`, evento `PedidoCanceladoEvent`. Uma busca pelo verbo acha tudo.

<!-- se: estrutura-projeto -->
{{AGENTE: tabela curta tipo → sufixo real usado no projeto → 1 exemplo; onde o projeto foge da convenção acima, registre a forma real e siga-a no código novo}}
<!-- fim: estrutura-projeto -->
<!-- se: estrutura-kit -->
| Tipo | Padrão | Exemplo |
|---|---|---|
| Command / Query | verbo no infinitivo + `Command`; `Listar`/`Obter`/`Buscar` + `Query` | `CriarVendaCommand`, `ListarVendasQuery` |
| Handler | nome do command/query + `Handler` | `CriarVendaHandler` |
| Controller / Request | verbo + substantivo + papel | `CriarVendaController` |
| Entidade, agregado, VO | **sem sufixo** | `Venda`, `ItemPedido` |
| Enum | substantivo + `Enum` | `VendaStatusEnum` |
| Event | substantivo + **particípio** + `Event` | `VendaCriadaEvent` |
| Exception | o que deu errado + `Exception` | `PedidoNaoEncontradoException` |
| Repository | substantivo + `Repository` (concreto, sem prefixo de tecnologia) | `PedidoRepository` |
| Port / Client / Fake | capacidade + `Port`; sistema + capacidade + `Client`; capacidade + `Fake` | `PagamentoPort`, `GatewayPagamentoClient`, `PagamentoFake` |
| Teste | classe + sufixo de teste da linguagem | `CriarVendaHandlerTest` |

Tipo novo: `<conceito><Papel>` com papel em inglês; acrescente a linha aqui.
<!-- fim: estrutura-kit -->

## Verbos com contrato de retorno

Vale para acesso a dados, consulta e API de módulo.

| Verbo | Devolve | Sem resultado |
|---|---|---|
| `obter*` | exatamente um | lança `<Conceito>NaoEncontradoException` (404) |
| `buscar*` | um ou vazio | vazio; só quando a ausência é normal no negócio |
| `existe*` | booleano | `falso` |
| `listar*` | lista (paginada quando o caso pede) | lista vazia |
| `contar*` | número | `0` |

Depois de `obter`, não teste vazio; depois de `buscar`, teste. Na dúvida, `obter`.

## Exemplos de referência

**Esta é a regra de estrutura:** o agente imita a referência do tipo de operação, não o padrão mais frequente nem um padrão de fora. Se houver duas formas no código, vale a da referência. Tipo sem referência boa fica "a escolher" e o agente pergunta. Atualize a tabela quando uma referência mudar.

| Tipo de operação | Referência |
|---|---|
| Escrita (criar ou alterar) | `{{AGENTE: caminho real}}` |
| Leitura (listar ou obter) | `{{AGENTE: caminho real}}` |
| Integração com sistema externo | `{{AGENTE: caminho real}}` |
| Chamada a outro módulo | `{{AGENTE: caminho real}}` |
<!-- se: estados -->
| Transição de estado | `{{AGENTE: caminho real}}` |
<!-- fim: estados -->
<!-- se: eventos -->
| Reação a evento | `{{AGENTE: caminho real}}` |
<!-- fim: eventos -->
<!-- se: frontend -->
| Tela com formulário | `{{AGENTE: caminho real}}` |
| Tela de listagem | `{{AGENTE: caminho real}}` |
<!-- fim: frontend -->

## Arquivos gerados: não editar à mão

| Caminho | Gerado por |
|---|---|
| {{AGENTE: ex.: src/**/generated/}} | {{AGENTE: comando}} |

## Receitas

<!-- se: estrutura-projeto -->
{{AGENTE: passos reais para adicionar um caso de uso e para integrar um sistema externo, como o código faz hoje, citando os exemplos de referência}}
<!-- fim: estrutura-projeto -->
<!-- se: estrutura-kit -->
### Adicionar um caso de uso
1. Teste primeiro: integração do handler (banco real, Ports com fake).
2. Regra nova no domínio, com teste unitário; consulta nova com nome de negócio no repository.
3. Fatia em `features/<caso-uso>/`; o framework valida, autoriza e despacha.
4. Precisa de algo de outra fatia? Mova para a pasta do tipo.
5. Registre a rota em `<modulo>.module`. Outro módulo vai chamar: receita abaixo.

### Adicionar um módulo
1. Confirme em [docs/DOMAIN.md](docs/DOMAIN.md) que é um bounded context novo.
2. Crie `src/modules/<modulo>/` com a primeira fatia, `<modulo>.module` e `api/` se outros módulos forem usá-lo; schema ou prefixo em `migrations/<modulo>/`.
3. Registre no framework; atualize a tabela de módulos e o `docs/DOMAIN.md`.

### Expor algo para outro módulo
1. Método de negócio na `<Modulo>Api`, só com DTOs públicos; a `<Modulo>Facade` só delega ao handler da fatia dona.
2. Ligue a interface à facade no registro do módulo. O consumidor injeta a interface (`vendasApi: VendasApi`), nunca a facade, o handler ou a entidade.

### Integrar um sistema externo
1. `Port` em `ports/` com tipos e erros no vocabulário do domínio.
2. `Client` em `clients/` com {{AGENTE: CLIENTE_HTTP_DO_FRAMEWORK}}, traduzindo o modelo externo; timeout e retry pelo cliente.
3. Ligue o `Port` ao client em `<modulo>.module`. O handler recebe o `Port`, nunca o client ou o SDK.
4. Fake em `tests/support/` e teste de contrato contra o fake e o client.
<!-- fim: estrutura-kit -->
<!-- se: cli -->

### Adicionar um comando de lote, CLI ou tarefa agendada
1. A regra já existe num caso de uso com teste; se não, crie-o primeiro.
2. A entrada é borda: lê argumentos, chama o caso de uso, formata a saída.
3. Agendamento num só lugar ({{AGENTE: MECANISMO_DE_AGENDAMENTO_DO_FRAMEWORK}}). Idempotente: rodar duas vezes não duplica efeito; loga o que processou.
<!-- fim: cli -->
<!-- se: estados -->

### Adicionar uma transição de estado
1. Acrescente ação → origem → destino à tabela do enum de estado.
2. Testes da matriz: a transição de cada origem válida e a recusa das demais.
3. A entidade aplica pelo método único de transição, com guardas e motivo de bloqueio; histórico na mesma transação.
4. O mesmo verbo na rota, na entrada, na permissão e no evento; as ações permitidas devolvidas incluem a nova.
<!-- fim: estados -->
<!-- se: eventos -->

### Publicar um evento novo
Siga [docs/EVENTS.md](docs/EVENTS.md#como-adicionar-um-evento).
<!-- fim: eventos -->
