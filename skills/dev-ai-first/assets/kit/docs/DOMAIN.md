# Domínio

> Modelo de domínio de {{AGENTE: NOME_DO_PROJETO}} segundo o DDD. Fonte de verdade para nomes no código: se um termo não está aqui, combine com o time e adicione antes de usar.

## 1. Visão do negócio

{{USUARIO: Parágrafo curto: quem são os usuários, que problema o sistema resolve, como gera valor.}}

## 2. Subdomínios

| Subdomínio | Tipo | Por quê | Estratégia |
|---|---|---|---|
| {{USUARIO: ex.: Recomendação}} | **core** | diferencial competitivo | construir com o melhor modelo de domínio e mais testes |
| {{USUARIO: ex.: Faturamento}} | supporting | necessário, não diferencia | construir de forma simples |
| {{USUARIO: ex.: Autenticação}} | generic | problema resolvido pelo mercado | comprar/usar pronto |

Investimento de design (DDD tático completo, testes mais rigorosos) concentra-se no **core**.

## 3. Bounded contexts e mapa de contextos

```mermaid
flowchart LR
  A[{{AGENTE: Contexto A}}] -- "eventos (published language)" --> B[{{AGENTE: Contexto B}}]
  B -- "customer / supplier" --> C[{{AGENTE: Contexto C}}]
  C -- "anticorruption layer" --> EXT[(Sistema externo)]
  A -. "shared kernel: tipos de identidade" .- C
```

| Contexto | Módulo | Responsabilidade | Dono |
|---|---|---|---|
| {{AGENTE: Contexto A}} | `{{AGENTE: modulo-a}}` | {{AGENTE: responsabilidade}} | {{USUARIO: time/pessoa}} |

Relações possíveis: partnership, shared kernel, customer/supplier, conformist, anticorruption layer, open host service, published language, separate ways.

## 4. Linguagem ubíqua

Um termo significa uma única coisa **dentro do seu contexto**. O mesmo termo em outro contexto pode significar outra coisa; registre os dois.

**Um conceito, um nome.** A coluna "Nomes recusados" lista sinônimos e grafias que não entram no código nem nos documentos para aquele termo. Por quê: quem busca um nome não acha o outro, e o sinônimo vira um segundo conceito sem ninguém decidir. Opcional: o `{{AGENTE: CMD_CHECK}}` pode buscar os nomes recusados no código.

| Termo | Contexto | Definição | Nome no código | Nomes recusados | Não confundir com |
|---|---|---|---|---|---|
| {{AGENTE: Pedido}} | {{AGENTE: Vendas}} | {{USUARIO: solicitação de compra de um cliente, antes da aprovação}} | `Pedido` | {{USUARIO: ex.: `Encomenda`, `Ordem`}} | {{AGENTE: Ordem de separação (Estoque)}} |
| {{AGENTE: Item do pedido}} | {{AGENTE: Vendas}} | {{USUARIO: produto e quantidade dentro de um pedido}} | `ItemPedido` (sem preposição; ver [convenção de nomes](../CODEBASE_MAP.md#convenção-de-nomes)) | `PedidoItem`, `ItemDoPedido` | |
| {{AGENTE: Status do pedido}} | {{AGENTE: Vendas}} | {{USUARIO: etapa do ciclo de vida do pedido}} | `status` (`PedidoStatusEnum`) | `situacao`, `estado` | |

## 5. Agregados e invariantes

Para cada agregado: o que ele protege e quais regras sempre valem. Cada invariante tem um **nome de regra** em camelCase afirmativo, dizendo o que ela exige (`limiteCreditoRespeitado`, `clienteSemBloqueio`): é o `regra` de `violacoes[]` na resposta 422 ([formato](API_GUIDELINES.md#erros)), o nome do predicado que a protege (ou a forma afirmativa dele: `excedeLimite()` → `limiteCreditoRespeitado`) e o termo citado no teste que a cobre. Cada invariante e cada transição tem teste. Regra ainda não implementada é marcada como tal (*não implementada*), nunca descrita como se o código já a cumprisse. Cada invariante e cada conceito com regra ("disponível", "bloqueado") apontam para a **única** definição no código (predicado, método de VO ou de serviço de domínio, ou método de leitura do repository); ao estender uma regra, busque pelo nome da regra e mude nesse lugar.

### {{AGENTE: AgregadoNome}} ({{AGENTE: contexto}})
- **Raiz:** `{{AGENTE: Entidade}}`
- **Contém:** {{AGENTE: entidades e VOs internos}}
- **Invariantes:**

  | Regra (id no código) | Invariante | Definição no código |
  |---|---|---|
  | `{{AGENTE: totalIgualSomaItens}}` | {{USUARIO: ex.: o total do pedido é a soma dos itens menos descontos}} | {{AGENTE: Pedido.total()}} |
  | `{{AGENTE: itensSomenteAntesAprovacao}}` | {{USUARIO: ex.: pedido aprovado não pode receber novos itens}} | {{AGENTE: Pedido.adicionarItem()}} |
  | `{{AGENTE: faturadoSemCancelamento}}` | {{USUARIO: ex.: pedido faturado não pode ser cancelado}} *(não implementada)* | |

- **Ciclo de vida:** o diagrama abaixo é a leitura humana; a fonte executável é a tabela de transições em `{{AGENTE: caminho do enum de estado}}` ([ARCHITECTURE.md](../ARCHITECTURE.md#54-estados-e-transições)). Se divergirem, vale a tabela e o diagrama é corrigido.
  ```mermaid
  stateDiagram-v2
    [*] --> Rascunho
    Rascunho --> Pendente: enviar
    Pendente --> Aprovado: aprovar
    Pendente --> Recusado: recusar
    Aprovado --> [*]
    Recusado --> [*]
  ```
- **Histórico:** {{AGENTE: onde fica; cada transição grava quem, quando, origem, destino e motivo}}
- **Eventos emitidos:** {{AGENTE: PedidoEnviadoEvent, PedidoAprovadoEvent, PedidoRecusadoEvent}}

## 6. Regras de negócio que não cabem em um agregado

| Regra (id no código) | Regra | Onde vive | Motivo |
|---|---|---|---|
| `{{AGENTE: limiteCreditoRespeitado}}` | {{USUARIO: ex.: limite de crédito considera pedidos abertos de todos os canais}} | serviço de domínio `{{AGENTE: AnaliseCredito}}` | envolve vários agregados |

## 7. Como descobrimos este modelo

- Sessões de **event storming**: {{USUARIO: links/fotos}}
- **Domain storytelling**: {{USUARIO: links}}
- Atualizar este documento após cada sessão de modelagem.

Ao modelar ou aceitar uma regra nova (pessoa ou agente):
- **Desafie os termos** contra a linguagem ubíqua: "você disse X, mas o glossário define Y; são a mesma coisa?". Termo novo ou ambíguo é resolvido aqui antes de virar código.
- **Invente cenários de borda** (valor zero, limite exato, operação repetida, estado intermediário, outro tenant) e confira cada um com o código e os testes existentes antes de aceitar a regra.
