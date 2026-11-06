## O quê

<!-- Resumo da mudança em 1–3 frases. -->

## Por quê

<!-- Issue: #… Contexto que o código não mostra. -->

## Como foi verificado

<!--
1. Comandos rodados.
2. O que foi observado (saída de teste, resposta da API), não só "passou".
3. Evidência do RED: saída do teste falhando pelo motivo certo, antes da implementação.
4. Por último: o que não foi verificado e por quê.
-->

- [ ] `{{CMD_CHECK}}` passou
- [ ] Plano e decisões conferidos com o diff: nada fora do escopo, nada planejado ou decidido faltando

## Impacto, riscos e rollback

<!-- Dados (migração, volume), contratos públicos (endpoints, eventos, API de módulo), compatibilidade com consumidores existentes. O que pode dar errado e como desfazer. Feature flag? -->

## Checklist de design

<!-- Respostas do checklist de design do AGENTS.md, uma linha cada. -->

## Checklist

- [ ] Testes cobrem o comportamento novo / o bug corrigido
- [ ] Respeita fronteiras de módulo e a matriz de responsabilidades (fatia não importa fatia; ORM só no repository; controller e request sem repository; regra de negócio só no domínio)
- [ ] A mesma montagem de entrada não foi copiada entre handlers ([passo comum](../CODING_GUIDELINES.md#passo-comum-a-vários-casos-de-uso); CONTRIBUTING.md, Revisão de código, item 2)
- [ ] Se um conceito mudou de sentido, todo leitor ganhou critério, ou o usuário decidiu mantê-lo com nome próprio (resposta citada; [checklist de design, item 5](../AGENTS.md#checklist-de-design))
- [ ] Usa o recurso do framework ou de biblioteca adotada em vez de solução própria (ou justifica a exceção)
- [ ] Contratos públicos (API, eventos, API de módulo) inalterados **ou** mudança compatível e documentada
- [ ] Itens de "perguntar antes" no diff (tabela em CONTRIBUTING.md, Revisão de código) listados com a autorização de cada um
- [ ] Documentação atualizada (tabela em AGENTS.md)
- [ ] Sem segredos, PII em logs ou dependências novas não aprovadas
- [ ] Revisão de segurança solicitada, se aplicável
- [ ] Feito com ajuda de agente de IA: sim / não

