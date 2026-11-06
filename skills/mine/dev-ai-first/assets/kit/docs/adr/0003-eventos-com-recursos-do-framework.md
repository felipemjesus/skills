# 0003. Transação no caso de uso e eventos com os recursos do framework; outbox só como exceção

- **Status:** Proposta
- **Data:** {{USUARIO: AAAA-MM-DD}}

## Contexto

Módulos reagem a fatos de outros módulos (ex.: reservar estoque quando um pedido é aprovado). Dentro do módulo, histórico, caixa de entrada e registros dependentes precisam ser consistentes com a operação, e "o que é atômico" e "o que acontece depois" precisam se responder lendo o caso de uso. O risco clássico é a inconsistência entre estado e evento: o estado muda e o evento se perde, ou o evento sai e a transação é desfeita.

{{AGENTE: FRAMEWORK}} oferece eventos, listeners e filas ({{AGENTE: MECANISMO_DE_COMANDOS_E_EVENTOS_DO_FRAMEWORK}}, {{AGENTE: MECANISMO_DE_FILAS_DO_FRAMEWORK}}), incluindo despachar um evento ou job só depois do commit da transação. Com framework first ([ADR-0005](0005-framework-first.md)), uma outbox própria com relay só se justifica se esses recursos não derem a garantia necessária.

## Opções consideradas

1. **Eventos e filas do framework, despachados depois do commit.** Simples e idiomático. Se o processo cair entre o commit e o despacho, o evento se perde, a menos que a fila seja persistida no mesmo banco e na mesma transação.
2. **Transactional outbox própria:** gravar o evento numa tabela na mesma transação; um relay publica depois. Nenhum evento se perde, ao custo de uma tabela, um relay e monitoramento próprios.
3. **Transação distribuída (2PC).** Complexa e mal suportada pela maioria das mensagerias.

## Decisão

Opção 1 como padrão.

- **Passo do caso de uso × reação a um fato.** O que faz parte da consistência da operação (gravar o agregado, histórico, caixa de entrada, outro registro do mesmo módulo) é passo explícito do handler, dentro da transação. Evento é só para reação posterior. Listener nunca grava nem muda o agregado que disparou o evento. O mapa evento → reações fica num só lugar; marcar no evento as capacidades que ele aciona é aceito como forma desse registro, só para reações após o commit.
- **Transação do caso de uso** (decidida aqui porque define o que é "depois do commit"): o limite fica à vista no handler; **uma transação por caso de uso**, que pode incluir os registros do mesmo módulo que o negócio exige consistentes, nunca de outro módulo; o repository nunca abre nem confirma transação; transações não se aninham (um caso de uso que chama outro reaproveita a transação). Detalhes em [ARCHITECTURE.md](../../ARCHITECTURE.md#51-comando-escrita).
- Eventos de domínio são despachados pelo mecanismo do framework, **depois do commit** da transação ({{AGENTE: RECURSO_DE_DESPACHO_APOS_COMMIT}}). HTTP, e-mail e fila nunca dentro da transação.
- Reações assíncronas são listeners enfileirados na fila do framework, com retry e *dead letter* conforme a documentação.
- Entrega *at-least-once* e consumidores idempotentes.
- Se a fila do framework usa o próprio banco relacional como armazenamento, o job gravado dentro da transação é atômico com a mudança de estado: verifique na documentação do framework como o despacho dentro de transação se comporta.
- **Exceção:** outbox própria (opção 2) só quando a perda de um evento for inaceitável e a fila adotada não for gravada na mesma transação (ex.: broker externo). A exceção é registrada em ADR própria, com o fluxo que exige.
- Event sourcing **não** é adotado como padrão.

## Consequências

- **Positivas:** nada de infraestrutura de eventos própria; listeners, retries e filas seguem a documentação; testes usam os fakes de eventos e filas do framework.
- **Negativas:** o handler fica mais longo, porque histórico e caixa de entrada viram passos à vista; com fila fora do banco, existe uma janela pequena de perda entre commit e despacho; consumidores precisam ser idempotentes; consistência eventual entre módulos.
- **Monitorar:** jobs falhos e tamanho da *dead letter queue*; idade do job mais antigo pendente.
