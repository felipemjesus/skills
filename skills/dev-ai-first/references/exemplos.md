# Exemplos em pseudocódigo

Leia este arquivo só quando o projeto ainda não tem exemplo de referência real (pasta vazia); se houver código, o exemplo do projeto vence.

## Sumário

- [Regra do VO num lugar só](#regra-do-vo-num-lugar-só)
- [Um conceito, uma definição](#um-conceito-uma-definição)
- [Um conceito em memória e na consulta](#um-conceito-em-memória-e-na-consulta)
- [Passo comum: montar a entrada do domínio](#passo-comum-montar-a-entrada-do-domínio)
- [Handler como índice, sem leitura em argumento](#handler-como-índice-sem-leitura-em-argumento)
- [Formato do erro](#formato-do-erro)
- [Carregar uma vez, já travado](#carregar-uma-vez-já-travado)
- [Histórico gravado pelo repository](#histórico-gravado-pelo-repository)
- [Transição pelo tempo](#transição-pelo-tempo)
- [Erros na API do módulo](#erros-na-api-do-módulo)
- [Mensagem de verificação de arquitetura](#mensagem-de-verificação-de-arquitetura)
- [Handler com banco real e Port com fake](#handler-com-banco-real-e-port-com-fake)
- [Efeito depois do commit](#efeito-depois-do-commit)
- [Erro pelo código e valor conhecido](#erro-pelo-código-e-valor-conhecido)
- [Frontend: fatia e teste de componente](#frontend-fatia-e-teste-de-componente)
- [Envelope de evento](#envelope-de-evento)

## Regra do VO num lugar só

Regra em CODING_GUIDELINES §4 Erros: o request valida só a forma; a regra fica no VO. Acumular erros de VOs só quando a demanda pedir.

```
// src/modules/pedidos/features/criar-pedido/criar-pedido.request: só forma
quantidade: inteiro obrigatório

// entities/quantidade (VO): a regra, uma vez
Quantidade(valor):
  se valor <= 0: lançar EntradaInvalidaException(campo: "quantidade", "a quantidade 0 deve ser maior que zero")

// só se a demanda pede todos os erros de VO numa resposta
erros = []
quantidade = tentar Quantidade(request.quantidade), se EntradaInvalidaException: erros.adicionar(excecao)
total = tentar Dinheiro(request.total), se EntradaInvalidaException: erros.adicionar(excecao)
se erros não vazia: lançar EntradaInvalidaException(erros)   // 400, um item de errors por campo
```

## Um conceito, uma definição

Regra em CODING_GUIDELINES (simplicidade: um conceito, uma definição): dois gates chamam a mesma definição e citam o mesmo nome de regra; cada regra é um predicado privado com nome.

```
// entities/pedido
Pedido.REGRA_TOTAL = "totalIgualSomaItens"          // declarado uma vez, o mesmo de docs/DOMAIN.md
totalConfere(): this.total == soma(this.itens, i => i.subtotal())

aprovar(ator):
  violacoes = []
  se não this.totalConfere(): violacoes.adicionar(Violacao(Pedido.REGRA_TOTAL, "o total R$ 250,00 não confere com os itens"))
  se violacoes não vazia: lançar AprovacaoRecusadaException(violacoes)
  this.transicionar(APROVAR, ator)

// src/modules/vendas/...: outro gate usa a mesma definição, não reescreve a soma
se não pedido.totalConfere(): violacoes.adicionar(Violacao(Pedido.REGRA_TOTAL, "..."))
```

Sinais de violação: `||`/`&&` de negócio no handler, listener ou job; o mesmo conceito com dois nomes de regra; condição anônima dentro da lista de violações.

## Um conceito em memória e na consulta

Regra em CODING_GUIDELINES "Um conceito em memória e na consulta": o conjunto com nome é a definição; predicado e critério usam o mesmo conjunto.

```
// enums/pedido-status.enum
PedidoStatusEnum.ativos = [ABERTO, AGUARDANDO_ESTOQUE, EM_SEPARACAO]

// entities/pedido
ativo(): PedidoStatusEnum.ativos.contem(this.status)

// repositories/pedido.repository: o mesmo conjunto, sem redefinir
contarAtivosPorEstoque(estoqueId): contar(estoqueId == estoqueId e status em PedidoStatusEnum.ativos)
```

Nunca no handler: `listarAbertos() + listarEmSeparacao()` é outra definição.

## Passo comum: montar a entrada do domínio

Regra em CODING_GUIDELINES "Passo comum a vários casos de uso": a montagem repetida vira um método com o nome do conceito no repository dono, que monta e não decide; o dado de outro módulo entra como argumento.

```
// antes: copiado em AprovarPedido, SepararPedido e CancelarPedido
saldo = this.estoqueApi.obterSaldo(pedido.estoqueId)
comprometido = this.pedidoRepository.contarAtivosPorEstoque(pedido.estoqueId)
disponibilidade = DisponibilidadeEstoque(saldo, comprometido)

// depois: repositories/pedido.repository
obterDisponibilidadeEstoque(estoqueId, saldoEstoque):
  comprometido = contar(pedidos ativos do estoque)
  devolver DisponibilidadeEstoque(saldoEstoque, comprometido)
```

Repository nunca chama outro repository nem `<Modulo>Api`. Se a demanda precisa dessa montagem, o passo 0 do plano é a extração, sem mudar comportamento, testes verdes antes e depois, em commit próprio.

## Handler como índice, sem leitura em argumento

Regra em CODING_GUIDELINES (funções e classes): o handler lê como os passos (carregar, autorizar, domínio, gravar, publicar); cada leitura vira variável com nome antes do uso.

```
// ruim: leituras escondidas dentro de uma chamada
pedido.aprovar(DisponibilidadeEstoque.de(this.estoqueApi.obterSaldo(this.pedidoRepository.obter(id).estoqueId), ...))

// bom
aprovar(command):
  pedido = this.pedidoRepository.obter(command.pedidoId)
  this.pedidoPolicy.autorizarAprovacao(command.ator, pedido)
  saldoEstoque = this.estoqueApi.obterSaldo(pedido.estoqueId)
  disponibilidade = this.pedidoRepository.obterDisponibilidadeEstoque(pedido.estoqueId, saldoEstoque)
  pedido.aprovar(disponibilidade, command.ator)
  transacao { this.pedidoRepository.salvar(pedido) }
  this.eventBus.despacharAposCommit(pedido.eventos())
```

## Formato do erro

Regra em CODING_GUIDELINES §4 Erros: Problem Details; `type` derivado do nome da exceção num lugar só; 400, 409 e 422 são categorias distintas; violações juntas em `violacoes`.

```json
{
  "type": "https://exemplo.com/erros/estoque-insuficiente",
  "title": "Estoque insuficiente",
  "status": 422,
  "detail": "O pedido pede 11 unidades; há 10 em estoque.",
  "instance": "/pedidos/123/aprovar",
  "violacoes": [{ "regra": "totalIgualSomaItens", "mensagem": "o total não confere com os itens", "campo": "itens" }]
}
```

## Carregar uma vez, já travado

Regra em ARCHITECTURE §5.1: uma leitura, dentro da transação, já travada; se a chave da trava vem de outro agregado, só a chave fica fora.

```
transacao:
  pedido = this.pedidoRepository.obterTravado(command.pedidoId)
  this.pedidoPolicy.autorizarAprovacao(command.ator, pedido)
  pedido.aprovar(command.ator)
  this.pedidoRepository.salvar(pedido)

// chave de outro agregado
estoqueId = this.pedidoRepository.obterEstoqueId(command.pedidoId)
transacao:
  this.pedidoRepository.travarSaldoEstoque(estoqueId)
  pedido = this.pedidoRepository.obterTravado(command.pedidoId)
  ...
```

## Histórico gravado pelo repository

Regra em ARCHITECTURE §5.4: a transição tem porta única no agregado, que a registra; o repository grava agregado e histórico juntos, na transação do handler.

```
// entities/pedido
transicionar(acao, ator, motivo = vazio):
  destino = PedidoStatusEnum.transicoes.destino(acao, this.status)   // lança se a tabela recusa
  this.transicoes.adicionar(HistoricoPedido(de: this.status, para: destino, quando: agora, quem: ator, motivo))
  this.status = destino

// repositories/pedido.repository
salvar(pedido):
  gravar linha do pedido
  para cada t em pedido.transicoesPendentes(): inserir em historico_pedido
```

## Transição pelo tempo

Regra em ARCHITECTURE §5.4: o tempo usa a mesma tabela de transições; o job só delega ao handler.

```
PagamentoStatusEnum.transicoes:
  CONFIRMAR: PENDENTE -> CONFIRMADO
  EXPIRAR:   PENDENTE -> EXPIRADO

// jobs/expirar-pagamentos.job
executar(agora):
  para cada pagamentoId em this.pagamentoRepository.listarVencidosAte(agora):
    this.expirarPagamentoHandler.executar(ExpirarPagamentoCommand(pagamentoId))
```

## Erros na API do módulo

Regra em ARCHITECTURE §6: a API declara os erros; a fachada só delega; quem consome não recria a exceção.

```
// src/modules/vendas/api/vendas.api
VendasApi:
  obterVenda(vendaId): VendaDto              // lança VendaNaoEncontradaException (api/)

VendasFacade implementa VendasApi:
  obterVenda(vendaId): this.obterVendaHandler.executar(ObterVendaQuery(vendaId))

// src/modules/pedidos/...
venda = this.vendasApi.obterVenda(command.vendaId)   // não encontrada → 404 pelo tratamento global
```

## Mensagem de verificação de arquitetura

Regra em ARCHITECTURE §9: o quê, por quê, o que fazer, sem desativar a regra.

```
ORM fora de repository: src/modules/vendas/features/criar-venda/CriarVendaHandler importa o ORM.
Por quê: ORM e SQL ficam só no repository, para a consulta ter um dono e um teste.
Faça isto: mova a consulta para um método com nome de negócio em VendaRepository.
Não desative nem mude a configuração: se a exceção parece legítima, pergunte.
Ver ARCHITECTURE.md §4.1.
```

## Handler com banco real e Port com fake

Regra em TESTING §4: o handler roda com banco real; só o Port externo vira fake; confere estado gravado e eventos.

```
teste "recusa aprovação quando o estoque é insuficiente":
  container.substituir(PagamentoPort, new PagamentoFake())
  eventosFake = criarEventosFake()
  pedido = factory(Pedido).comQuantidade(11).doEstoque(factory(Estoque).comSaldo(10)).pendente().criar()

  excecao = esperarExcecao(EstoqueInsuficienteException):
    container.obter(AprovarPedidoHandler).executar(new AprovarPedidoCommand(pedido.id, ator: analista))

  esperar(container.obter(PedidoRepository).obter(pedido.id).status).ser(PedidoStatusEnum.PENDENTE)
  eventosFake.esperarNaoDespachado(PedidoAprovadoEvent)
```

## Efeito depois do commit

Regra em TESTING §4: se a gravação falha, nada é gravado e nenhum efeito sai.

```
teste "não cobra quando a gravação da aprovação falha":
  pagamentoFake = container.substituir(PagamentoPort, new PagamentoFake())
  pedido = factory(Pedido).pendente().criar()
  falharNaGravacao(PedidoRepository)

  esperarExcecao(...): aprovarPedidoHandler.executar(new AprovarPedidoCommand(pedido.id, ator: analista))

  esperar(pedidoRepository.obter(pedido.id).status).ser(PedidoStatusEnum.PENDENTE)
  esperar(pagamentoFake.cobrancas).serVazio()
```

## Erro pelo código e valor conhecido

Regra em TESTING §4: o teste confere o nome da regra ou o `type`, nunca o texto; o esperado é um valor conhecido, não a fórmula do código.

```
esperar(resposta.status).ser(422)
esperar(resposta.corpo.violacoes.map(v => v.regra)).conter("totalIgualSomaItens")
// ruim: conferir resposta.corpo.title

// ruim: tautológico, passa com a fórmula errada
esperar(pedido.total()).ser(somar(itens, i => i.preco * i.quantidade))
// bom
esperar(pedido.total()).ser(Dinheiro.de("250.00"))
```

## Frontend: fatia e teste de componente

Regra em docs/FRONTEND.md: hook e formulário ficam na pasta da fatia; a violação do backend aparece junto do campo.

```
// features/criar-venda/use-criar-venda
useCriarVenda():
  mutation = useMutation(enviar: dados => vendasApi.criar(dados), aoTerSucesso: () => invalidar(['vendas']))
  return { criar: mutation.enviar, enviando: mutation.pendente, erro: mutation.erro }

teste "mostra a violação do backend junto do campo":
  rede.responder(POST /vendas, 422, problemDetails(violacoes: [{ regra: "totalIgualSomaItens", campo: "itens", mensagem: "o total não confere com os itens" }]))
  renderizar(<CriarVendaForm />)
  clicar(botão "Criar venda")
  esperar(texto "o total não confere com os itens" visível)
```

## Envelope de evento

Regra em docs/EVENTS.md: com broker externo, o evento leva id, tipo versionado e rastreio.

```
{
  id: "01J...",                    // idempotência
  type: "vendas.pedido-aprovado",  // <contexto>.<evento>
  version: 1,
  occurredAt: "2026-10-28T12:00:00Z",
  producer: "vendas",
  correlationId: "...",
  data: { pedidoId: "...", total: { valor: "800.00", moeda: "BRL" } }
}
```
