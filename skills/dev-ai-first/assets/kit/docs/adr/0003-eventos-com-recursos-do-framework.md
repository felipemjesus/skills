# 0003. Transação no caso de uso e eventos com os recursos do framework; outbox só como exceção

- **Status:** Proposta
- **Data:** {{USUARIO: AAAA-MM-DD}}

## Contexto

Módulos reagem a fatos de outros módulos, e dentro do módulo histórico e registros dependentes precisam ser consistentes com a operação. "O que é atômico" e "o que acontece depois" devem se responder lendo o caso de uso. O risco é o estado mudar e o evento se perder, ou o evento sair e a transação ser desfeita. O framework oferece eventos, listeners, filas e despacho depois do commit.

## Opções consideradas

1. **Eventos e filas do framework, despachados depois do commit.** Simples e idiomático; se o processo cair entre o commit e o despacho, o evento se perde, a menos que a fila seja gravada no mesmo banco e na mesma transação.
2. **Outbox própria** (evento gravado na transação, relay publica depois). Nada se perde, ao custo de tabela, relay e monitoramento próprios.
3. **Transação distribuída (2PC).** Complexa e mal suportada.

## Decisão

Opção 1 como padrão. Passo do caso de uso (consistência da operação) fica explícito no caso de uso, dentro de **uma transação por caso de uso**, aberta e confirmada à vista, nunca pelo repository; reação a um fato é despachada depois do commit e nunca grava o agregado que disparou o evento. Consumidores idempotentes, entrega *at-least-once*. Outbox própria só quando a perda de um evento for inaceitável e a fila não for gravada na mesma transação, registrada em ADR própria. Event sourcing não é o padrão. Detalhes: [ARCHITECTURE.md §5.1](../../ARCHITECTURE.md#51-comando-escrita) e [§5.3](../../ARCHITECTURE.md#53-eventos-passo-do-caso-de-uso--reação-a-um-fato).

## Consequências

- **Positivas:** nenhuma infraestrutura de eventos própria; retries e filas seguem a documentação; testes usam os fakes do framework.
- **Custos aceitos:** o caso de uso fica mais longo, com histórico e registros dependentes à vista; com fila fora do banco, uma janela pequena de perda entre commit e despacho; consistência eventual entre módulos.
- **Monitorar:** jobs falhos, tamanho da *dead letter queue*, idade do job pendente mais antigo.
