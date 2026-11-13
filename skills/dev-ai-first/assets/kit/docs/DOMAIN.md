# Domínio

> Modelo de domínio de {{AGENTE: NOME_DO_PROJETO}}. Fonte de verdade para nomes no código: termo que não está aqui é combinado com o time e adicionado antes de usar.

## 1. Visão do negócio

{{USUARIO: parágrafo curto: quem usa, que problema o sistema resolve, como gera valor}}

## 2. Subdomínios

| Subdomínio | Tipo | Por quê |
|---|---|---|
| {{USUARIO: subdomínio}} | {{USUARIO: core / supporting / generic}} | {{USUARIO: por quê}} |

Design mais cuidadoso e testes mais rigorosos concentram-se no **core**; generic se compra ou usa pronto.

## 3. Bounded contexts

| Contexto | Módulo | Responsabilidade | Relação com outros contextos | Dono |
|---|---|---|---|---|
| {{AGENTE: Vendas}} | `{{AGENTE: vendas}}` | {{AGENTE: responsabilidade}} | {{AGENTE: ex.: publica eventos que estoque consome}} | {{USUARIO: time/pessoa}} |

## 4. Linguagem ubíqua

Um termo significa uma coisa só **dentro do seu contexto**; se outro contexto usa o mesmo termo com outro sentido, registre os dois.

**Um conceito, um nome.** "Nomes recusados" lista sinônimos e grafias que não entram no código nem nos documentos. Por quê: quem busca um nome não acha o outro, e o sinônimo vira um segundo conceito sem ninguém decidir.

| Termo | Contexto | Definição | Nome no código | Nomes recusados | Não confundir com |
|---|---|---|---|---|---|
| {{AGENTE: Pedido}} | {{AGENTE: Vendas}} | {{USUARIO: definição em uma frase}} | `Pedido` | {{USUARIO: sinônimos descartados}} | |
| {{AGENTE: Item do pedido}} | {{AGENTE: Vendas}} | {{USUARIO: definição}} | `ItemPedido` ([convenção de nomes](../CODEBASE_MAP.md#convenção-de-nomes)) | `PedidoItem`, `ItemDoPedido` | |

## 5. Agregados e invariantes

Cada invariante tem um **nome de regra** em camelCase afirmativo, dizendo o que exige (`totalIgualSomaItens`). O mesmo nome é o `regra` de `violacoes[]` no erro ([formato](../CODING_GUIDELINES.md#4-erros)), o predicado que a protege (ou a forma afirmativa dele) e o termo citado no teste que a cobre.
- Cada invariante e cada transição tem teste.
- Cada invariante e cada conceito com regra ("disponível", "bloqueado") apontam para a **única** definição no código; ao estender a regra, busque pelo nome e mude nesse lugar.
- Regra ainda não implementada é marcada *não implementada*, nunca descrita como cumprida.

### {{AGENTE: AgregadoNome}} ({{AGENTE: contexto}})
- **Raiz:** `{{AGENTE: Pedido}}` · **Contém:** {{AGENTE: entidades e VOs internos, ex.: ItemPedido}}
- **Invariantes:**

  | Regra (id no código) | Invariante | Definição no código |
  |---|---|---|
  | `{{AGENTE: totalIgualSomaItens}}` | {{USUARIO: ex.: o total do pedido é a soma dos itens}} | {{AGENTE: Pedido.total()}} |
  | `{{AGENTE: nomeDaRegra}}` | {{USUARIO: invariante}} *(não implementada)* | |

<!-- se: estados -->
- **Ciclo de vida:** a fonte executável é a tabela de transições em `{{AGENTE: caminho do enum de estado}}` ([ARCHITECTURE.md](../ARCHITECTURE.md#54-estados-e-transições)); o diagrama é a leitura humana e, se divergir, é corrigido.
  ```mermaid
  stateDiagram-v2
    [*] --> Pendente
    Pendente --> Aprovado: aprovar
    Pendente --> Cancelado: cancelar
  ```
- **Histórico:** {{AGENTE: onde fica; cada transição grava quem, quando, origem, destino e motivo}}
<!-- fim: estados -->
<!-- se: eventos -->
- **Eventos emitidos:** {{AGENTE: ex.: PedidoAprovadoEvent}}
<!-- fim: eventos -->

## 6. Regras que não cabem em um agregado

| Regra (id no código) | Regra | Onde vive | Motivo |
|---|---|---|---|
| `{{AGENTE: nomeDaRegra}}` | {{USUARIO: ex.: pedido só é aprovado com estoque para todos os itens}} | {{AGENTE: serviço de domínio}} | envolve vários agregados |

## 7. Ao modelar uma regra nova

- **Desafie os termos** contra o glossário: "você disse X, mas o glossário define Y; são a mesma coisa?". Termo novo ou ambíguo é resolvido aqui antes de virar código.
- **Invente cenários de borda** (valor zero, limite exato, operação repetida, estado intermediário, outro tenant) e confira cada um com o código e os testes antes de aceitar a regra.
