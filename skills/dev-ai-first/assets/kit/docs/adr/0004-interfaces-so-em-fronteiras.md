# 0004. Interfaces só em fronteiras

- **Status:** Proposta
- **Data:** {{USUARIO: AAAA-MM-DD}}

## Contexto

Interface + implementação para toda dependência (repository com interface no domínio, implementação na infraestrutura, binding e fake em memória) gera cerimônia: a maioria tem uma implementação só, e os fakes imitam mal o banco, então testes passam com o fake e quebram com o banco real (consulta, transação, despacho de eventos). Já sistemas externos e LLMs são lentos, instáveis, pagos ou não determinísticos, e o modelo deles não deve vazar para o domínio.

## Opções consideradas

1. **Interface para toda dependência.** Máximo desacoplamento; muitos arquivos e bindings, testes de handler pouco fiéis.
2. **Nenhuma interface.** Menos código, mas o caso de uso depende de SDK externo; testes lentos, caros ou instáveis.
3. **Interface só quando há motivo:** sistema externo ou LLM (`Port`), mais de uma implementação real, teste sem outro jeito de trocar a dependência e, nesta estrutura, a API pública entre módulos (`<Modulo>Api`), que pode virar cliente HTTP se o módulo for extraído. O resto é classe concreta.

## Decisão

Opção 3. Repository, domain service, policy, handler e recursos do framework não ganham interface; nos testes, handler roda com banco real e só os `Port` externos viram fakes. "Não precisa de interface" nunca autoriza chamar sistema externo, LLM ou SDK direto do caso de uso. Regra completa: [CODING_GUIDELINES.md](../../CODING_GUIDELINES.md#interfaces-só-quando-há-motivo).

## Consequências

- **Positivas:** menos arquivos e bindings; testes de handler pegam erros de consulta, transação e eventos que um fake esconderia.
- **Custos aceitos:** testes de handler mais lentos, com banco no ambiente de teste e no CI; trocar de ORM ou banco custa mais. Risco de o agente generalizar "sem interface" para fronteira externa, mitigado pela regra de dependência que proíbe SDK externo fora de `clients/`.
- **Quando revisitar:** surgir uma segunda implementação real de um repository, ou a suíte de integração atrapalhar o ciclo de feedback.
