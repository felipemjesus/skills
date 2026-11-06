# Diretrizes de código

> Como escrevemos código aqui. Cada regra tem um motivo; quando o motivo não se aplica, use bom senso e explique a exceção no PR. Ferramentas automáticas (lint, formatador, checagem de arquitetura) cobrem o que é mecânico. Este documento cobre o que exige julgamento.

## 1. Princípios

### Framework first
Antes de criar abstração, utilitário, wrapper, camada ou infraestrutura, procure o recurso na documentação oficial de {{AGENTE: FRAMEWORK}} e das bibliotecas adotadas e use-o como a documentação mostra ([ADR-0005](docs/adr/0005-framework-first.md)). Solução própria só quando o framework não oferece, com justificativa no PR ou em ADR. A aplicação deve parecer um projeto típico do framework para quem conhece a documentação oficial.

Exemplos do que **não** criar quando o framework oferece: relógio ou gerador de ID próprios (use os da linguagem, do framework ou do ORM e os helpers de tempo da ferramenta de testes); tipo `Result` próprio (use exceções de domínio e o tratamento global de erros do framework, a menos que `Result` seja o idioma da linguagem); publicador de eventos ou outbox próprios (use eventos e filas do framework, [ADR-0003](docs/adr/0003-eventos-com-recursos-do-framework.md)); interfaces de autorização ou de flags (use {{AGENTE: MECANISMO_DE_AUTORIZACAO_DO_FRAMEWORK}} e {{AGENTE: MECANISMO_DE_FEATURE_FLAGS}} direto); builders de teste quando o ORM ou a biblioteca de testes têm factories; wrappers de cliente HTTP.

### Versões e sintaxe atual

Usamos a versão estável mais recente de frameworks e bibliotecas ([ADR-0005](docs/adr/0005-framework-first.md)); a versão em uso está no lockfile, não nos documentos.

- Código novo usa a forma **recomendada pela documentação da versão instalada**. O critério não é "a sintaxe mais nova que existe", é o que a documentação recomenda ou marca como obsoleto.
- Nada de API marcada como obsoleta (*deprecated*).
- Código antigo é migrado quando for tocado pela demanda ou num PR de refatoração próprio, sem misturar com funcionalidade.
- Antes de escrever, confira a versão no lockfile e consulte a documentação **dessa** versão. Não confie na memória: agentes tendem a escrever a sintaxe do treinamento.

| Forma antiga ainda compatível | Forma atual preferida |
|---|---|
| {{AGENTE: EXEMPLOS_DA_STACK}} | |
| *(ilustrativo, JavaScript)* `JSON.parse(JSON.stringify(x))` para cópia profunda | `structuredClone(x)` |
| *(ilustrativo, PHP)* `switch` que só devolve um valor | expressão `match` |

Cada linha da tabela do projeto é confirmada na documentação oficial antes de entrar.

**Verificação automática:** `{{AGENTE: FERRAMENTA_DE_MODERNIZACAO}}` (ex.: Rector no PHP, codemods oficiais do framework) roda em modo de simulação no `{{AGENTE: CMD_CHECK}}` e falha se houver reescrita pendente; `{{AGENTE: REGRA_DE_API_OBSOLETA}}` (regra de lint ou de análise estática que aponta uso de API obsoleta) também faz parte do `{{AGENTE: CMD_CHECK}}`.

