# Testes

> Níveis, comandos, regras próprias de teste e como corrigir bugs.

## 1. Estratégia

| Nível | O que cobre | I/O real? | Comando |
|---|---|---|---|
| Unitário | domínio: entidades, VOs, enums, serviços, policies | não | `{{AGENTE: CMD_TEST_UNIT}}` |
<!-- se: backend -->
| Integração | casos de uso com banco real e fronteiras externas com fake; acesso a dados, listeners, jobs | banco | `{{AGENTE: CMD_TEST_INTEGRATION}}` |
| Contrato | a implementação real de uma fronteira externa e o fake dela se comportam igual | depende | na integração |
<!-- fim: backend -->
<!-- se: bdd -->
| Aceitação (BDD) | funcionalidade de ponta a ponta | sim | `{{AGENTE: CMD_TEST_ACCEPTANCE}}` |
<!-- fim: bdd -->
<!-- se: frontend -->
| Componente | componentes e lógica de tela, rede simulada | não | `{{AGENTE: CMD_FRONTEND_TEST}}` |
| E2E | cenários com tela, backend real | sim | `{{AGENTE: CMD_FRONTEND_E2E}}` |
<!-- fim: frontend -->

Metas de tempo da suíte: a definir.

- **Helpers do framework, não utilitários próprios:** {{AGENTE: HELPERS_DE_TESTE_DO_FRAMEWORK}} (tempo, fakes de eventos, filas e HTTP, troca de dependência) e factories com estados nomeados (`pendente()`).
- **Teste verde não prova que funciona para o usuário:** depois dele, rode o sistema e observe pelo [mapa de verificação](docs/VERIFICACAO.md).
<!-- se: backend -->

### Casos de uso: integração com banco real

