# 0004. Interfaces só em fronteiras

- **Status:** Proposta
- **Data:** {{USUARIO: AAAA-MM-DD}}

## Contexto

O desenho inicial previa interface + implementação para quase toda dependência do handler: `VendaRepository` (interface no domínio) + `SqlVendaRepository` (implementação na infraestrutura), com binding na composition root e um fake em memória para os testes. Na prática, a maioria dessas interfaces tem uma única implementação e nunca terá outra (o projeto usa um banco só). O resultado é cerimônia: dois ou três arquivos e um binding por repositório, fakes que precisam imitar o banco e testes de handler que passam com o fake e quebram com o banco real (consulta errada, transação, outbox).

Ao mesmo tempo, algumas dependências precisam mesmo de uma fronteira: sistemas externos e LLMs são lentos, instáveis, pagos ou não determinísticos, e o modelo deles não deve vazar para o domínio.

## Opções consideradas

1. **Interface para toda dependência.** Máximo desacoplamento e handlers testáveis só com fakes. Custo: muitos arquivos e bindings, fakes que divergem do banco, testes de handler pouco fiéis.
2. **Nenhuma interface.** Menos código, mas o handler passa a depender de SDKs e clientes externos; testes ficam lentos, caros ou instáveis e o modelo externo vaza para o domínio.
3. **Interface só em fronteiras externas, quando há mais de uma implementação real e na API pública entre módulos.** O resto é classe concreta.

## Decisão

Opção 3.

- Usa interface (sufixo `Port`, ou a API pública do módulo `<Modulo>Api`): sistema externo (ERP, pagamento, e-mail, SMS), LLM, mais de uma implementação real (estratégias) e API pública entre módulos. A `<Modulo>Api` é implementada pela `<Modulo>Facade`, que só delega aos handlers do próprio módulo; o consumidor injeta a interface (`estoqueApi: EstoqueApi`), e a mesma interface pode ser atendida por um cliente HTTP se o módulo for extraído.
- Dependência injetada recebe o nome do tipo em camelCase; por interface, o nome da interface (`consultaCreditoPort: ConsultaCreditoPort`), para o leitor ver a fronteira no nome.
- Não usa interface: repository (classe concreta em `repositories/`, sem prefixo de tecnologia, único lugar com ORM/SQL, inclusive leituras), domain service, policy, handler e qualquer recurso do próprio framework (autorização, flags, cache, filas, cliente HTTP, relógio). Esses são usados direto e substituídos nos testes pelos fakes e helpers do framework.
- Regra de três para interfaces: crie quando surgir a segunda implementação real ou a fronteira externa.
- Handlers são testados por padrão com **banco real** (teste de integração); Ports externos são trocados por fakes.
- "Não precisa de interface" **não** autoriza chamar sistema externo, LLM ou SDK direto do handler: fronteira externa é sempre via Port.

## Consequências

- **Positivas:** menos arquivos e bindings; testes de handler pegam erros de consulta, transação e despacho de eventos que um fake esconderia; o registro do módulo só liga Ports e API pública.
- **Negativas:** testes de handler ficam mais lentos que os unitários e exigem banco no ambiente de teste e no CI; trocar de ORM ou de banco custa mais (evento raro, aceito também pela [ADR-0005](0005-framework-first.md)). Risco de agentes generalizarem a regra ("sem interface") para fronteiras externas; mitigado pela lista explícita em [CODING_GUIDELINES.md](../../CODING_GUIDELINES.md#interfaces-só-quando-há-motivo) e em [AGENTS.md](../../AGENTS.md) e pela regra de dependência que proíbe handler de importar client externo ou SDK.
- **Quando revisitar:** surgir uma segunda implementação real de um repository (outro armazenamento), ou a suíte de integração ficar lenta a ponto de atrapalhar o ciclo de feedback.