### Separação de responsabilidades
Framework first define **qual** recurso usar; a [matriz de responsabilidades](ARCHITECTURE.md#41-responsabilidades) define **onde**. Cada artefato tem um único motivo para mudar. Em resumo: ORM e SQL só no repository (inclusive leituras); controller e request nunca recebem repository nem consultam o banco; handler orquestra sem ORM e sem regra de negócio; regra de negócio só em entidade, agregado, VO, enum e serviço de domínio; listeners e jobs delegam a handlers; HTTP e SDK de sistema externo só no `Client`.

Sinais de violação para a revisão: os da [matriz](ARCHITECTURE.md#41-responsabilidades) (uma fonte só; não repetidos aqui).

### Orientação a objetos

Todo código de aplicação e de domínio fica em classes. Assim cada regra tem um dono com nome, as dependências aparecem no construtor e o leitor acha o comportamento perguntando ao objeto, não procurando funções soltas pelo projeto.

**Funções de topo só na borda do framework**, numa lista fechada:
- ponto de entrada e inicialização (`main`, bootstrap);
- arquivos de configuração de ferramentas (lint, testes, build);
- arquivos de rotas, quando o framework os declara como funções;
- fábricas de dados de teste;
- APIs de biblioteca que exigem função ou objeto literal (ex.: callback de configuração, definição de tool de um SDK de IA, componente ou hook do framework de UI).

Fora dessa lista, o que seria função utilitária vira:
- um **value object** com o comportamento (`Dinheiro`, `Cpf`, `PeriodoVigencia`);
- um **método do agregado**, quando a regra é sobre o próprio estado;
- um **serviço de domínio instanciável e injetado**, quando a regra envolve vários agregados ou é um cálculo com nome (`CalculoFreteService`);
- uma **fábrica estática** só para criar e reconstituir (`Pedido.criar(...)`, `Pedido.reconstituir(...)`).

**Policy:** método do agregado quando a regra depende só do estado dele (`pedido.podeSerCancelado()`); classe instanciável e injetada nos demais casos (ex.: depende do usuário e do agregado: `PedidoPolicy`). **Mapper:** classe instanciável e injetada, usada só pelo repository. Nada de classe só com métodos estáticos nem objeto literal usado como namespace.

Verificação: `{{AGENTE: VERIFICACAO_DE_FUNCOES_DE_TOPO}}` no `{{AGENTE: CMD_CHECK}}` (regra de lint ou de arquitetura, ou busca no CI) acusa função de topo fora das pastas da borda. Os exemplos deste kit seguem essa regra; se um exemplo e uma regra de lint do projeto se contradizem, a convenção documentada é a referência e a contradição é levada a quem decide ([AGENTS.md](AGENTS.md#perguntar-antes)).

### Verificações, exemplos e API do framework

- **Os exemplos dos documentos passam nas verificações do próprio projeto** (lint, tipos, arquitetura). Um exemplo que a verificação recusa é defeito do documento, como um comentário falso: corrija o exemplo para a forma aceita, e não a convenção nem a configuração. Se não estiver claro qual dos dois está certo, aponte a contradição e pergunte. Por quê: o agente copia o exemplo; se o exemplo não passa, ele aprende a contornar a regra.
- **A API do framework vence a regra de estilo.** Nome ou chave exigido por uma biblioteca (ex.: chaves de agregação do ORM com prefixo `_`, nome de método que o framework chama por convenção) é permitido onde a [matriz](ARCHITECTURE.md#41-responsabilidades) permite aquela API: chave do ORM, no repository. Se uma regra de lint recusa a chave, a exceção é declarada na configuração do lint com escopo restrito, depois de perguntar ([AGENTS.md](AGENTS.md#perguntar-antes)). Nunca se troca de API para escapar da regra.
- **O kit não afirma sobre a configuração o que ela não faz, e nunca manda mudá-la sem trazer a mudança.** Se um documento diz que uma regra está desligada ou que uma exceção existe, a configuração de exemplo da stack mostra isso; onde o kit precisa de uma exceção (ex.: chaves do ORM), ela já vem declarada na configuração de exemplo. Mexer além do que o kit traz continua em [Perguntar antes](AGENTS.md#perguntar-antes). Por quê: uma instrução que contradiz o "perguntar antes" vira autorização para o atalho que o agente tinha recusado.
- **Trocar a API recomendada por SQL cru (ou outra forma menos segura) para escapar de uma regra é contornar a regra:** pergunte ([AGENTS.md](AGENTS.md#nunca)). SQL cru no repository continua permitido quando a API do ORM não expressa a consulta, com o motivo num comentário.

### Simplicidade primeiro
- **KISS.** A solução mais simples que resolve o problema atual. Código esperto é código difícil de revisar.
- **YAGNI.** Não construa para requisitos hipotéticos. Abstração nova precisa de pelo menos dois usos reais ou de uma fronteira arquitetural (porta). Ex.: notificação pedida sem canal definido começa com o `NotificadorPort` implementado por um client que registra em log; servidor de e-mail entra quando for pedido.
- **DRY com moderação.** Duplicação de *conhecimento* (uma regra de negócio em dois lugares) é bug esperando acontecer. Duplicação de *código* parecido por coincidência é aceitável. Regra de três: abstraia na terceira repetição, não na segunda; para um passo repetido em handlers, o que fazer na terceira vez está em [Passo comum a vários casos de uso](#passo-comum-a-vários-casos-de-uso).
- **Um conceito de negócio, uma definição.** Cada conceito com regra ("item disponível", "cliente bloqueado", "pedido em atraso") tem uma única definição com nome: predicado do agregado, método de VO ou de serviço de domínio, ou método de leitura do repository com o nome do conceito (`listarClientesBloqueados`) quando a definição é uma consulta. Handlers, consultas, listeners e jobs reutilizam essa definição. Antes de escrever uma condição de negócio, busque o conceito pelo nome e pelo nome da regra em [docs/DOMAIN.md](docs/DOMAIN.md); se existe, use; se precisa mudar, mude no único lugar. Um teste trava a definição (casos de borda do conceito). Por quê: com duas definições, quem muda uma não sabe da outra, e o mesmo registro aparece "disponível" numa tela e indisponível na outra. Exemplo com dois gates, consulta e agregado em [Um conceito, uma definição: como reutilizar](#um-conceito-uma-definição-como-reutilizar).
- **Uma implementação viva por conceito.** Um conceito tem um modelo e um caso de uso tem uma implementação. A versão nova substitui a antiga no mesmo ciclo, ou a antiga entra como dívida com prazo em [ARCHITECTURE.md](ARCHITECTURE.md#11-riscos-e-débitos-conhecidos). Nada de árvore `New` ao lado da antiga nem sufixo `_NEW`: com duas versões vivas, a primeira pergunta passa a ser "qual delas roda?".
- **Uma forma por tipo de operação.** Toda escrita, leitura, transição e integração tem a mesma forma, aprendida uma vez; código novo segue o [exemplo de referência](CODEBASE_MAP.md#exemplos-de-referência), não o padrão mais frequente.
- **Camada ou padrão só quando o problema aparece.** Cada camada a mais é um salto de leitura e, chegando antes do problema, convive com a versão anterior.

### SOLID, na prática

| Princípio | Regra concreta neste projeto |
|---|---|
| **S**: responsabilidade única | Cada artefato tem a responsabilidade da [matriz](ARCHITECTURE.md#41-responsabilidades). Um caso de uso por fatia (`features/<caso-uso>/`), um handler por caso de uso. Uma classe muda por um único motivo. |
| **O**: aberto/fechado | Variação de comportamento por estratégia injetada (ex.: gateways de pagamento, regras de preço), não por `if/switch` crescente. Variação só de dados é uma tabela declarativa. |
| **L**: substituição de Liskov | Todo client de um `Port` passa na mesma suíte de testes de contrato. O fake também. |
| **I**: segregação de interfaces | Portas pequenas e com nome de negócio. Melhor `NotificadorClientePort` e `AgendadorEntregaPort` que um `IntegrationService` com 15 métodos. |
| **D**: inversão de dependência | Aplicada nas **fronteiras externas**, não em toda dependência: handlers dependem de `Port` (interface em `ports/`) para sistemas externos e LLM; repositories, recursos do framework e classes internas são concretos ([Interfaces só quando há motivo](#interfaces-só-quando-há-motivo)). Tudo é injetado pelo container do framework; nada de `new` de dependência dentro de handler. |

### Outros princípios
- **Lei de Demeter.** Fale com seus vizinhos imediatos: `pedido.total()` em vez de `pedido.itens.map(...).reduce(...)` fora do agregado.
- **Tell, don't ask.** Peça ao objeto para fazer (`conta.debitar(valor)`), não pergunte o estado para decidir por ele.
- **Composição sobre herança.** Herança só para relações "é um" estáveis; um nível, no máximo dois.
- **CQS.** Um método ou altera estado ou retorna dado, não os dois.
- **Fail fast nas pré-condições; acumular nas regras independentes.** Pré-condições (existe, tem permissão, o estado permite) falham cedo, com erro claro. Regras independentes sobre os dados são avaliadas todas e devolvidas juntas: o usuário não corrige uma e descobre a próxima. Nunca continue com estado inválido.
- **Menor espanto.** Um nome deve dizer o que a coisa faz e o que devolve. `getX` não grava nada; `validar` não persiste; `obter`, `buscar`, `existe`, `listar` e `contar` têm contrato de retorno fixo ([CODEBASE_MAP.md](CODEBASE_MAP.md#verbos-com-contrato-de-retorno)). Sem verbos genéricos (`tratar`, `processar`, `fazer`) e sem sufixo técnico que colida com termo do domínio. Um termo tem um significado só.

## 2. Modelagem e tipos

- **Linguagem ubíqua.** Nomes vêm de [docs/DOMAIN.md](docs/DOMAIN.md). Se o negócio diz "matrícula", o código não diz "registration" nem "inscricao".
- **Value objects contra obsessão por primitivos.** `Email`, `Dinheiro`, `Cpf`, `PedidoId` em vez de `string`/`number`. A validação fica no construtor; um VO existente é sempre válido.
- **A regra que tem VO fica só no VO.** O request valida a **forma** (presença, tipo, tamanho, formato estrutural); o que o VO valida (dígito verificador do `Cnpj`, formato do `Email`) não se repete no request. Quando o VO rejeita, lança a exceção de entrada inválida com o `campo`, e o tratamento global de erros devolve 400 como faz com o request. Por quê: com a regra nos dois lugares, o VO fica inalcançável pelo HTTP (o request recusa antes), o teste do VO não prova o comportamento da API e as duas versões divergem na primeira mudança.

  ```
  // features/cadastrar-cliente/cadastrar-cliente.request: só forma
  cnpj: texto obrigatório, até 18 caracteres
  email: texto obrigatório, até 254 caracteres

  // entities/cnpj (VO): a regra, num lugar só
  Cnpj(valor):
    se não this.digitosValidos(valor): lançar EntradaInvalidaException(campo: "cnpj", "o CNPJ 12.345.678/0001-00 tem dígito verificador inválido")
  ```

  **Erros de entrada de vários VOs (decisão do kit).** Os erros de forma voltam juntos: o validador do framework, no request, junta todos em `errors`. Os VOs são criados depois, no controller ou no handler, e **podem** falhar um por vez (400 com o `campo` do primeiro), porque com a forma já validada a regra do VO raramente falha. Se a demanda pedir todos juntos, crie os VOs coletando as `EntradaInvalidaException` e lance uma só, com a lista, que o tratamento global devolve como 400 com `errors[]`; na forma curta abaixo, sem utilitário genérico novo no kernel (salvo se ele já existir). Por quê: a decisão escrita evita que cada fatia invente seu acumulador.

  ```
  // só quando a demanda pede todos os erros de VO numa resposta
  erros = []
  cnpj = tentar Cnpj(request.cnpj), se EntradaInvalidaException: erros.adicionar(excecao)
  email = tentar Email(request.email), se EntradaInvalidaException: erros.adicionar(excecao)
  se erros não vazia: lançar EntradaInvalidaException(erros)   // 400, um item de errors por campo
  ```
- **Estados ilegais irrepresentáveis.** Prefira tipos que impeçam combinações inválidas (uniões discriminadas, enums, máquinas de estado) a flags booleanas soltas. O ciclo de vida é uma tabela de transições declarada, a única porta de mudança de estado ([ARCHITECTURE.md](ARCHITECTURE.md#54-estados-e-transições)); conjuntos de estados com significado de negócio têm nome (`STATUS_QUE_PERMITEM_EDICAO`).
- **Regra como predicado com nome do negócio**, no objeto que tem os dados: `pedido.podeSerCancelado()`, não `if (pedido.status == 3 && pedido.itens.length > 0)` no handler. O handler vira uma lista de condições legíveis como frases.
- **Nenhum literal mágico.** Limiares, estados, permissões e tipos aparecem pelo nome; se a constante existe, o literal não aparece.
- **Imutabilidade por padrão.** VOs, DTOs, commands, queries e eventos são imutáveis. Agregados mudam só por métodos que garantem invariantes.
- **Entidade com comportamento, sem persistência.** {{AGENTE: ENTIDADE: model do ORM (active record) ou classe de domínio separada — seguir o idioma do framework}}. Em qualquer caso, a entidade guarda regras, invariantes, transições e eventos; chamadas de consulta e persistência ficam no repository. Com active record, o model mantém também a configuração declarativa do ORM (tipos, relações, escopos), mas escopos são chamados só pelo repository.
- **Agregados pequenos.** Um agregado protege um conjunto de invariantes. Referencie outros agregados por ID. A transação é do caso de uso, não do agregado: pode incluir outros registros do mesmo módulo que o negócio exige consistentes ([ARCHITECTURE.md](ARCHITECTURE.md#51-comando-escrita)).
- **Sem modelo anêmico no domínio.** Regra de negócio fica na entidade, no agregado, no VO, no enum ou em um serviço de domínio (`CalculoFreteService`), não espalhada nos handlers. O handler só orquestra: carrega via repository, autoriza, chama o domínio, salva via repository, publica eventos. Esse é o principal risco das fatias verticais; a revisão deve barrar `if` de regra de negócio dentro de handler.
- **Fatias não se conhecem.** Uma fatia de `features/` não importa outra. Se duas fatias precisam do mesmo código, ele sobe para a pasta do seu tipo no módulo (`entities/`, `services/`, `repositories/`, `clients/`, ...).
- **Nomes de instâncias e variáveis.** Um objeto tem um nome só, e o nome diz o que ele é:
  - **dependência injetada = nome do tipo em camelCase**, privada e somente leitura: `pedidoRepository: PedidoRepository`, `calculoFreteService: CalculoFreteService`;
  - **dependência por interface = nome da interface**, para o leitor ver a fronteira: `consultaCreditoPort: ConsultaCreditoPort`, `estoqueApi: EstoqueApi`;
  - **estado e acesso com o mesmo nome:** o campo privado e o getter que o expõe têm o nome do conceito (`status` guardado, `status()` lido; `total` guardado ou calculado, `total()` lido), sem prefixo `_` nem sinônimo. Um conceito não ganha dois nomes no mesmo objeto (`status`/`situacao`, `motivoRecusa`/`motivo`, `valorTotal`/`total`): quem busca um não acha o outro, e o agente copia o par para cada campo novo; os sinônimos recusados de cada termo estão no [glossário](docs/DOMAIN.md#4-linguagem-ubíqua). Sinal de violação: getter cujo nome difere do campo que ele devolve;
  - **variável local = conceito do domínio** no singular ou no plural (`pedido`, `itensDisponiveis`); um objeto, um nome (não `encontrado` e depois `pedido`), inclusive na releitura sob trava ([exemplo](ARCHITECTURE.md#51-comando-escrita));
  - **sem abreviações** (`repo`, `em`, `uc`, `svc`) e **sem genéricos** (`data`, `result`, `resultado`, `item`, `obj`, `novo`, `encontrado`, `linha`) quando há um conceito;
  - parâmetro e objeto de parâmetros com o nome do conceito do próprio domínio, nunca emprestado de outro.
  - **sem artigo nem a preposição "de"**, papel técnico por último; atributo de um conceito leva o dono primeiro (`PedidoId`), coisa em si leva o núcleo primeiro (`ItemPedido`, `ConsultaCreditoPort`); regras completas e o porquê em [CODEBASE_MAP.md](CODEBASE_MAP.md#convenção-de-nomes).
- **Nomes:** português do Brasil com sufixo técnico em inglês (`AprovarPedidoCommand`, `AprovarPedidoHandler`, `PedidoAprovadoEvent`, `PedidoNaoEncontradoException`). Entidades, agregados e VOs não têm sufixo (`Pedido`, `Dinheiro`). Tabela completa em [CODEBASE_MAP.md](CODEBASE_MAP.md#convenção-de-nomes).

### Um conceito, uma definição: como reutilizar

A regra de [Um conceito de negócio, uma definição](#simplicidade-primeiro) falha de um jeito previsível: o segundo caso de uso que precisa do conceito o reescreve "do jeito dele". Com duas definições, quem muda uma não sabe da outra.

**Conceito composto, dois gates.** "Cliente bloqueado" = tem fatura vencida **ou** está suspenso. Ele é definido uma vez (método do agregado, VO ou serviço de domínio) e os gates de `CriarPedido` e de `RenovarAssinatura` chamam a mesma definição e citam o mesmo nome de regra:

```
// entities/situacao-cliente: o nome da regra é declarado uma vez, junto da definição (o mesmo de docs/DOMAIN.md)
SituacaoCliente.REGRA_BLOQUEIO = "clienteSemBloqueio"

// entities/situacao-cliente (VO): a definição única
SituacaoCliente(temFaturaVencida, suspenso):
  bloqueado(): this.temFaturaVencida || this.suspenso

// services/regras-pedido.service: gate de CriarPedido
avaliar(situacaoCliente, pedido):
  violacoes = []
  se situacaoCliente.bloqueado():
    violacoes.adicionar(Violacao(SituacaoCliente.REGRA_BLOQUEIO, "o cliente 42 tem fatura vencida ou está suspenso; regularize para comprar"))
  ...
  devolver violacoes

// services/regras-assinatura.service: gate de RenovarAssinatura
avaliar(situacaoCliente, assinatura):
  violacoes = []
  se situacaoCliente.bloqueado():
    violacoes.adicionar(Violacao(SituacaoCliente.REGRA_BLOQUEIO, "o cliente 42 tem fatura vencida ou está suspenso; regularize para renovar"))
  ...
```

O repository carrega os fatos (`clienteRepository.obterSituacao(clienteId)` devolve `SituacaoCliente`); a decisão "está bloqueado?" fica no VO. A mensagem pode variar com o caso de uso; o nome da regra e a definição, não.

**Conceito que é consulta.** Quando o conceito seleciona registros ("pedidos aguardando estoque"), ele é **um** método do repository com o nome do conceito. Variantes da mesma consulta compartilham o critério num ponto privado:

```
// repositories/pedido.repository
listarAguardandoPorProduto(produtoId): consultar(this.criterioAguardando(produtoId)).ordenarPor(criadoEm)
contarAguardandoPorProduto(produtoId): contar(this.criterioAguardando(produtoId))
privado criterioAguardando(produtoId): status == AGUARDANDO_ESTOQUE e produtoId == produtoId e reservaExpiradaEm == nulo
```

Nunca no handler: `aguardando = listarPendentes(produtoId) + listarSemReserva(produtoId)` é uma terceira definição de "aguardando".

**Predicados com nome também dentro do agregado.** Quando o próprio agregado acumula violações, cada regra é um predicado privado com nome, não um ternário anônimo dentro da montagem da lista:

```
// entities/assinatura
renovar(hoje, ator):
  violacoes = []
  se this.atingiuMaximoRenovacoes(): violacoes.adicionar(Violacao("maximoRenovacoesRespeitado", "a assinatura já foi renovada 3 vezes"))
  se this.vencidaHaMaisDe(PRAZO_RENOVACAO, hoje): violacoes.adicionar(Violacao("renovacaoDentroPrazo", "o prazo de renovação acabou em 10/03"))
  se violacoes não vazia: lançar RenovacaoRecusadaException(violacoes)
  this.transicionar(RENOVAR, ator)   // porta única; registra a transição para o histórico (ARCHITECTURE.md §5.4)

privado atingiuMaximoRenovacoes(): this.renovacoes >= MAXIMO_RENOVACOES
```

**Teste que trava a definição:** casos do conceito, os que são e os que não são ([TESTING.md](TESTING.md#4-escrevendo-bons-testes)):

```
casos (temFaturaVencida, suspenso, bloqueado):
  (sim, não, sim)
  (não, sim, sim)
  (sim, sim, sim)
  (não, não, não)
```

**Sinais de violação para a revisão:**
- condição de negócio montada no handler, listener ou job (`||`/`&&` de consultas ou de predicados);
- o mesmo conceito com nomes ou textos de regra diferentes em dois gates (`clienteSemBloqueio` num, `clienteAdimplente` no outro);
- ternário ou condição anônima dentro da lista de violações.

### Um conceito em memória e na consulta

Caso particular de [Um conceito, uma definição](#um-conceito-uma-definição-como-reutilizar). Quando o mesmo conceito é usado pela entidade (em memória) e pelo critério de uma consulta, a definição continua sendo uma só, e as duas formas a leem do mesmo lugar. Sem isso, "pedido ativo" fica com duas definições: um predicado na entidade e um `where` no repository.

- **Conceito que é um conjunto de estados:** o conjunto tem nome no enum de estado, e o predicado da entidade e o critério do repository usam esse conjunto.
- **Conceito mais rico** (estado + prazo + outro campo): uma specification em `specifications/` expõe `satisfeitaPor(entidade)` para a memória e o critério para a consulta, os dois no mesmo arquivo e com o mesmo teste de casos.

```
// enums/pedido-status.enum: o conjunto com nome é a definição
PedidoStatusEnum.ativos = [ABERTO, AGUARDANDO_ESTOQUE, EM_SEPARACAO]

// entities/pedido: predicado em memória
ativo(): PedidoStatusEnum.ativos.contem(this.status)

// repositories/pedido.repository: o mesmo conjunto no critério, sem redefinir
contarAtivosPorCliente(clienteId): contar(clienteId == clienteId e status em PedidoStatusEnum.ativos)

// specifications/pedido-atrasado.specification: conceito composto que depende do tempo
PedidoAtrasadoSpecification:
  TOLERANCIA = 3 dias                                   // o limite é declarado uma vez, aqui
  satisfeitaPor(pedido, agora): PedidoStatusEnum.ativos.contem(pedido.status) e pedido.prazoEntrega + TOLERANCIA < agora
  criterio(agora): status em PedidoStatusEnum.ativos e prazoEntrega < agora - TOLERANCIA

// entities/pedido: o agregado usa a specification
atrasado(agora): PedidoAtrasadoSpecification.satisfeitaPor(this, agora)

// repositories/pedido.repository: só traduz o critério para o ORM ({{AGENTE: ex.: where do ORM, scope}})
listarAtrasadosPorCliente(clienteId, agora): consultar(clienteId == clienteId e PedidoAtrasadoSpecification.criterio(agora))
```

O repository recebe o critério pronto e só o traduz para o ORM; a decisão "o que é atrasado" não é dele.

**Definição que depende do tempo.** "Atrasado", "vencido", "expirado" recebem `agora` como parâmetro (vindo do relógio do framework, no handler) e são a mesma definição na consulta e no domínio: a specification declara uma vez a condição e o limite de tempo (tolerância, prazo em dias), e o agregado e o repository a chamam com o mesmo `agora`. O repository nunca reescreve a condição nem reaproveita só o limite. Por quê: com o limite compartilhado e o predicado copiado, a primeira mudança (de `<` para `<=`, de dias corridos para úteis) chega a um lado só, e o pedido aparece atrasado na lista e em dia na regra. Sinal de violação: comparação de data com `agora` (ou `hoje`) dentro do repository fora da specification.

### Passo comum a vários casos de uso

Quando o mesmo sub-roteiro (travar, carregar a fila, atualizar, salvar) aparece pela terceira vez em handlers diferentes, ou empurra um handler para além do [limite do papel](#tamanho-e-complexidade-por-papel) (40 linhas de código; referência ~25–30) ou de ~5 dependências, extraia nesta ordem de preferência:

1. **A regra do passo vai para o domínio**: agregado, VO ou serviço de domínio, que recebe os dados prontos e devolve a decisão. O handler continua dono da sequência (carregar, travar, chamar o domínio, gravar) e fica com uma linha onde tinha dez.
2. **"Depois de X, também Y", e precisa ser atômico:** um método do repository que carrega ou grava o conjunto com o nome do conceito (`obterFilaReservasParaAtualizar(produtoId)`, com a trava), sem regra, mais a regra em (1).
3. **Não precisa ser atômico:** uma reação a evento ([ARCHITECTURE.md](ARCHITECTURE.md#53-eventos-passo-do-caso-de-uso--reação-a-um-fato)), com entrega garantida se gravar estado de negócio.

Nunca um "service de aplicação" que esconde a sequência inteira do handler: o handler deixa de ser o roteiro e o service cresce até misturar todos os casos de uso.

```
// antes: o mesmo bloco em CancelarPedido, DevolverPedido e ExpirarPedido
fila = this.reservaRepository.travarFilaPorProduto(pedido.produtoId)
proxima = fila.reservas.filtrar(r => r.status == AGUARDANDO).ordenarPor(criadoEm).primeira()
se proxima: proxima.transicionar(CONFIRMAR) ...

// depois: a regra no agregado; o handler continua com a sequência à vista
fila = this.reservaRepository.obterFilaParaAtualizar(pedido.produtoId)   // carrega e trava
fila.liberarVaga(pedido.id)                                              // regra: quem é o próximo
transacao { this.pedidoRepository.salvar(pedido); this.reservaRepository.salvar(fila) }
```

**Entrada do domínio montada de várias leituras.** Quando vários handlers montam o mesmo objeto de entrada do domínio (`DisponibilidadeEstoque`, `SituacaoCliente`) a partir de várias leituras, um método com o nome do conceito devolve o objeto pronto, **sem regra de negócio** (a decisão continua no objeto montado). Quando: a mesma regra de três acima, ou já na segunda repetição se a montagem tem mais de uma leitura. Por quê: a montagem copiada diverge em detalhes (um handler exclui o próprio pedido, o outro não), e cada cópia é uma definição silenciosa do conceito.
- **Dados todos do próprio módulo** → método de leitura com o nome do conceito no repository dono, que devolve o objeto de entrada pronto (`reservaRepository.obterDisponibilidadeEstoque(produtoId)`), com uma consulta ou várias dentro dele.
- **Parte vem de outro módulo** (`<Modulo>Api`) → o handler lê a API numa variável com nome (uma linha) e a passa como argumento ao mesmo método do repository, que monta o resto (`obterDisponibilidadeEstoque(produtoId, saldoEstoque)`). Repository nunca usa outro repository nem `<Modulo>Api`, e nenhum tipo novo nasce para isso. Se o dado do outro módulo é lido sempre, prefira a cópia local alimentada por eventos ([ARCHITECTURE.md §6](ARCHITECTURE.md#6-comunicação-entre-módulos)), e o argumento some.

```
// antes: as mesmas leituras e a mesma montagem em ConfirmarPedido, ReservarProduto e CancelarReserva
saldo = this.estoqueApi.obterSaldo(command.produtoId)
reservados = this.reservaRepository.contarAtivasPorProduto(command.produtoId)
aguardando = this.reservaRepository.contarAguardandoPorProduto(command.produtoId)
disponibilidadeEstoque = DisponibilidadeEstoque(saldo, reservados, aguardando)

// depois: repositories/reserva.repository — monta, não decide
obterDisponibilidadeEstoque(produtoId, saldoEstoque):
  reservados = contar(reservas ativas do produto)
  aguardando = contar(reservas aguardando do produto)
  devolver DisponibilidadeEstoque(saldoEstoque, reservados, aguardando)

// no handler: a leitura externa com nome, a montagem numa linha, a regra no VO
saldoEstoque = this.estoqueApi.obterSaldo(command.produtoId)
disponibilidadeEstoque = this.reservaRepository.obterDisponibilidadeEstoque(command.produtoId, saldoEstoque)
pedido.confirmar(disponibilidadeEstoque)
```

**Preparar antes de implementar.** Se a demanda é difícil no código atual (a montagem que ela precisa já está copiada em outros handlers, o handler que ela altera já está no limite), o primeiro passo do plano é a preparação: a extração acima, sem mudar comportamento, com os testes verdes antes e depois e em commit próprio; só então a feature, que passa a ser uma mudança pequena. Primeiro deixe a mudança fácil, depois faça a mudança fácil. Por quê: preparada antes, a extração é verificada pelos testes que já existem; deixada para depois, a feature nasce com mais uma cópia, e a limpeza vira dívida que ninguém agenda.

**Cada passo do plano é uma fatia completa.** Um passo leva um comportamento de ponta a ponta (domínio, handler, repository, rota) e termina com um teste passando que o prova sozinho; nunca uma camada ("primeiro o domínio, depois o repository"), que só se verifica quando a última camada chega.

```
// plano por camada: nada se verifica até o passo 3
1. entidade Pedido com limite   2. repository   3. handler e rota

// plano em fatias: cada passo termina verde
0. preparação: extrair obterDisponibilidadeEstoque dos 3 handlers → testes atuais verdes, commit refactor
1. confirmar pedido dentro do limite → teste de integração do handler passa
2. recusar pedido acima do limite → teste do erro de regra passa
```

### Interfaces só quando há motivo

Interface não é padrão ([ADR-0004](docs/adr/0004-interfaces-so-em-fronteiras.md)). Crie uma só nos casos abaixo.

**Usa interface** (sufixo `Port`, ou a API pública do módulo `<Modulo>Api`):

| Caso | Por quê |
|---|---|
| Sistema externo (ERP, pagamento, e-mail, SMS) | lento, instável ou caro em teste; o modelo externo não vaza para o domínio (anticorruption layer) |
| LLM (porta de IA) | não determinístico, pago, troca de modelo; fake no teste |
| Mais de uma implementação real | estratégias (frete, gateway de pagamento, provedores) |
| API pública entre módulos (`<Modulo>Api`, implementada pela `<Modulo>Facade`) | contrato; o consumidor não depende da implementação, que pode virar cliente HTTP se o módulo for extraído |

**Não usa interface** (classe concreta):

| Caso | Como |
|---|---|
| Repository (um banco só) | classe concreta `PedidoRepository` em `repositories/`, sem prefixo de tecnologia; único lugar com ORM/SQL |
| Mapper, domain service, policy, handler | classe concreta, instanciável e injetada (policy pode ser método do agregado, se depende só do estado dele) |
| Recursos do próprio framework (autorização, flags, cache, filas, cliente HTTP, data/hora, IDs) | usados direto; nos testes, os fakes e helpers que o framework oferece |

- **Regra de três para interfaces:** crie quando surgir a segunda implementação real ou a fronteira externa, não antes. Um adapter é ponto de extensão hipotético; dois é real.
- **Teste da remoção:** se apagar a classe ou interface e a complexidade sumir junto, ela era só passagem; não crie. (Não se aplica a controller e handler, que são bordas deliberadas da [matriz](ARCHITECTURE.md#41-responsabilidades).)
- **Atenção, agentes:** "não precisa de interface" **não** autoriza chamar sistema externo, LLM ou SDK direto do handler, nem usar o ORM fora do repository. Fronteira externa é sempre via `Port`, com `Client` em `clients/` e fake nos testes.

## 3. Funções e classes

- Funções pequenas, um nível de abstração por função. Se precisa de comentário para separar "partes", são funções diferentes.
- **O método principal é um índice.** Pré-condições primeiro, com retorno antecipado; depois cada passo é uma chamada com nome de intenção. O leitor entende a operação em poucas linhas e desce só ao passo que precisa mudar:

  ```
  cancelar(command):
    pedido = this.pedidoRepository.obter(command.pedidoId)          // carregar
    this.pedidoPolicy.autorizarCancelamento(command.ator, pedido)  // pré-condições
    pedido.cancelar(command.ator, command.motivo)                  // regra + transição (e o registro dela)
    transacao { this.pedidoRepository.salvar(pedido) }             // gravar
    this.eventBus.despacharAposCommit(pedido.eventos())            // efeitos ({{AGENTE: tipo do framework}} em camelCase)
  ```
- **O handler lê como os passos do caso de uso:** carregar → autorizar → domínio → gravar → publicar. Montagem da entrada vai para um método com o nome do conceito ([passo comum](#passo-comum-a-vários-casos-de-uso)) e a regra vai para o domínio; o tamanho tem a régua do [papel](#tamanho-e-complexidade-por-papel).
- **Nenhuma leitura dentro de argumento.** Cada leitura (repository, `<Modulo>Api`, `Port`) vira uma variável com o nome do conceito antes do uso. Leitura aninhada em argumento esconde o que o caso de uso carrega e quantas consultas faz:

  ```
  // ruim: três leituras dentro de uma chamada
  disponibilidade = DisponibilidadeEstoque.de(produto, this.estoqueApi.obterSaldo(this.pedidoRepository.obter(id).produtoId), this.reservaRepository.contarAtivas(...))

  // bom: cada leitura com nome, depois o domínio
  pedido = this.pedidoRepository.obter(command.pedidoId)
  saldoEstoque = this.estoqueApi.obterSaldo(pedido.produtoId)
  disponibilidadeEstoque = this.reservaRepository.obterDisponibilidadeEstoque(pedido.produtoId, saldoEstoque)
  pedido.confirmar(disponibilidadeEstoque)
  ```
- **Dependências e chamadas explícitas.** Dependências chegam pelo construtor; nada de buscar serviço no meio do método, despachar por string ou método mágico. "Ir para a definição" e a busca textual precisam funcionar.
- Até ~3 parâmetros; acima disso, um objeto de parâmetros nomeado.
- Sem parâmetros booleanos que mudam o comportamento (`enviar(true)`). Use duas funções ou um enum.
- Retorno antecipado (guard clauses) em vez de aninhamento profundo.
- Sem efeitos colaterais escondidos. Data/hora, aleatoriedade e IDs vêm dos recursos da linguagem, do framework ou do ORM; os testes controlam o tempo com os helpers da ferramenta de testes, sem relógio próprio.

### Tamanho e complexidade por papel

Não há número ideal de linhas: o critério é coesão e intenção (cada trecho com um nome que diz o quê; um nível de abstração por método). O número é gatilho para olhar, não meta, e a régua depende do papel. No handler, um orquestrador linear, linhas são o proxy certo: um handler de 60 linhas costuma ser uma sequência de chamadas quase sem `if`, de complexidade baixa, que esconde montagem repetida ou regra que é do domínio. No domínio, o que pesa é ramificação e aninhamento, não comprimento. Extrair só para caber no número (`parte1`, `executarResto`, dois métodos que só se entendem lidos juntos) é pior que o original: extraia por intenção.

| Papel | Verificação automática (erro) | Referência | Revisão |
|---|---|---|---|
| Handler (`executar`/`handle`) | até 40 linhas de código (contadas sem linhas em branco e comentários), aninhamento até 2, complexidade ciclomática até 6 | ~25–30 linhas | lê como os passos do caso de uso; [sem leitura dentro de argumento](#3-funções-e-classes); montagem repetida → método de leitura com nome ([passo comum](#passo-comum-a-vários-casos-de-uso)); extração por intenção |
| Domínio (agregado, VO, enum, serviço de domínio, specification, policy) | complexidade até 10, aninhamento até 3; sem limite de linhas | — | invariante num lugar só; sem método raso que só repassa |
| Repository e controller | mesma complexidade e aninhamento do domínio; sem limite de linhas | controller ~15 linhas | sem regra de negócio |
| Testes | nenhum limite (os arquivos de teste ficam fora destas regras) | — | um comportamento por teste |
| Classe | até 6 dependências no construtor | ~5; classe com mais de ~200 linhas de código é alerta de revisão | responsabilidade única |

**Verificação.** No `{{AGENTE: CMD_CHECK}}`: `{{AGENTE: VERIFICACAO_HANDLER}}` mede linhas, aninhamento e complexidade só no método principal dos handlers de `features/` (linhas no orquestrador); `{{AGENTE: VERIFICACAO_COMPLEXIDADE}}` mede complexidade e aninhamento no restante do código de produção, sem contar linhas (complexidade no domínio); `{{AGENTE: VERIFICACAO_DEPENDENCIAS_CONSTRUTOR}}` conta as dependências do construtor. Use a regra pronta do lint ou da análise estática da linguagem; se a ferramenta mede outra métrica (complexidade cognitiva em vez de ciclomática), ajuste os números para o equivalente e diga qual é a métrica. O que ela não mede fica na revisão, sem verificação artesanal. Mensagem no [formato do kit](ARCHITECTURE.md#9-fitness-functions): o quê · por quê · faça isto (extraia a montagem por intenção, leve a regra ao domínio, use guard clauses) · "não aumente o limite nem desative: pergunte" · link para esta seção.

**Exceção.** Uma sequência longa pode ser legítima. O agente pergunta antes; aprovada, a verificação é desativada só naquela função, com o motivo escrito ao lado (por que a sequência é longa). "Não deu para extrair" não é motivo. Não aumente o limite nem desative sem perguntar.

Arquivo pequeno não basta se o fluxo se espalha por muitos deles: o alvo é arquivo pequeno **e** roteiro inteiro no handler.

## 4. Erros

| Situação | Como tratar |
|---|---|
| Violação de regra de negócio esperada | exceção de domínio de uma das categorias fechadas abaixo, convertida em resposta pelo tratamento global de erros do framework. `Result`/`Either` só se for o idioma da linguagem ou do framework |
| Desfecho de negócio que não é falha (ex.: "assinado fora do prazo, vai para análise") | resultado com nome devolvido pelo handler, não exceção |
| Entrada inválida na borda | rejeitar no `Request` da fatia (validação de schema), antes do handler |
| Falha de infraestrutura (timeout, rede, serviço externo fora) | exceção técnica, tratada pelo retry e timeout do cliente HTTP ou da fila do framework no `Client`; se persistir, vira erro mapeado para resposta |
| Bug (estado impossível) | deixar estourar; será capturado, logado e alertado |

**Categorias fechadas de erro de domínio.** Toda exceção de domínio pertence a uma categoria, e cada categoria tem um status HTTP ([docs/API_GUIDELINES.md](docs/API_GUIDELINES.md#erros)). Com um vocabulário fechado, cada borda trata todos os desfechos e o leitor não procura `try/catch` pelo caminho.

| Categoria | Exemplo | Status |
|---|---|---|
| Não encontrado | `PedidoNaoEncontradoException` | 404 |
| Sem permissão | `CancelamentoNaoPermitidoException` | 403 |
| Entrada inválida | erro de validação de formato do Request, com `errors` por campo | 400 |
| Estado não permite / conflito com o estado existente | `PedidoJaFaturadoException` (transição recusada pela tabela); `ProdutoCodigoJaCadastradoException` (unicidade de negócio violada) | 409 |
| Regra violada | `LimiteCreditoExcedidoException`; a exceção base carrega a lista `violacoes` (uma ou várias regras) | 422 |

Critério entre 409 e 422: a operação conflita com algo que já existe ou com o estado atual (transição recusada, código já cadastrado, versão desatualizada) → 409; os dados enviados violam uma regra de negócio, independentemente do que existe → 422.

- A mensagem diz o que aconteceu, com quais valores e o que fazer ("o pedido 123 já foi faturado; para devolver, abra uma devolução"), sem vazar dado sensível. Mensagem genérica ("operação não permitida") é defeito.
- Regras independentes violadas voltam juntas, numa só resposta, no campo `violacoes` do Problem Details. **Formato único:** lista de `{ regra, mensagem, campo? }`, em que `regra` é o nome da regra ([convenção](docs/API_GUIDELINES.md#erros)) e `mensagem` é o texto de negócio. O nome é único por conceito: dois gates que verificam o mesmo conceito citam o mesmo nome de regra ([exemplo](#um-conceito-uma-definição-como-reutilizar)). O gate devolve exatamente essa lista, e cada regra é um predicado com nome (`atingiuLimitePedidosAbertos(cliente)`), nunca uma condição anônima.
- **O nome do tipo do erro vem do tipo.** A classe base de exceção de domínio obtém o nome da própria classe (recurso da linguagem) uma vez; as subclasses não repetem o nome numa string ou num atributo. Nome duplicado em string fica errado na primeira renomeação.
- Nunca engula erro (`catch` vazio ou só com log seguido de continuar como se nada fosse), nem o converta em resultado vazio (`[]`, `false`, `null`) que o chamador ignora, nem siga até o commit depois de uma falha.
- Mapeamento erro → resposta HTTP fica no tratamento global de exceções do framework, não em cada fatia nem em try/catch no controller ([docs/API_GUIDELINES.md](docs/API_GUIDELINES.md#erros)).

## 5. Comentários e documentação no código

- Comente o **porquê**, não o quê. O código diz o quê.
- Bons comentários: motivo de uma decisão não óbvia, link para issue/ADR, aviso de armadilha, invariante de negócio. Cite a fonte quando houver: manual externo, issue, identificador da regra no requisito ou em [docs/DOMAIN.md](docs/DOMAIN.md).
- **Comentário falso, copiado ou desatualizado é defeito**, tratado como bug: o leitor acredita nele. Passos numerados em comentário ("passo 1… passo 12") pedem extração de funções com nome.
- Sem código comentado; o histórico do git guarda.
- `TODO` só com issue vinculada: `TODO(#123): ...`.
- Documente a API pública do módulo (a interface `<Modulo>Api`) e as interfaces `Port`.

## 6. Design patterns: quando usar aqui

| Padrão | Uso típico no projeto | Evite quando |
|---|---|---|
| Repository | persistência de agregados (um por agregado raiz) e consultas de leitura que devolvem DTOs: classe concreta em `repositories/` (`PedidoRepository`), sem interface; único lugar com ORM/SQL; não abre nem confirma transação | virar repository genérico (`BaseRepository<T>` com CRUD): métodos com nome de negócio que revela todo filtro aplicado (`listarPendentesPorCliente`, nunca `listarTodos` que filtra) |
| Unit of Work | uma transação por caso de uso, aberta e confirmada à vista no handler com o recurso do framework/ORM | aninhar transações; o caso de uso chamado reaproveita a de quem chamou |
| Factory | criação de agregados com invariantes complexas; factories do ORM/biblioteca de testes para dados de teste | um construtor simples resolve |
| Strategy | variações de regra (preço, frete, cálculo de impostos) | só existe uma variação |
| Adapter | toda integração externa (`Client` em `clients/` implementando um `Port`) | |
| Facade (API do módulo) | `<Modulo>Facade` implementa a interface `<Modulo>Api` e só delega aos handlers do próprio módulo; é o que outros módulos injetam | ter regra, acessar ORM ou delegar para outra fachada |
| Decorator / middleware | aspectos transversais pelo mecanismo do framework (middleware, interceptors, recursos de retry e cache) | a lógica é de negócio; o framework já oferece o recurso |
| Observer / eventos | reação a fatos de domínio entre agregados e módulos pelo mecanismo de eventos do framework (`Listener` e `Subscriber` em `listeners/`, delegando a handlers) | o fluxo precisa de resposta síncrona |
| Specification / gate | regras de seleção/elegibilidade reutilizadas (`PedidoElegivelParaDescontoSpecification`), com o predicado em memória e o critério da consulta no mesmo lugar ([exemplo](#um-conceito-em-memória-e-na-consulta)); *gate*: classe pura que avalia regras independentes e devolve a lista de falhas | a regra é usada uma única vez |
| Tabela declarativa | variação que difere só em dados (colunas de relatório, campos de documento, tipos de ato): cada caso é uma declaração curta sobre um mecanismo comum | a variação é de comportamento: use Strategy |
| Máquina de estados | ciclo de vida como tabela de transições, única porta de mudança de estado | o agregado não tem ciclo de vida |
| Command | intenção de escrita como objeto (`AprovarPedidoCommand`), executada por um handler (`AprovarPedidoHandler`), pelo barramento do framework se houver | |
| Null Object | comportamento padrão opcional (ex.: notificador desligado) | esconderia um erro |
| Anticorruption layer | modelos de sistemas externos | |

Anti-padrões a evitar:
- Singleton com estado global; Service Locator; despacho por string ou método mágico; substituição de classe por varredura de pasta.
- God class/"Manager"/"Helper"/"Utils" genéricos; handler que só repassa para um service do agregado com todos os casos de uso; fachada sobre fachada (a `<Modulo>Facade` da API pública é a exceção: ela marca a fronteira entre módulos, e a fachada passa-adiante não marca fronteira nenhuma).
- Função de topo fora da borda do framework; classe só com métodos estáticos; objeto literal como namespace.
- Gravação ou mudança do agregado em listener (é passo do caso de uso).
- Estado de caso de uso em sessão entre requisições: processo de várias etapas tem estado persistido e consultável.
- Gerações paralelas do mesmo conceito (`New`, `_NEW`, dois endpoints e uma flag para o mesmo caso de uso).
- Herança para reaproveitar fluxo; reimplementar o que o framework já oferece.

## 7. Code smells e a refatoração correspondente

| Cheiro | Refatoração |
|---|---|
| Função longa | extrair função |
| Muitos parâmetros | objeto de parâmetros / VO |
| Obsessão por primitivos | value object |
| `switch` sobre tipo repetido | polimorfismo / strategy |
| Inveja de recursos (método usa mais dados de outro objeto) | mover método |
| Agregado de dados (mesmos campos sempre juntos) | extrair VO |
| Mudança divergente (uma classe muda por vários motivos) | dividir classe |
| Cirurgia espalhada (uma mudança toca muitos arquivos) | reunir responsabilidade |
| Comentário explicando bloco | extrair função com nome claro |
| Número mágico | constante ou enum com nome |
| Mesmo conceito de negócio com duas definições ("disponível" calculado de dois jeitos) | consolidar num único predicado ou método de leitura com o nome do conceito e reutilizar |
| Nome genérico ou que mente (`tratar`, `processar`, `existe(): void`, `listarTodos` que filtra) | renomear pelo que faz e devolve |
| Passos numerados em comentário | extrair cada passo em método com nome de intenção |

Refatoração é um passo separado, com testes verdes antes e depois. Não misture refatoração e mudança de comportamento no mesmo commit.

**O que vale refatorar.** Um cheiro da tabela não basta para propor refatoração: a proposta é **forte** quando junta três sinais, **vale explorar** com dois e **especulativa** com um.
- **A área muda com frequência:** o histórico de versões mostra o arquivo ou o módulo em muitos commits recentes ({{AGENTE: ex.: `git log --since=6.months --format= --name-only | sort | uniq -c`}}). Código feio que ninguém toca não paga a refatoração.
- **Houve atrito real na tarefa atual:** a mudança pedida exigiu tocar vários arquivos, copiar uma montagem ou contornar a estrutura; cite onde.
- **Passa no teste da deleção:** imagine a classe ou o módulo apagado. Se a complexidade se espalharia pelos chamadores (cada um teria de refazer a regra ou a montagem), ele concentra algo e vale fortalecer; se ela simplesmente sumiria, ele só repassa chamadas e a proposta é removê-lo. Não se aplica a controller e handler, finos de propósito ([ARCHITECTURE.md §4.1](ARCHITECTURE.md#41-responsabilidades)).

A saída é a proposta graduada, com os sinais que a sustentam, não a execução: refatoração fora do pedido é pergunta ([AGENTS.md](AGENTS.md#perguntar-antes)), salvo a preparação que a própria demanda exige ([Passo comum](#passo-comum-a-vários-casos-de-uso)). Proposta que contraria uma ADR aceita só é feita quando o atrito observado justifica reabri-la, e então propõe a ADR substituta. Por quê: sem critério, todo cheiro vira proposta, e as poucas que pagam o custo se perdem no meio das outras.

## 8. Regras para código escrito por agentes de IA

Valem para agentes e para pessoas que revisam o que eles produzem.

- **Não invente.** APIs, funções, opções de configuração e pacotes precisam existir. Verifique no código ou na documentação.
- **Framework first.** Antes de escrever algo de infraestrutura, consulte a documentação oficial do framework e das bibliotecas e use o recurso nativo. Na dúvida se existe, pergunte em vez de criar.
- **Respeite a matriz de responsabilidades.** ORM só no repository; controller e request sem repository; regra só no domínio.
- **Procure antes de criar.** Busque arquivo ou recurso com o mesmo propósito no projeto e no framework antes de escrever um novo.
- **Siga o exemplo de referência.** Antes de escrever, encontre **dois** exemplos do mesmo tipo no mesmo contexto e imite a estrutura. Se houver duas formas, siga o [exemplo de referência](CODEBASE_MAP.md#exemplos-de-referência), não a mais frequente. Se o documento e o vizinho divergirem, siga o vizinho e aponte a divergência no PR.
- **Nada de experimento ou código morto na árvore.** Tudo o que roda está ligado no registro do módulo; rascunho, alternativa comentada e caso de uso que só um teste liga saem do repositório.
- **Diffs pequenos.** Uma intenção por mudança. Não reformate nem renomeie código que não faz parte da tarefa.
- **Não enfraqueça a verificação.** Ajustar asserção, aumentar timeout, marcar teste como pulado ou afrouxar configuração de lint, arquitetura ou tipos para "passar" é proibido sem justificativa explícita no PR.
- **Verifique pelo resultado.** Diga o que foi observado (saída do teste, resposta da API), não só que "os testes passaram".
- **Sem dependências novas sem pedir.**
- **Explique o que não verificou.** Se um comando não pôde ser executado, diga no PR.
- Revisão humana é obrigatória para: segurança, migrações, contratos públicos e configuração de CI/deploy.
- **Pare e pergunte** quando a tarefa for ambígua, exigir decisão de produto ou cair na lista "perguntar antes" do `AGENTS.md`. Demanda ambígua se esclarece em rodadas:
  - **Rodadas por dependência.** Cada rodada leva só as perguntas cujos pré-requisitos já foram respondidos; a que depende de outra ainda aberta fica para a próxima. Por quê: perguntar tudo de uma vez obriga o usuário a responder hipóteses que a primeira resposta derruba.
  - **Cenário concreto de borda em cada pergunta**, redigida para que "sim" aceite a recomendação: "Um cliente com 2 pedidos em aberto cria o 3º e um dos dois é cancelado no mesmo minuto: o 3º conta como dentro do limite? Recomendo que sim, contando só os pedidos em aberto no momento da confirmação." Pergunta abstrata ("como tratar concorrência?") recebe resposta abstrata.
  - **Suposição não substitui pergunta.** Regra de negócio com mais de uma resposta defensável é pergunta. Suposição só vale para detalhe com uma resposta claramente defensável, ou quando o usuário delegou ("você decide"), registrada com as palavras dele. Por quê: suposição sobre regra de negócio é a decisão do usuário tomada sem ele, e só aparece quando já está no código.
  - **Termina quando nenhuma regra de negócio ficou presumida em silêncio:** cada uma foi perguntada ou, nos casos acima, registrada como suposição, em [docs/DOMAIN.md](docs/DOMAIN.md) e na tabela de critérios do [design doc](docs/design-docs/0000-template.md#critérios-de-aceitação) (sem design doc, no relato).

## 9. Commits e branches

- [Conventional Commits](https://www.conventionalcommits.org/): `feat(pedidos): aprovar pedido com limite de crédito`.
- Tipos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `build`, `ci`.
- Mensagem explica o porquê quando não for óbvio.
- Detalhes do fluxo em [CONTRIBUTING.md](CONTRIBUTING.md).