Consulta, transação, autorização e despacho só quebram de verdade com banco real. O acesso a dados **não** tem fake.
- **Domínio sem banco,** mesmo com active record: instancie o model em memória, sem salvar ([responsabilidades](ARCHITECTURE.md#41-responsabilidades)).
- **Motor de produção** ({{AGENTE: BANCO_DE_DADOS}}), nunca banco em memória de outro motor.
- **Isolamento:** {{AGENTE: ESTRATEGIA_DE_ISOLAMENTO}} (transação revertida; truncate quando o código depende do commit).
- **Obtido pelo container;** só as fronteiras externas (terceiros, LLM) viram fake. O agente roda o teste do caso de uso que alterou; o CI, a suíte inteira.
- **Efeito depois do commit não sai se a transação falhar.** Com efeito após o commit (evento, fila, e-mail, chamada externa), um teste provoca falha na transação depois da primeira gravação e afirma que nada foi gravado nem enviado. Por quê: efeito antes do commit passa no caminho feliz e avisa de um pedido que não existe.
<!-- fim: backend -->
<!-- se: frontend -->

### Telas: componente e ponta a ponta

- **Componente:** rede simulada na camada de API, não no componente; cobre carregando, vazio, erro e sucesso.
- **Seletor por papel e nome acessível** (`getByRole('button', { name: 'Cancelar pedido' })`); `data-testid` só quando não há papel. Nunca classe CSS, posição ou texto que muda. O seletor estável de cada funcionalidade fica no [mapa de verificação](docs/VERIFICACAO.md).
- **E2E:** o caminho principal de cada funcionalidade, backend real, espera por condição.
- **Erro do backend na tela:** um teste por categoria de erro tratada (validação no campo, conflito, não encontrado).
<!-- fim: frontend -->

## 2. TDD

Comportamento novo e bug começam por um teste no nível em que vivem (unitário no domínio, integração no caso de uso, componente na tela). **O RED só conta se falhou pela asserção esperada,** não por compilação, import ou fixture; a saída vai no PR. Sem infraestrutura de teste, o RED é o primeiro teste que roda depois de montá-la: diga isso.

<!-- se: bdd -->
## 3. BDD

Cenários em linguagem ubíqua em {{AGENTE: pasta dos .feature, ex.: tests/acceptance/<modulo>/}}: comportamento, não interface ("aprova o pedido", não "clica no botão"); um por cenário; steps finos, que chamam o caso de uso ou a API.

<!-- fim: bdd -->
## 4. Escrevendo bons testes

<!-- se: estados -->
- **Matriz de transições por agregado:** cada transição a partir de cada origem válida, e a recusa a partir das demais, em casos tabelados.
<!-- fim: estados -->
- **Teste que trava a definição de um conceito:** casos de borda de cada conceito com regra ("disponível") na sua definição única.
<!-- se: backend -->
- **Concorrência em limite contado e em fato lido como regra** ([write skew](ARCHITECTURE.md#51-comando-escrita)): duas operações em paralelo no limite, só uma passa; sabotado sem a trava, falha. Para A × B, segure A dentro da transação (depois da trava, antes do commit) e só então dispare B; espere um dos desfechos válidos, nunca os dois.
<!-- fim: backend -->
<!-- se: eventos -->
- **Reação que grava estado:** teste de reexecução (a mesma mensagem duas vezes produz o efeito uma vez) e de falha (a primeira tentativa falha, a nova conclui) ([docs/EVENTS.md](docs/EVENTS.md#reação-que-grava-estado--reação-que-só-avisa)).
<!-- fim: eventos -->
- **Erro pelo código, não pelo texto:** confira o `type` e `violacoes[].regra` ([formato](CODING_GUIDELINES.md#4-erros)), nunca `title`, `detail` ou a mensagem.
- **Verifique pela interface pública** (API, leitura pelo acesso a dados, fake de eventos, tela), não pelo armazenamento direto, salvo efeito sem leitura pela API (diga no teste).
- **Modos de falha de agente:** teste tautológico (valor esperado recalculado com a fórmula do código, em vez de escrito à mão), `only` esquecido, `sleep` em vez de esperar condição com timeout, teste vazio ou que confere o valor do próprio dublê.

## 5. Dublês de teste

Fake para fronteira externa e LLM (`PagamentoFake`); fakes do framework para eventos, filas, HTTP e tempo. Mock só quando a interação é o comportamento; nunca de SDK ou ORM. A implementação real da fronteira é testada com **respostas reais gravadas** (inclusive malformadas e de erro), trocando só o I/O.

## 6. Onde ficam

<!-- se: estrutura-projeto -->
{{AGENTE: tabela teste → onde fica → 1 exemplo real (unitário, integração do caso de uso, componente, e2e, fakes, factories) e o sufixo que separa os níveis}}
<!-- fim: estrutura-projeto -->
<!-- se: estrutura-kit -->
| Teste | Onde | Exemplo |
|---|---|---|
| Unitário de domínio | junto do arquivo testado | `src/modules/pedidos/entities/{{AGENTE: pedido.test / PedidoTest}}` |
| Integração do caso de uso | na fatia, com sufixo de integração | `src/modules/pedidos/features/aprovar-pedido/{{AGENTE: aprovar-pedido.handler.int.test}}` |
| Outros de integração | `tests/integration/<modulo>/` | `tests/integration/pedidos/{{AGENTE: pedido.repository.test}}` |
| Fakes de Port e fixtures | `tests/support/<modulo>/` | `PagamentoFake` |

Ferramenta que prefere árvore separada (ex.: Pest): `tests/unit/<modulo>/` e `tests/integration/<modulo>/`.
<!-- fim: estrutura-kit -->
<!-- se: frontend -->
Testes do frontend: [docs/FRONTEND.md](docs/FRONTEND.md).
<!-- fim: frontend -->

## 7. Cobertura

Meta no domínio e nos casos de uso: a definir; sem meta nas bordas. Código novo sem teste: justificativa no PR. Mutação no domínio core, se o projeto tiver a ferramenta ({{AGENTE: FERRAMENTA_DE_MUTACAO ou "nenhuma"}}).

## 8. Testes instáveis (flaky)

Teste instável é bug: quarentena com issue no mesmo dia; prazo de correção a definir. Nunca re-execute o CI até passar sem investigar.

## 9. Corrigindo bugs

1. **Reproduza o sintoma exato com um teste** antes de corrigir: o mesmo status, a mesma mensagem, o mesmo valor errado, não uma falha parecida. Reduza ao menor cenário que ainda falha.
   - **Não reproduz? Isso é o achado:** o teste fica no relato mostrando que o caminho relatado não falha, e você pergunta o dado ou o ambiente que falta. Não "corrija" algo vizinho para ter o que entregar.
2. **Hipóteses antes de instrumentar:** 3 a 5 causas em ordem de probabilidade, cada uma com o que ela prevê. Vão no relato e não bloqueiam: siga pela primeira, uma variável por vez. Log de depuração com prefixo único (`[DBG-PEDIDO-TOTAL]`), removido antes de concluir. Por quê: com uma ideia só, a primeira explicação plausível vira a causa.
3. **O teste que teria pegado o erro,** no nível certo (unitário se a regra está no domínio; integração se é consulta, transação ou evento; componente ou e2e se é tela). Se só há um nível mais raso, que não refaz a cadeia do bug, verde nele não prova a correção: registre a falta como achado.
4. **Onde mais isso existe?** Busque a mesma causa nos outros pontos que usam o conceito; corrija só o pedido e liste o resto no PR.
5. **Que verificação automática evitaria a classe do erro?** (lint, regra de arquitetura, tipo mais restrito, constraint) Proponha no PR.
<!-- se: verificacao-arquitetura -->

## 10. Regras de arquitetura

Regra nova só é confiável depois de vista falhando: crie um caso sabotado, confirme que `{{AGENTE: CMD_ARCH_CHECK}}` falha com a mensagem esperada, remova o caso e registre a saída no PR.
<!-- fim: verificacao-arquitetura -->
