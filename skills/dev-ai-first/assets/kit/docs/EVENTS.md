# Eventos

> Evento publicado é contrato: outros módulos dependem dele. Eventos, listeners e filas usam {{AGENTE: MECANISMO_DE_COMANDOS_E_EVENTOS_DO_FRAMEWORK}} e {{AGENTE: MECANISMO_DE_FILAS_DO_FRAMEWORK}}, como a documentação do framework mostra.
<!-- se: estrutura-kit -->
> Decisão: [ADR-0003](adr/0003-eventos-com-recursos-do-framework.md).
<!-- fim: estrutura-kit -->

Evento de domínio fica no módulo e muda livremente; de integração (entre módulos) é público, versionado e não expõe a estrutura do agregado.

## Convenções

- **Passo do caso de uso × reação a um fato.** O que faz parte da consistência da operação (agregado, histórico, outro registro do mesmo módulo) é passo explícito do caso de uso, na transação, e não vira evento. Evento é para **reação** posterior, depois do commit: "o que é atômico?" e "o que vem depois?" se respondem lendo o caso de uso e o mapa de reações.
- **Listener não grava nem muda o agregado que disparou o evento.** Se precisa, é passo do caso de uso.
- **Mapa evento → reações num só lugar:** o registro do módulo (ou a marcação, no evento, das reações depois do commit que ele aciona).
- **Assinatura `<fato>.<reação>`** (`pedidoAprovado.reservarEstoque`); o contrato assíncrono fica em arquivo próprio, tipado (enum como enum, não `string`).
- **Nome no passado** com sufixo `Event` (`PedidoAprovadoEvent`, nunca `AprovarPedido`); para fora do módulo, fatos, não ordens.
- **Carga mínima:** IDs e o que o consumidor buscaria em seguida; imutável, sem comportamento nem dado pessoal desnecessário.
- **Com broker externo ou outro sistema:** envelope com `id` (idempotência), `type` (`vendas.pedido-aprovado`), `version`, `occurredAt` e `data`. Dentro da aplicação, a classe do evento é o contrato.

## Garantias

| Garantia | Como |
|---|---|
| Consistência com o estado | despacho **depois do commit** pelo framework ({{AGENTE: RECURSO_DE_DESPACHO_APOS_COMMIT}}); fila no banco grava o job na mesma transação. Outbox própria só por ADR |
| Entrega e duplicatas | pelo menos uma vez; consumidor idempotente (checa o estado antes de agir) |
| Ordem | só por chave (ex.: `pedidoId`), nunca global |
| Falha no consumidor | retry com backoff da fila; após o limite de tentativas (a definir; até lá, o padrão do framework), jobs falhos com alerta |

Versões: campo opcional novo mantém a versão; remover, renomear ou mudar sentido cria a 2, publicada junto da 1 até todos migrarem.

## Reação que grava estado × reação que só avisa

| Reação | Exemplo | Como roda | Testes |
|---|---|---|---|
| **Grava estado de negócio** | liberar o próximo pedido da fila de espera, recalcular estoque | listener enfileirado com tentativas, backoff e idempotência; **ou** job agendado de reconciliação que refaz o que faltou | mesma mensagem duas vezes → um efeito; primeira tentativa falha → a seguinte conclui |
| **Só avisa** | log, notificação best-effort, métrica | em processo, depois do commit | o despacho, com o fake de eventos do framework |

Por quê: se a reação em processo falha, o caso de uso já confirmou e ninguém tenta de novo; perder estado de negócio deixa o sistema inconsistente em silêncio.

**Sinal de violação:** listener em processo (sem fila nem retry) que grava estado, sem reconciliação registrada.

## Sagas

| Saga | Tipo | Passos | Compensações |
|---|---|---|---|
| {{AGENTE: ex.: fechar pedido}} | {{AGENTE: coreografia ou orquestração}} | {{AGENTE: PedidoCriadoEvent → EstoqueReservadoEvent → PagamentoAprovadoEvent}} | {{AGENTE: liberar estoque se o pagamento falhar}} |

## Catálogo

| Evento | Versão | Produtor | Consumidores | Quando | Schema |
|---|---|---|---|---|---|
| `{{AGENTE: contexto.evento}}` | 1 | `{{AGENTE: modulo}}` | `{{AGENTE: modulo}}` | {{AGENTE: condição}} | {{AGENTE: link}} |

## Como adicionar um evento

1. Confirme o nome na linguagem ubíqua ([DOMAIN.md](DOMAIN.md#4-linguagem-ubíqua)).
2. Defina o schema de `data` e registre no catálogo.
3. Crie a classe do evento no formato do framework; o agregado o registra e o caso de uso o despacha depois do commit.
4. Testes: unitário (o agregado registra o evento) e de integração do caso de uso (despacho, com o fake de eventos).
5. No consumidor: reação idempotente, registrada no mapa, enfileirada com retry se grava estado ([critério](#reação-que-grava-estado--reação-que-só-avisa)), com teste de entrega duplicada. O listener delega ao caso de uso; não acessa dados nem tem regra própria.
