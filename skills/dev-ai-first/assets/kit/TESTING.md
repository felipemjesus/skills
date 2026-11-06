# Testes

> Como testamos. Testes são a especificação executável do sistema e a principal rede de segurança para mudanças feitas por pessoas e por agentes.

## 1. Estratégia

```
            ▲  poucos, lentos, caros
           ╱ ╲      e2e / aceitação (BDD), incluindo e2e do frontend
          ╱───╲
         ╱     ╲    integração: handlers e repositories com banco real, listeners, jobs
        ╱───────╲
       ╱ unitário ╲  domínio (agregados, VOs, services, policies); componentes do frontend
      ╱───────────╲ muitos, rápidos, baratos
```

| Nível | O que cobre | I/O real? | Comando | Meta de tempo |
|---|---|---|---|---|
| Unitário | entidades e agregados, VOs, enums, serviços de domínio, policies | não | `{{AGENTE: CMD_TEST_UNIT}}` | suíte < {{USUARIO: N}} s |
| Integração | **handlers** (command e query) com banco real e Ports com fake; repositories (escrita e leitura), listeners, jobs | sim (banco real) | `{{AGENTE: CMD_TEST_INTEGRATION}}` | teste de uma fatia < {{USUARIO: N}} s |
| Contrato | todo client de um `Port` e o fake dele se comportam igual | depende | parte da integração | |
| Aceitação (BDD) | comportamento de ponta a ponta de uma funcionalidade | sim | `{{AGENTE: CMD_TEST_ACCEPTANCE}}` | |
| Componente (frontend) | comportamento visível de componentes e hooks da fatia, com rede simulada | não | `{{AGENTE: CMD_FRONTEND_TEST}}` | suíte < {{USUARIO: N}} s |
| E2E (frontend) | cenários BDD que têm tela, no navegador, com backend real | sim | `{{AGENTE: CMD_FRONTEND_E2E}}` | |

