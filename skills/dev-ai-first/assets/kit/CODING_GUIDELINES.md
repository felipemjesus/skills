# Diretrizes de código

> Princípios que valem em qualquer estrutura; o mecânico fica com lint e formatador. Como cada regra é garantida: [ARCHITECTURE.md §9](ARCHITECTURE.md#9-fitness-functions). Padrão do projeto que contraria um princípio: siga o padrão, registre e pergunte ([ordem de verdade](AGENTS.md#ordem-de-verdade)). Exceção a uma regra se explica no PR.

## 1. Princípios

### Framework first
Antes de criar abstração, utilitário, wrapper ou infraestrutura, procure o recurso na documentação oficial de {{AGENTE: FRAMEWORK}} e das bibliotecas adotadas e use-o como ela mostra. Solução própria só quando o framework não oferece, com justificativa no PR ou em ADR.
<!-- se: estrutura-kit -->
Decisão na [ADR-0005](docs/adr/0005-framework-first.md).
<!-- fim: estrutura-kit -->

**Não criar** quando o framework oferece: relógio ou gerador de ID; tipo `Result` (salvo se for o idioma da linguagem); publicador de eventos ou outbox; interfaces de autorização ou de flags (use {{AGENTE: mecanismos de autorização e de feature flags do framework}} direto); builders de teste quando há factories; wrappers de cliente HTTP.

### Versões e sintaxe atual

A versão em uso está no lockfile. Antes de escrever, consulte a documentação **dessa** versão: agentes tendem a escrever a sintaxe do treinamento.
- Dependência nova entra na versão estável mais recente compatível, depois de [perguntar](AGENTS.md#perguntar-antes).
- Código novo usa a forma recomendada para a versão instalada; nada de API obsoleta (*deprecated*). Código antigo migra quando a demanda o toca ou num PR de refatoração próprio.

| Forma antiga ainda compatível | Forma atual preferida |
|---|---|
| {{AGENTE: EXEMPLOS_DA_STACK, cada linha confirmada na documentação oficial}} | |

### Separação de responsabilidades

Cada papel tem um motivo para mudar, qualquer que seja o nome que o projeto lhe dá:
- **a entrada** (rota, controller, comando de terminal) só recebe e delega;
- **a validação de forma** (presença, tipo, tamanho) fica na borda;
- **o caso de uso** (handler, action, service de aplicação) orquestra, sem regra de negócio própria;
- **a regra de negócio** fica no domínio: entidade, value object e agregado com comportamento;
- **a integração externa** (terceiro, LLM, SDK) fica atrás de uma fronteira que traduz o modelo externo.
<!-- se: backend -->
- **a persistência** fica num lugar só: ORM e SQL não vazam para entrada, caso de uso nem domínio;
- **a transação** abre e fecha no caso de uso.
<!-- fim: backend -->
<!-- se: frontend -->
- **a tela** apresenta e coleta; a regra de negócio é do backend ([FRONTEND.md](docs/FRONTEND.md)).
<!-- fim: frontend -->

Onde cada papel fica neste projeto, com os sinais de violação: [ARCHITECTURE.md §4.1](ARCHITECTURE.md#41-responsabilidades).

### API pública de módulo

Outro módulo fala com um módulo só pela porta pública dele (facade ou equivalente), que delega e não tem regra. Nunca importe o interior de outro módulo nem leia as tabelas dele ([fronteiras](ARCHITECTURE.md#6-comunicação-entre-módulos)).

### Orientação a objetos

Código de aplicação e de domínio fica em classes: cada regra tem um dono com nome e as dependências aparecem no construtor. **Funções de topo só na borda do framework:** inicialização, configuração, rotas declaradas como funções, fábricas de dados de teste e APIs que exigem função (callback, tool de SDK de IA).
<!-- se: frontend -->
Componente e hook de UI são funções quando o framework de UI exige; a lógica independente dele fica em classes.
<!-- fim: frontend -->

O que seria função utilitária vira value object, método do agregado, serviço de domínio injetado ou fábrica estática só para criar e reconstituir (`Pedido.criar(...)`). **Policy:** método do agregado se depende só dele (`pedido.podeSerCancelado()`); senão, classe injetada (`PedidoPolicy`). Nada de classe só com métodos estáticos nem objeto literal como namespace.

### Nomes

Tipos em português, com sufixo técnico em inglês e sem preposição nem artigo (`PedidoId`, `ItemPedido`, `ConsultaCreditoPort`), com os termos da [linguagem ubíqua](docs/DOMAIN.md#4-linguagem-ubíqua). Sufixos do projeto: [CODEBASE_MAP.md](CODEBASE_MAP.md#convenção-de-nomes); variáveis: §2.

### Verificações, exemplos e API do framework

- **Os exemplos dos documentos passam nas verificações:** exemplo recusado é defeito do documento, não da configuração.
- **A API do framework vence a regra de estilo.** Nome exigido por uma biblioteca é permitido; se o lint recusa, a exceção vai na configuração com escopo restrito, depois de [perguntar](AGENTS.md#perguntar-antes).
<!-- se: backend -->
- **Trocar a API do ORM por SQL cru para escapar de uma regra é contornar a regra** ([Nunca](AGENTS.md#nunca)). SQL cru na persistência só quando o ORM não expressa a consulta, com o motivo em comentário.
<!-- fim: backend -->

### Simplicidade primeiro
- **Abstração nova só com dois usos reais ou uma fronteira externa.** Duplicação de *conhecimento* é bug; código parecido por coincidência, não. Regra de três: abstraia na terceira repetição ([passo comum](#passo-comum-a-vários-casos-de-uso)).
- **Um conceito de negócio, uma definição** ("estoque disponível"), com nome, no domínio ou num método de leitura. Antes de escrever uma condição de negócio, busque o conceito em [docs/DOMAIN.md](docs/DOMAIN.md#4-linguagem-ubíqua). Por quê: com duas definições, o registro aparece "disponível" numa tela e indisponível na outra.
- **Uma implementação viva por conceito.** A nova substitui a antiga no mesmo ciclo, ou a antiga vira dívida em [ARCHITECTURE.md §11](ARCHITECTURE.md#11-riscos-e-débitos-conhecidos). Nada de `New` ou `_NEW`.
- **Uma forma por tipo de operação**, a do [exemplo de referência](CODEBASE_MAP.md#exemplos-de-referência). Camada ou padrão só quando o problema aparece.
- **Falhar cedo nas pré-condições** (existe, tem permissão, o estado permite); **acumular nas regras independentes**, que voltam juntas.
- Verbos com contrato de retorno: [CODEBASE_MAP.md](CODEBASE_MAP.md#verbos-com-contrato-de-retorno).

### Um conceito, uma definição: como reutilizar

O segundo caso de uso chama a mesma definição e cita o mesmo nome de regra, em vez de reescrever o conceito:

```
DisponibilidadeEstoque(saldo, reservados):          // a definição única
  REGRA = "estoqueSuficiente"
  atende(quantidade): this.saldo - this.reservados >= quantidade

// em criar pedido e em confirmar venda: a mesma chamada, o mesmo nome
se não disponibilidadeEstoque.atende(item.quantidade):
  violacoes.adicionar(Violacao(DisponibilidadeEstoque.REGRA, "restam 3 unidades; o pedido pede 5"))
```

A mensagem varia; o nome e a definição, não. Conceito que é consulta é **um** método de leitura; variantes (`listar…`, `contar…`) compartilham o critério. **Sinais de violação:** condição de negócio montada no caso de uso ou na reação a evento; o mesmo conceito com nomes de regra diferentes.

### Um conceito em memória e na consulta

O predicado em memória e o critério de consulta leem a definição do mesmo lugar: conjunto de estados com nome no enum (`PedidoStatusEnum.ativos`) ou, para conceito mais rico (estado + prazo), uma specification com `satisfeitaPor(entidade, agora)` e `criterio(agora)` no mesmo arquivo e com o mesmo teste de casos. Definição que depende do tempo recebe `agora` do relógio do framework. Por quê: com o predicado copiado, a mudança de `<` para `<=` chega a um lado só.
<!-- se: backend -->
A persistência recebe o critério pronto e só o traduz para o ORM; comparar data com `agora` na persistência é sinal de violação.
<!-- fim: backend -->

### Passo comum a vários casos de uso

Na terceira repetição de um sub-roteiro, ou quando ele passa o [limite do papel](#tamanho-e-complexidade-por-papel), a regra do passo vai para o domínio e a sequência continua visível no caso de uso. Nunca um service que esconde a sequência de vários casos de uso.

Ordem de extração: (1) a regra vai para agregado, VO ou serviço de domínio, que recebe os dados prontos e devolve a decisão; (2) "depois de X, também Y", atômico: um método com o nome do conceito, sem regra; (3) não atômico: reação a evento, com entrega garantida se gravar estado de negócio.
<!-- se: backend -->
**Entrada do domínio montada de várias leituras** (já na segunda repetição): um método da persistência dona, com o nome do conceito, monta o objeto **sem decidir nada**. O dado de outro módulo é lido no caso de uso, pela porta pública dele, e passado como argumento; a persistência nunca chama outra persistência nem outro módulo.

```
saldoEstoque = estoqueApi.obterSaldo(produtoId)
disponibilidadeEstoque = pedidoRepository.obterDisponibilidadeEstoque(produtoId, saldoEstoque)
pedido.confirmar(disponibilidadeEstoque)   // a regra no domínio
```
<!-- fim: backend -->
<!-- se: estrutura-projeto -->
{{AGENTE: onde o projeto põe um passo repetido entre casos de uso, com 1 exemplo `arquivo`}}
<!-- fim: estrutura-projeto -->

**Preparar antes de implementar:** se a demanda é difícil no código atual, o primeiro passo é a extração sem mudar comportamento, em commit próprio. **Cada passo do plano é uma fatia completa**, de ponta a ponta e com um teste passando; nunca uma camada.

### Interfaces só quando há motivo

**Usa interface:** fronteira externa (lenta, instável ou cara em teste; LLM), mais de uma implementação real, ou teste que não tem outro jeito de trocar a dependência. **Classe concreta:** caso de uso, serviço de domínio, policy, porta pública de módulo com uma implementação; recursos do framework (autorização, flags, cache, filas, HTTP, data/hora, IDs) usados direto, com os fakes dele nos testes.
<!-- se: backend -->
Persistência com um banco só e mapper também são classes concretas.
<!-- fim: backend -->
- **Inversão de dependência só nas fronteiras externas;** tudo vem do container, sem `new` de dependência no caso de uso. **Teste da remoção:** se apagar a interface e a complexidade sumir junto, era só passagem.
- Toda implementação de uma fronteira, inclusive o fake, passa na mesma suíte de contrato.
- "Não precisa de interface" **não** autoriza chamar sistema externo, LLM ou SDK direto do caso de uso.
<!-- se: estrutura-kit -->
Na estrutura do kit: fronteira externa é `Port` em `ports/` com `Client` em `clients/`; a porta pública do módulo é `<Modulo>Api`, implementada pela `<Modulo>Facade`; repository é classe concreta. Decisão na [ADR-0004](docs/adr/0004-interfaces-so-em-fronteiras.md).
<!-- fim: estrutura-kit -->

## 2. Modelagem e tipos

- **Value objects contra primitivos** (`Dinheiro`, `PedidoId`), validados no construtor: VO existente é sempre válido.
- **A regra que tem VO fica só no VO;** a validação de entrada checa só a forma. O VO rejeita com a exceção de entrada inválida e o `campo` (400). Erros de vários VOs falham um por vez, salvo se a demanda pedir todos juntos.
- **Estados ilegais irrepresentáveis:** enums e tabela de transições, não flags soltas; conjuntos de estados com nome (`STATUS_QUE_PERMITEM_EDICAO`). **Regra como predicado com nome** no objeto que tem os dados (`pedido.podeSerCancelado()`, não `status == 3 && ...` no caso de uso); nenhum literal mágico.
- **Imutáveis:** VOs, DTOs, comandos, consultas e eventos; agregados mudam só por métodos que garantem invariantes.
- **Entidade com comportamento;** agregados pequenos, referenciando outros por ID; `if` de regra de negócio no caso de uso é barrado na revisão.
<!-- se: backend -->
- **Entidade sem persistência:** não consulta nem grava; a transação é do caso de uso ([ARCHITECTURE.md §5.1](ARCHITECTURE.md#51-comando-escrita)).
<!-- fim: backend -->
- **Um objeto, um nome, que diz o que ele é.** Dependência injetada = nome do tipo em camelCase, privada e somente leitura (`pedidoPolicy`). Campo e getter com o nome do conceito, sem sinônimo (`status`/`situacao`); variável local = conceito (`pedido`, `itensDisponiveis`), sem abreviação (`repo`) nem genérico (`data`, `result`, `item`).

## 3. Funções e classes

- **O método principal é um índice:** pré-condições primeiro, com retorno antecipado; depois cada passo é uma chamada com nome de intenção. Comentário separando "partes" pede métodos.
<!-- se: estrutura-kit -->
- O handler segue a forma de [ARCHITECTURE.md §5.1](ARCHITECTURE.md#51-comando-escrita).
<!-- fim: estrutura-kit -->
- **Nenhuma leitura dentro de argumento:** não `confirmar(obterSaldo(obterPedido(id).produtoId))`; cada leitura vira variável com o nome do conceito.
- **Dependências explícitas** pelo construtor; nada de service locator, despacho por string ou método mágico.
- Até ~3 parâmetros; sem booleano que muda o comportamento; data/hora, aleatoriedade e IDs vêm da linguagem, do framework ou do ORM.

### Tamanho e complexidade por papel

O número é gatilho para olhar, não meta. No caso de uso pesam linhas (60 linhas quase sem `if` escondem montagem repetida ou regra do domínio); no domínio, ramificação. Extrair só para caber (`parte1`) é pior: extraia por intenção.

| Papel | Limite verificado (erro) | Referência |
|---|---|---|
| Caso de uso (método principal) | 40 linhas de código, aninhamento 2, complexidade 6 | ~25–30 linhas |
| Domínio | complexidade 10, aninhamento 3; sem limite de linhas | — |
| Entrada | como o domínio; sem regra de negócio | ~15 linhas |
<!-- se: backend -->
| Persistência | como o domínio; sem regra de negócio | — |
<!-- fim: backend -->
<!-- se: frontend -->
| Componente de tela | como o domínio; sem regra de negócio | uma responsabilidade visual |
<!-- fim: frontend -->
| Classe | até 6 dependências no construtor | ~5; mais de ~200 linhas é alerta |

Testes não têm limite: um comportamento por teste. Use a regra pronta do lint, ajustando à métrica dela. **Exceção:** pergunte antes; aprovada, desative só naquela função, com o motivo ao lado. "Não deu para extrair" não é motivo.

## 4. Erros

| Situação | Como tratar |
|---|---|
| Regra de negócio violada | exceção de domínio de uma categoria abaixo, convertida pelo tratamento global |
| Desfecho que não é falha ("vai para análise") | resultado com nome, não exceção |
| Falha de infraestrutura | exceção técnica, com retry e timeout do cliente ou da fila |
| Bug (estado impossível) | deixar estourar: é capturado, logado e alertado |

**Categorias fechadas:** toda exceção de domínio tem uma, e cada uma tem um status.

| Categoria | Exemplo | Status |
|---|---|---|
| Não encontrado (ou sem permissão para saber que existe) | `PedidoNaoEncontradoException` | 404 |
| Sem permissão | `CancelamentoPedidoNaoPermitidoException` | 403 |
| Entrada inválida | validação de forma, com `errors` por campo | 400 |
| Estado não permite / conflito | `PedidoJaPagoException`; versão desatualizada | 409 |
| Regra violada | a exceção base carrega a lista `violacoes` | 422 |

**409 × 422:** conflita com o que existe ou com o estado atual → 409; os dados enviados violam uma regra, independentemente do que existe → 422.

- **Mensagem** com o que aconteceu, os valores e o que fazer ("o pedido 123 já foi pago; abra uma devolução"); nunca genérica, stack trace ou SQL.
- **`violacoes`:** `{ regra, mensagem, campo? }`, separadas do `errors` da validação de entrada. **`regra`** em camelCase afirmativo (`totalIgualSomaItens`), igual à tabela de [invariantes](docs/DOMAIN.md#5-agregados-e-invariantes) e ao predicado; nunca código numérico.
- O nome do tipo do erro vem da classe; subclasses não o repetem em string.
- Nunca engula erro (`catch` vazio, só log), nem o converta em vazio (`[]`, `false`, `null`), nem siga gravando depois de uma falha. Erro → resposta fica no tratamento global, não em `try/catch` por caso de uso.
<!-- se: api -->

**Na API HTTP:** [Problem Details (RFC 9457)](https://www.rfc-editor.org/rfc/rfc9457), com `violacoes` e `errors` como extensões:

```json
{
  "type": "https://{{USUARIO: dominio}}/erros/total-diferente-soma-itens",
  "title": "Total diferente da soma dos itens",
  "status": 422,
  "detail": "O pedido 123 tem total R$ 120,00, mas os itens somam R$ 100,00.",
  "violacoes": [{ "regra": "totalIgualSomaItens", "mensagem": "…" }]
}
```

O `type` termina no nome da exceção em kebab-case, sem `Exception`, derivado num único lugar. Além das categorias: 401 não autenticado, 429 + `Retry-After`, 503 dependência externa fora.
<!-- fim: api -->

## 5. Comentários

Comente o **porquê**, citando a fonte (issue, ADR, regra em [docs/DOMAIN.md](docs/DOMAIN.md)). Comentário falso ou desatualizado é defeito. Sem código comentado; `TODO` só com issue (`TODO(#123)`).

## 6. Padrões e anti-padrões

- **Variação só de dados é tabela declarativa;** de comportamento, estratégia injetada, não `if/switch` crescente.
<!-- se: backend -->
- **Persistência com nome de negócio:** o método revela todo filtro (`listarPendentesPorPedido`, nunca `listarTodos` que filtra); nada de repository genérico; não abre nem confirma transação.
- **Transação e concorrência:** uma por caso de uso, à vista nele, sem aninhar; validar antes da primeira escrita; efeito externo (evento, HTTP, e-mail, fila) só depois do commit; limite contado e fato gravado por um caso de uso e lido como regra por outro (*write skew*) usam a mesma trava ou restrição, com teste de concorrência ([ARCHITECTURE.md §5.1](ARCHITECTURE.md#51-comando-escrita)).
<!-- fim: backend -->

Anti-padrões: singleton com estado global; "Manager"/"Helper"/"Utils"; caso de uso que repassa a um service com todos os casos de uso; fachada sobre fachada; gravar o agregado numa reação a evento; estado de processo em sessão; gerações paralelas do mesmo conceito; herança para reaproveitar fluxo.

## 7. O que vale refatorar

Refatoração é passo separado, com testes verdes antes e depois. Proposta **forte** com três sinais, **vale explorar** com dois, **especulativa** com um:
- **a área muda com frequência** ({{AGENTE: comando, ex.: `git log --since=6.months --format= --name-only | sort | uniq -c`}});
- **houve atrito real na tarefa atual** (vários arquivos, montagem copiada); cite onde;
- **passa no teste da deleção:** com a classe apagada, a complexidade se espalharia pelos chamadores? Vale fortalecer; se sumiria, proponha removê-la (não vale para entrada e caso de uso, finos de propósito).

Refatoração fora do pedido é [pergunta](AGENTS.md#perguntar-antes), salvo a preparação que a demanda exige. Migrar o padrão do projeto para um princípio também é pergunta. Contrariar uma ADR aceita exige a ADR substituta.

## 8. Regras para código escrito por agentes de IA

Complementam [Sempre](AGENTS.md#sempre) e [Nunca](AGENTS.md#nunca).

- **Siga o exemplo de referência.** Antes de escrever, encontre **dois** exemplos do mesmo tipo no mesmo contexto e imite; não misture duas formas no mesmo módulo. Com duas formas, siga o [exemplo de referência](CODEBASE_MAP.md#exemplos-de-referência). Documento e vizinho divergem: siga o vizinho e aponte no PR. Vizinho contraria um princípio: siga o vizinho, registre em [ARCHITECTURE.md §11](ARCHITECTURE.md#11-riscos-e-débitos-conhecidos) e pergunte se o dev quer migrar.
- **Nada de experimento ou código morto:** rascunho, alternativa comentada e caso de uso que só um teste liga saem.
- **Diffs pequenos:** uma intenção por mudança; trabalho novo acrescenta arquivos em vez de ramificar código compartilhado; não reformate nem renomeie fora da tarefa.
- **Teste primeiro**, falhando pelo motivo certo ([TESTING.md](TESTING.md#4-escrevendo-bons-testes)).
- Revisão humana obrigatória para segurança, migrações, contratos públicos e CI/deploy.
- **Pare e pergunte** quando a tarefa for ambígua, exigir decisão de produto ou cair em [Perguntar antes](AGENTS.md#perguntar-antes). Rodadas de perguntas:
  - **Por dependência:** cada rodada leva só perguntas cujos pré-requisitos já foram respondidos.
  - **Cenário concreto de borda em cada pergunta**, redigida para que "sim" aceite a recomendação: "Um item é removido do pedido enquanto o pagamento é confirmado: cobramos o total recalculado? Recomendo que sim."
  - **Suposição não substitui pergunta:** regra com mais de uma resposta defensável é pergunta; suposição só para detalhe óbvio ou quando o dev delegou, registrada com as palavras dele.
  - **Termina quando nenhuma regra de negócio ficou presumida em silêncio:** cada uma perguntada ou registrada como suposição, em [docs/DOMAIN.md](docs/DOMAIN.md) e na tabela de critérios do design doc (sem ele, no relato).
