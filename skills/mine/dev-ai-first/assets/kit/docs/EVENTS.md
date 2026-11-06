# Eventos

> Convenções e catálogo de eventos. Evento publicado é contrato público: outros módulos (e talvez outros sistemas) dependem dele. Eventos, listeners e filas usam {{AGENTE: MECANISMO_DE_COMANDOS_E_EVENTOS_DO_FRAMEWORK}} e {{AGENTE: MECANISMO_DE_FILAS_DO_FRAMEWORK}}, como a documentação do framework mostra ([ADR-0003](adr/0003-eventos-com-recursos-do-framework.md)).

## Tipos de evento

| Tipo | Escopo | Exemplo | Contrato |
|---|---|---|---|
| **Evento de domínio** | dentro do módulo | `ItemPedidoAdicionadoEvent` | interno, pode mudar livremente |
| **Evento de integração** | entre módulos ou sistemas | `PedidoAprovadoEvent` | público, versionado, mudança com compatibilidade |

Um evento de domínio pode ser traduzido para um evento de integração com menos detalhes. Não exponha a estrutura interna do agregado.

## Convenções

- **Nome no passado** (substantivo + particípio), em linguagem ubíqua, com sufixo `Event`: `PedidoAprovadoEvent`, nunca `AprovarPedido` (isso é comando: `AprovarPedidoCommand`). O `type` do envelope usa a forma kebab-case sem sufixo.
- **Passo do caso de uso × reação a um fato.** O que faz parte da consistência da operação (gravar o agregado, histórico, caixa de entrada, outro registro do mesmo módulo) é passo explícito do handler, dentro da transação, e não vira evento. Evento é para **reação** posterior, despachada após o commit; se a reação grava estado de negócio, ela precisa de entrega garantida ([critério](#reação-que-grava-estado--reação-que-só-avisa)). Assim "o que é atômico?" e "o que acontece depois?" se respondem lendo o caso de uso e o mapa abaixo ([ARCHITECTURE.md](../ARCHITECTURE.md#53-eventos-passo-do-caso-de-uso--reação-a-um-fato)).
- **Listener não grava nem muda o agregado que disparou o evento.** Se precisa, é passo do caso de uso.
- **Fatos, não ordens, para fora do módulo.** O publicador não sabe quem consome em outros módulos nem o que farão.
- **Mapa evento → reações num só lugar:** o registro do módulo lista, para cada evento, as reações. Marcar no evento as capacidades que ele aciona é aceito como forma desse registro, só para reações após o commit.
- **Assinatura `<fato>.<reação>`:** cada reação registrada tem nome que junta o fato e o que faz (`pedidoAprovado.reservarEstoque`), e o contrato assíncrono fica em arquivo próprio, tipado (enums como enums, não `string`).
- **Carga mínima e suficiente:** IDs + dados que o consumidor precisaria buscar logo em seguida. Sem dados pessoais desnecessários.
- **Classe do evento** no formato do framework, com dados imutáveis (IDs e valores), sem comportamento.
- **Envelope padrão** para eventos que saem do processo (mensageria externa ou outro sistema); dentro da aplicação, a própria classe do evento é o contrato:

```json
{
  "id": "01J...",                       // único, usado para idempotência
  "type": "vendas.pedido-aprovado",     // <contexto>.<evento>
  "version": 1,
  "occurredAt": "2026-10-28T12:00:00Z",
  "producer": "vendas",
  "correlationId": "…",                 // rastreia o fluxo de ponta a ponta
  "causationId": "…",                   // id do comando/evento que causou este
  "tenantId": "…",
  "data": { "pedidoId": "…", "clienteId": "…", "total": { "valor": "800.00", "moeda": "BRL" } }
}
```

## Garantias

| Garantia | Como |
|---|---|
| Consistência com a mudança de estado | evento despachado **depois do commit** pelo recurso do framework ({{AGENTE: RECURSO_DE_DESPACHO_APOS_COMMIT}}); com a fila no próprio banco, o job é gravado na mesma transação. Outbox própria só como exceção registrada em ADR, quando a perda for inaceitável ([ADR-0003](adr/0003-eventos-com-recursos-do-framework.md)) |
| Entrega | pelo menos uma vez (*at-least-once*) |
| Duplicatas | consumidores **idempotentes**: a operação é naturalmente idempotente ou o handler verifica o estado antes de agir; use o recurso de unicidade/idempotência de jobs do framework, se houver |
| Ordem | garantida só por chave de partição (ex.: `pedidoId`); nunca dependa de ordem global |
| Falha no consumidor | retry com backoff pela configuração da fila do framework; após {{USUARIO: N}} tentativas, jobs falhos / *dead letter queue* com alerta |

### Reação que grava estado × reação que só avisa

| Reação | Exemplo | Como roda | Testes |
|---|---|---|---|
| **Grava estado de negócio** | liberar o próximo pedido da fila de espera, recalcular estoque, abrir cobrança | listener enfileirado na fila do framework ({{AGENTE: MECANISMO_DE_FILAS_DO_FRAMEWORK}}) com tentativas, backoff e idempotência; **ou** job agendado de reconciliação que encontra e refaz o que faltou | reexecução (mesma mensagem duas vezes → um efeito) e falha (primeira tentativa falha → a nova tentativa conclui) |
| **Só avisa** | log, notificação best-effort, métrica | em processo, depois do commit | o despacho, com o fake de eventos do framework |

Por quê: o evento em processo é despachado depois do commit; se a reação falha, o caso de uso já confirmou e ninguém tenta de novo. Para um aviso, perder um é aceitável; para estado de negócio, o sistema fica inconsistente em silêncio (o próximo da fila nunca é chamado).

**Sinal de violação:** listener em processo (sem fila, sem retry) que despacha um command com transação ou chama um repository de escrita, sem job de reconciliação registrado.

## Versionamento

- Mudanças **compatíveis** (adicionar campo opcional) mantêm a versão.
- Mudanças **incompatíveis** (remover/renomear campo, mudar semântica) criam `version: 2`; publique as duas versões até todos os consumidores migrarem.
- Consumidores ignoram campos desconhecidos (*tolerant reader*).

## Sagas

Processos que atravessam módulos são sagas:

- **Coreografia** (padrão): cada módulo reage a eventos e publica os seus. Simples para até ~3 passos.
- **Orquestração**: um coordenador explícito envia comandos e acompanha o estado. Use quando houver muitos passos, compensações ou necessidade de visibilidade do processo.
- Toda etapa com efeito tem uma **ação compensatória** definida.

| Saga | Tipo | Passos | Compensações |
|---|---|---|---|
| {{AGENTE: ex.: Checkout}} | {{AGENTE: coreografia}} | {{AGENTE: PedidoCriadoEvent → EstoqueReservadoEvent → PagamentoAprovadoEvent}} | {{AGENTE: liberar estoque se pagamento falhar}} |

## Catálogo

| Evento | Versão | Produtor | Consumidores | Quando é publicado | Schema |
|---|---|---|---|---|---|
| `{{AGENTE: contexto.evento}}` | 1 | `{{AGENTE: modulo}}` | `{{AGENTE: modulo}}` | {{AGENTE: condição}} | {{AGENTE: link}} |

## Como adicionar um evento

1. Confirme o nome com a linguagem ubíqua ([DOMAIN.md](DOMAIN.md)).
2. Defina o schema de `data` e registre no catálogo acima.
3. Crie a classe do evento em `events/` (ex.: `PedidoAprovadoEvent`) no formato do framework e registre-o no agregado. O handler salva pelo `PedidoRepository` e despacha o evento pelo mecanismo do framework, depois do commit.
4. Escreva teste unitário (o agregado registra o evento) e de integração (o teste do handler, com banco real, verifica o despacho com o fake de eventos do framework).
5. No consumidor: reação idempotente em `listeners/`, registrada no mecanismo do framework (enfileirada, com retry, se grava estado de negócio: [critério](#reação-que-grava-estado--reação-que-só-avisa)), como `Listener` (evento do próprio módulo, ex.: `EnviarComprovanteListener`) ou `Subscriber` (evento de outro módulo, ex.: `PedidoAprovadoSubscriber`), com teste de entrega duplicada. O listener delega ao handler de uma fatia; não usa ORM nem tem regra própria.