O domínio continua sendo a maior parte dos testes: é onde está a regra, e os testes dele são unitários e rápidos. Mesmo quando a entidade é o model do ORM (active record), ela é testada sem banco: instancie o model em memória, sem salvar, e chame o comportamento. Isso só funciona porque a entidade não chama persistência ([matriz de responsabilidades](ARCHITECTURE.md#41-responsabilidades)).

Testes usam os recursos da ferramenta de testes e do framework, não utilitários próprios: {{AGENTE: HELPERS_DE_TESTE_DO_FRAMEWORK}} (ex.: congelar o tempo, fakes de eventos, filas, HTTP e notificações, troca de dependência no container) e factories do ORM ou da biblioteca de testes para criar dados.

### Handlers: integração com banco real

Handlers são testados por padrão com **banco real** ([ADR-0004](docs/adr/0004-interfaces-so-em-fronteiras.md)). O handler só orquestra: carrega pelo repository, autoriza, chama o domínio, salva pelo repository e despacha eventos. A regra já está coberta pelos testes unitários do domínio; o que pode quebrar no handler é a consulta, a transação, a autorização e o despacho de eventos, e isso só um banco real mostra. Um fake de repository passaria nesses casos e esconderia o erro.

- **Banco:** o mesmo motor de produção ({{AGENTE: BANCO_DE_DADOS}}), em container local ou serviço no CI. Não substitua por um banco em memória de outro motor: diferenças de tipos, transações e SQL fazem o teste passar e a produção falhar.
- **Ciclo de vida:** um banco por execução da suíte, com as migrações aplicadas uma vez.
- **Isolamento por teste:** {{AGENTE: ESTRATEGIA_DE_ISOLAMENTO}}. Padrão recomendado: cada teste roda dentro de uma transação revertida no fim (rápido). Use limpeza das tabelas (truncate) quando o código testado depende do commit, como listeners e jobs despachados após o commit. Prefira o mecanismo de isolamento que o framework oferece para testes com banco.
- **Dependências:** o handler é obtido pelo container do framework, como em produção; só os `Port` (sistemas externos, LLM) são trocados por fakes, com o mecanismo de troca de dependência do framework. Tempo congelado e eventos/filas com os fakes do framework.
- **Feedback rápido:** `{{AGENTE: CMD_CHECK}}` roda os unitários. O agente roda o teste de integração da fatia que alterou (`{{AGENTE: CMD_TEST_INTEGRATION}} <caminho>`), e o CI roda a suíte de integração inteira.

Exemplo (pseudocódigo):

```
// features/aprovar-pedido/aprovar-pedido.handler.int.test
teste "recusa aprovação quando o total excede o limite de crédito":
  container.substituir(ConsultaCreditoPort, new ConsultaCreditoFake().comLimite(cliente: "c-1", R$ 1.000,00))
  eventosFake = criarEventosFake()
  pedido = factory(Pedido).doCliente("c-1").comTotal(R$ 1.200,00).pendente().criar()   // grava no banco
  aprovarPedidoHandler = container.obter(AprovarPedidoHandler)
  pedidoRepository = container.obter(PedidoRepository)

  excecao = esperarExcecao(LimiteCreditoExcedidoException):
    aprovarPedidoHandler.executar(new AprovarPedidoCommand(pedido.id, ator: analista))
  esperar(excecao.violacoes.map(v => v.regra)).ser(["limiteCreditoRespeitado"])

  esperar(pedidoRepository.obter(pedido.id).status).ser(PedidoStatusEnum.PENDENTE)
  eventosFake.esperarNaoDespachado(PedidoAprovadoEvent)
```

**Efeito depois do commit não sai se a transação falhar.** Caso de uso com efeito após o commit (evento, fila, e-mail, chamada a `Port`) tem teste obrigatório que provoca uma falha dentro da transação, depois da primeira gravação, e afirma que nada foi gravado e que o fake da porta ou da fila não recebeu nada. Por quê: efeito disparado antes do commit (ou fora do mecanismo "após o commit" do framework) passa em todos os testes do caminho feliz e avisa o cliente de um pedido que não existe.

```
teste "não notifica o cliente quando a gravação da aprovação falha":
  envioEmailFake = container.substituir(EnvioEmailPort, new EnvioEmailFake())
  pedido = factory(Pedido).pendente().criar()
  falharNaGravacao(HistoricoPedidoRepository)   // {{AGENTE: ex.: trocar o repository por um que lança, ou violar uma constraint}}

  esperarExcecao(...): aprovarPedidoHandler.executar(new AprovarPedidoCommand(pedido.id, ator: analista))

  esperar(pedidoRepository.obter(pedido.id).status).ser(PedidoStatusEnum.PENDENTE)   // nada gravado
  esperar(envioEmailFake.enviados).serVazio()                                         // nenhum efeito
```

**Endpoint de listagem: testes mínimos** (regras em [docs/API_GUIDELINES.md](docs/API_GUIDELINES.md#paginação-filtros-e-ordenação)), cada um esperando 400 com o parâmetro em `errors`: filtro com valor fora da lista fechada (status fora do enum); ordenação por campo fora da lista permitida; `limit` acima do máximo; cursor inválido; parâmetro desconhecido. Somam-se aos do comportamento (filtro aplicado, ordem, página seguinte sem repetir nem pular).

### Onde ficam

| Teste | Onde | Exemplo |
|---|---|---|
| Unitário de domínio | junto do arquivo testado | `src/modules/pedidos/entities/{{AGENTE: pedido.test / PedidoTest}}` |
| Integração de handler | junto da fatia, com sufixo de integração | `src/modules/pedidos/features/aprovar-pedido/{{AGENTE: aprovar-pedido.handler.int.test / AprovarPedidoHandlerTest}}` |
| Outros de integração (repository, client, listener) | `tests/integration/<modulo>/` | `tests/integration/pedidos/{{AGENTE: pedido.repository.test / PedidoRepositoryTest}}` |
| Aceitação (BDD) | `tests/acceptance/<modulo>/` | `tests/acceptance/pedidos/aprovar-pedido.feature` |
| Fakes de Port e fixtures | `tests/support/<modulo>/` | `ConsultaCreditoFake` |
| Factories de dados de teste | local que o ORM ou o framework usa | {{AGENTE: ex.: factory do model Pedido}} |
| Componente (frontend) | junto da fatia do frontend | `modules/pedidos/features/aprovar-pedido/aprovar-pedido-dialog.test` |
| E2E (frontend) | `tests/e2e/<modulo>/` | `tests/e2e/pedidos/aprovar-pedido.spec` |

Testes junto do código mantêm a fatia inteira numa pasta só; o sufixo de integração (ex.: `.int.test`) permite que o comando de unitários exclua esses arquivos e o de integração os inclua. Se a linguagem ou a ferramenta de testes preferir uma árvore separada (ex.: PHP com Pest e PSR-4), use `tests/unit/<modulo>/` (espelhando `entities/`, `enums/`, ...) e `tests/integration/<modulo>/features/`.

## 2. TDD

Ciclo: **vermelho → verde → refatorar.**

1. Escreva o menor teste que descreve o próximo comportamento e veja-o falhar pelo motivo certo. **O RED só conta se o teste rodou e falhou com a mensagem esperada** (asserção sobre o comportamento), não por erro de compilação, import ou fixture. A saída do RED vai no PR.
2. Escreva o mínimo de código para passar.
3. Refatore produção e teste mantendo verde.

Obrigatório para **todo comportamento novo**, nos dois níveis: unitário no domínio e integração do handler no caso de uso (o teste do handler também é escrito antes do handler e visto falhando). Também para correção de bugs (o teste reproduz o bug antes da correção; ver [Corrigindo bugs](#9-corrigindo-bugs)). Se a infraestrutura do teste de integração ainda não existe (primeira fatia do módulo), o RED é o primeiro teste que roda depois de montá-la; diga isso no relato. Para código exploratório (spike), descarte o spike e reescreva com TDD.

## 3. BDD

Funcionalidades com valor de negócio têm cenários em linguagem ubíqua, escritos com o time de produto quando possível:

```gherkin
# tests/acceptance/pedidos/aprovar-pedido.feature
Funcionalidade: Aprovar pedido
  Para liberar a separação no estoque
  Como analista comercial
  Quero aprovar pedidos dentro do limite de crédito do cliente

  Cenário: Pedido dentro do limite é aprovado
    Dado um cliente com limite de crédito de R$ 1.000,00
    E um pedido pendente de R$ 800,00 desse cliente
    Quando o analista aprova o pedido
    Então o pedido fica com status "aprovado"
    E o evento "PedidoAprovadoEvent" é publicado

  Cenário: Pedido acima do limite é recusado
    Dado um cliente com limite de crédito de R$ 1.000,00
    E um pedido pendente de R$ 1.200,00 desse cliente
    Quando o analista aprova o pedido
    Então a aprovação é recusada pela regra "limiteCreditoRespeitado"
```

- Cenários descrevem comportamento, não interface ("aprova o pedido", não "clica no botão verde").
- Um cenário, um comportamento.
- Step definitions finas: chamam handlers ou a API, sem lógica.
- Cenários que têm tela também viram testes e2e de frontend ([docs/FRONTEND.md](docs/FRONTEND.md#7-testes)).

## 4. Escrevendo bons testes

- **Nome descreve comportamento:** `recusa aprovação quando o total excede o limite de crédito`, não `testAprovar2`. Lida em sequência, a lista de nomes de testes é a lista de regras e transições: a especificação executável.
- **Matriz de transições por agregado.** Cada transição da tabela tem teste a partir de cada origem válida e a recusa ("estado não permite") a partir das demais, de preferência com o recurso de casos tabelados da ferramenta de teste:

  ```
  casos (origem, ação, resultado):
    (PENDENTE, APROVAR, APROVADO)
    (PENDENTE, CANCELAR, CANCELADO)
    (FATURADO, CANCELAR, recusa: estado não permite)
  ```
- **Teste que trava a definição de um conceito.** Cada conceito com regra ("item disponível", "cliente bloqueado") tem teste dos casos de borda na sua definição única; quem criar uma segunda definição verá que a primeira já estava coberta.
- **Teste de concorrência para limites contados e para fatos lidos como regra:** dispara duas operações em paralelo no limite e espera que só uma passe; sabotado sem a trava, falha. Vale também quando um caso de uso grava o fato que é pré-condição de outro ([ARCHITECTURE.md](ARCHITECTURE.md#51-comando-escrita), *write skew*): o teste dispara A × B em paralelo (ex.: `RegistrarInadimplencia` × `CriarPedido` para o mesmo cliente) e espera um dos dois desfechos válidos (o pedido entra antes da fatura ou é recusado depois dela), nunca o pedido aceito de um cliente que já estava bloqueado quando ele foi confirmado. Para o teste não depender da sorte, segure A dentro da transação (depois da trava, antes do commit) e só então dispare B.
- **Reação que grava estado:** tem teste de reexecução (a mesma mensagem duas vezes produz o efeito uma vez) e de falha (a primeira tentativa falha, a nova tentativa conclui) ([docs/EVENTS.md](docs/EVENTS.md#reação-que-grava-estado--reação-que-só-avisa)).
- **Forma clara não substitui teste.** Código fácil de ler deixa entender; só o teste deixa mudar com segurança.
- **Estrutura AAA** (arrange, act, assert) ou Dado/Quando/Então, com as três partes visíveis.
- **Um comportamento por teste.** Várias asserções sobre o mesmo resultado são aceitáveis.
- **Teste comportamento, não implementação.** Não verifique chamadas a métodos privados nem ordem de chamadas internas, a menos que a ordem seja o requisito.
- **Verifique pela interface pública.** Confira o resultado pelo que o sistema expõe: resposta da API, método de leitura do repository, evento capturado pelo fake do framework. Não use canal lateral (SQL direto no banco) quando existe forma pela interface. No teste de aceitação caixa-preta, verifique pela API; consulta direta ao banco só quando o efeito não tem leitura pela API (ex.: dado gravado só para auditoria), e diga isso no teste.
- **Erro pelo código, não pelo texto.** Testes de aceitação e de integração conferem o `type` do Problem Details e `violacoes[].regra`, nunca `title`, `detail` ou a mensagem: o texto muda por clareza ou tradução, o código é o contrato ([formato](CODING_GUIDELINES.md#4-erros)).

  ```
  // step "a aprovação é recusada pela regra {regra}": o nome da regra, nunca o nome de uma classe
  esperar(resposta.status).ser(422)
  esperar(resposta.corpo.type).terminarCom("/erros/limite-credito-excedido")   // opcional: a categoria, fora do Gherkin
  esperar(resposta.corpo.violacoes.map(v => v.regra)).conter(regra)
  // erro sem violacoes: pelo type
  esperar(resposta.corpo.type).ser("https://{{USUARIO: dominio}}/erros/pedido-ja-faturado")
  // ruim: esperar(resposta.corpo.title).conter("limite de crédito")
  ```
- **Sem teste tautológico.** O valor esperado é escrito à mão, não recalculado do mesmo jeito que o código calcula:

  ```
  // ruim: repete a fórmula do código; passa mesmo se a fórmula estiver errada
  esperar(pedido.total()).ser(itens.somar(i => i.preco * i.quantidade))
  // bom: valor conhecido do cenário
  esperar(pedido.total()).ser(Dinheiro.de("250.00"))
  ```
- **Dados de teste por factories** do ORM ou da biblioteca de testes, com valores padrão válidos e estados nomeados (ex.: `pendente()`, `aprovado()`). Builder próprio só se não houver factory.
- **Determinismo.** Tempo congelado e IDs e aleatoriedade fixos pelos helpers da ferramenta de testes ou do framework. Nada de `sleep`; aguarde condição com timeout.
- **Isolamento.** Cada teste prepara e limpa o próprio estado. A ordem de execução não importa.
- **Teste honesto.** Nada de teste vazio (`esperar(true).ser(true)`), teste isolado com `only` esquecido, teste que simula o próprio código testado e confere o valor simulado, nem teste que não roda no CI.

## 5. Dublês de teste

| Tipo | Quando usar |
|---|---|
| **Fake de Port** (implementação em memória, ex.: `ConsultaCreditoFake`) | sistemas externos e LLM. Repository **não** tem fake: handler usa o banco real |
| **Fakes do framework** | eventos, filas, HTTP, notificações, tempo: use os que o framework oferece, sem escrever os seus |
| Stub | resposta fixa para um cenário específico |
| Mock | só quando a *interação* é o comportamento (ex.: "e-mail foi enviado") |
| Spy | verificar eventos publicados (prefira o fake de eventos do framework) |

Não faça mock de tipos que você não controla (SDK, ORM). SDK de sistema externo fica atrás de um `Port` com fake; ORM é testado de verdade, com banco real.

O `Client` de um sistema externo é testado com **respostas reais gravadas** desse sistema (inclusive as malformadas e as de erro), trocando só o ponto de I/O; o teste confere a tradução de nomes, dados e erros para o vocabulário do domínio.

## 6. Testes como contrato com agentes

Agentes de código usam os testes para saber se acertaram. Por isso:
- A suíte unitária precisa ser **rápida** e rodar por arquivo, para dar feedback a cada passo. O teste de integração de uma fatia também precisa rodar sozinho, em poucos segundos.
- Falhas precisam ser **legíveis**: a mensagem diz o que era esperado e o que veio.
- Testes não podem ser alterados para acomodar uma implementação errada. Mudança de asserção exige justificativa no PR.

## 7. Cobertura

- Cobertura é sinal, não meta. Mínimo de {{USUARIO: N}}% nas pastas de domínio (`entities/`, `enums/`, `services/`, ...; por testes unitários) e nos handlers de `features/` (por testes de integração); sem meta em controllers, `repositories/`, `clients/`, `jobs/` e `listeners/` (cobertos por integração e aceitação).
- Código novo sem teste precisa de justificativa no PR.
- Testes de mutação ({{AGENTE: FERRAMENTA_DE_MUTACAO}}) recomendados no domínio dos módulos core, para medir a qualidade das asserções; opcionais nos demais.

## 8. Testes instáveis (flaky)

Teste instável é bug. Coloque em quarentena com issue vinculada no mesmo dia e corrija em até {{USUARIO: N}} dias. Nunca re-execute o CI até passar sem investigar.

## 9. Corrigindo bugs

1. **Reproduza o sintoma exato com um teste** antes de corrigir. O teste falha pelo motivo do bug e mostra o que foi relatado (o mesmo status, a mesma mensagem, o mesmo valor errado), não uma falha parecida (RED com evidência no PR). Reduza ao menor cenário que ainda falha antes de procurar a causa: cada dado que sai sem o teste ficar verde é uma hipótese a menos.
   - **Não reproduz?** Isso é o achado: o teste fica no relato mostrando que o caminho relatado não falha, e você pergunta ao usuário o dado ou o ambiente que falta (registro específico, horário, versão). Não "corrija" algo vizinho para ter o que entregar.
2. **Hipóteses antes de instrumentar.** Liste 3–5 causas possíveis em ordem de probabilidade, cada uma com o que ela prevê ("se a causa é a contagem incluir o pedido cancelado, cancelar antes de confirmar faz o erro sumir"). A lista vai no relato e não bloqueia o trabalho: siga pela primeira, e o usuário pode reordenar. Teste uma hipótese por vez, mudando uma variável por vez. Log de depuração leva um prefixo único (`[DBG-PEDIDO-LIMITE]`) e sai antes de concluir; uma busca pelo prefixo confirma que não ficou nenhum. Por quê: com uma ideia só, a primeira explicação plausível vira a causa, e o teste é ajustado até concordar com ela.
3. **5 porquês** a partir da hipótese confirmada, até a causa, não até o sintoma. Registre a hipótese confirmada e a cadeia no commit e na descrição do PR.
4. **O teste que teria pegado o erro:** escreva no nível certo (unitário se a regra está no domínio, integração se o erro é de consulta, transação ou evento). Se o projeto só tem um nível mais raso que não refaz a cadeia real do bug (ex.: só unitário, e o bug é de transação), verde nele não prova a correção: registre a falta do nível como achado no PR.
5. **Onde mais isso existe?** Busque a mesma causa nos outros pontos que usam o mesmo conceito (outros gates, outros handlers, consultas) e relate o que encontrou: corrija só o que foi pedido e liste o resto no PR (ou abra issue).
6. **Que verificação automática evitaria a classe do erro?** (regra de lint, de arquitetura, tipo mais restrito, constraint no banco). Registre como proposta no PR.

## 10. Regras de arquitetura

Regra de arquitetura nova (lint, dependências, testes de arquitetura) só é confiável depois de ser vista falhando: crie um caso sabotado (um arquivo que viola a regra), confirme que `{{AGENTE: CMD_ARCH_CHECK}}` falha com a mensagem esperada e então remova o caso. Registre a saída no PR.
