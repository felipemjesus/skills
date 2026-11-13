# Arquitetura

> Estado atual da arquitetura de {{AGENTE: NOME_DO_PROJETO}}. O motivo das decisões está em [docs/adr/](docs/adr/README.md).

## 1. Objetivos e atributos de qualidade

Em ordem de prioridade: em conflito, o de cima vence.

| # | Atributo | Meta mensurável |
|---|---|---|
| 1 | Manutenibilidade | a definir (ex.: mudança típica toca 1 módulo) |
| 2 | Disponibilidade | a definir (ex.: 99,9% mensal) |
| 3 | Desempenho | a definir (ex.: p95 < 300 ms) |

Restrições: a definir.

## 2. Contexto do sistema

```mermaid
flowchart LR
  user([Usuário]) --> app[{{AGENTE: NOME_DO_PROJETO}}]
  app --> ext[(Sistemas externos<br/>{{AGENTE: SISTEMAS_EXTERNOS}})]
```

## 3. Contêineres

- **Aplicação:** em {{AGENTE: FRAMEWORK}}.
<!-- se: backend -->
- **Banco:** estado transacional, em {{AGENTE: BANCO_DE_DADOS}}.
<!-- fim: backend -->
<!-- se: eventos -->
- **Fila e workers:** reações assíncronas e jobs, em {{AGENTE: MENSAGERIA}}; mesmo código, outro processo.
<!-- fim: eventos -->
<!-- se: frontend -->
- **Frontend:** em {{AGENTE: FRONTEND}} ([docs/FRONTEND.md](docs/FRONTEND.md)).
<!-- fim: frontend -->

{{AGENTE: apague o que não existe e acrescente o que existe (cache, outro processo)}}

## 4. Estilo arquitetural

**Princípios**, válidos em qualquer organização do código:
- **Responsabilidade por papel** (§4.1); a regra de negócio fica no domínio.
- **Framework first:** cada peça usa o recurso que {{AGENTE: FRAMEWORK}} documenta, como a documentação mostra; solução própria só quando ele não oferece, com justificativa.
- **Módulo com porta pública:** outro módulo só fala com ele pela API pública (§6).
- **O caminho convencional é o mais curto:** seguir o [exemplo de referência](CODEBASE_MAP.md#exemplos-de-referência) custa menos que inventar.
- **Cada funcionalidade num lugar com dono:** uma busca pelo nome do negócio acha a cadeia inteira (§4.2).
- **Um único escritor por valor durável:** cada dado gravado (tabela, campo, arquivo, configuração) tem um só dono que escreve; os outros leem ou pedem a ele.
- **Trabalho novo acrescenta arquivos,** em vez de mais um ramo (`if`, `switch`, entrada num registro central) numa raiz compartilhada.
- **Dependência proibida falha por máquina** (§9).
- **Exceção explícita:** declarada na configuração da verificação ou em §11, com motivo, e revisada como mudança de arquitetura.
- **Princípio × padrão do projeto:** o código novo segue o padrão do projeto, sem misturar duas formas no mesmo módulo; onde o padrão contraria um princípio, a divergência vai para §11 e o dev decide se migra.

<!-- se: estrutura-kit -->
**Estrutura proposta pelo kit:** monolito modular com fatias verticais e domínio rico ([ADR-0002](docs/adr/0002-monolito-modular-com-fatias-verticais.md)), framework first ([ADR-0005](docs/adr/0005-framework-first.md)). Um deploy, com módulos alinhados aos contextos do [domínio](docs/DOMAIN.md); no módulo, uma pasta por caso de uso em `features/` e um domínio rico compartilhado entre as fatias (`entities/`, `enums/`, `services/`, ...). Pasta convencional do framework (`Models/`, `Policies/`) fica dentro do módulo.
<!-- fim: estrutura-kit -->
<!-- se: estrutura-projeto -->
**Estrutura identificada:** {{AGENTE: organização real (por camada, por módulo, por feature) em até 5 linhas, com 1 `arquivo` de exemplo de cada tipo; código novo imita o vizinho}}
<!-- fim: estrutura-projeto -->
<!-- se: backend -->

Recursos do framework neste projeto:
- **Entidade:** {{AGENTE: model do ORM (active record) ou classe de domínio separada}}. Com active record, o model é a entidade, mas consulta e gravação ficam na persistência; com classe separada, a persistência converte linha ↔ entidade.
- **Comandos, eventos e filas:** {{AGENTE: MECANISMOS_DO_FRAMEWORK}}; o job delega a um caso de uso.
- **Data/hora e IDs:** {{AGENTE: ex.: relógio do framework, UUIDv7 pelo ORM}}; nos testes, tempo congelado pelo helper da ferramenta.
- **Erros HTTP:** exceção de domínio mapeada para resposta num só lugar, pelo tratamento global do framework.
<!-- fim: backend -->

### 4.1 Responsabilidades

Cada papel tem um único motivo para mudar, qualquer que seja o nome do tipo. Referência para escrever e revisar código.

| Papel | Faz | Não faz |
|---|---|---|
| Entrada (rota, controller, comando de terminal) | recebe, monta a intenção, delega ao caso de uso, formata a saída | regra de negócio, try/catch de regra, consulta ao formatar |
| Validação de forma | presença, tipo e tamanho, na borda; regra com value object fica só no VO | regra de negócio; "existe" e "único" (do caso de uso, garantidos no banco) |
<!-- se: backend -->
| Caso de uso | roteiro da operação (§5.1): carrega, autoriza, chama o domínio, grava; abre e fecha a transação; efeitos depois do commit | `if` de negócio, ORM, HTTP, sessão ou contexto ambiente, terceirizar a sequência ([passo comum](CODING_GUIDELINES.md#passo-comum-a-vários-casos-de-uso)) |
| Domínio (entidade, agregado, VO, enum, serviço de domínio) | métodos de intenção e predicados com nome do negócio; invariantes; estado só pela transição (§5.4); regra entre agregados num serviço, com os dados prontos | persistir, consultar, HTTP, efeito externo |
| Persistência | **único lugar com ORM e SQL**; leitura com nome que revela todo filtro; `obter*` lança "não encontrado" ([verbos](CODEBASE_MAP.md#verbos-com-contrato-de-retorno)) | regra de domínio ([um conceito](CODING_GUIDELINES.md#um-conceito-em-memória-e-na-consulta)), objeto HTTP, usuário do contexto, **abrir ou confirmar transação** |
| Consulta | devolve uma projeção pronta (§5.2) | carregar agregado para ler |
<!-- fim: backend -->
| Integração externa | fala com sistema externo ou LLM atrás de uma fronteira; traduz nomes e erros para o domínio | regra de negócio; vazar o modelo externo |
<!-- se: eventos -->
| Reação a evento | reage a um fato depois do commit, delegando a um caso de uso | regra de negócio, gravar o agregado que disparou o evento |
<!-- fim: eventos -->
<!-- se: frontend -->
| Tela / componente | apresenta e coleta; mostra ações e erros vindos do backend ([docs/FRONTEND.md](docs/FRONTEND.md)) | regra de negócio, validação de negócio duplicada |
<!-- fim: frontend -->
<!-- se: cli -->

Comando de lote ou agendado é entrada: idempotente, registra o que processou, formata a saída numa classe com teste.
<!-- fim: cli -->

<!-- se: estrutura-kit -->
**Neste projeto (estrutura do kit):**

| Papel | Tipo |
|---|---|
| Entrada | `Route` + `Controller` na fatia (`src/modules/vendas/features/criar-venda/`); saída por `Resource` |
| Validação de forma | `Request`; autorização simples pela `Policy` |
| Caso de uso | `Command` + `CriarVendaHandler` na fatia, na forma da §5.1 |
| Domínio | `entities/`, `enums/`, `services/`, `specifications/`, `policies/`, `events/`, `exceptions/` |
| Persistência | `repositories/*Repository` (+ `mappers/`, só com entidade separada do model) |
| Consulta | `Query` + handler + método de leitura do repository que devolve DTOs |
| Integração externa | `ports/*Port` + `clients/*Client` |
| Reação | `Subscriber`, `Listener` ou `Job` em `listeners/`, que delega a um handler |
| API pública | `<Modulo>Api` + `<Modulo>Facade` em `api/`, que só delega |

Controller e handler finos são deliberados; não os funda. Mas cada salto traz informação nova: nada de `XService` com os casos de uso do agregado nem fachada que delega a outra fachada.
<!-- fim: estrutura-kit -->
<!-- se: estrutura-projeto -->
**Neste projeto:** {{AGENTE: para cada papel acima, "papel → tipo real (`arquivo` de exemplo)", 1 linha cada, só o que o código separa; o que ele mistura vai como dívida em §11}}
<!-- fim: estrutura-projeto -->

**Sinais de violação:**
- regra de negócio na entrada, na tela ou numa reação; condição de negócio montada fora do domínio (`||`/`&&` de consultas ou predicados);
- um conceito definido de dois jeitos ou com dois nomes; regra sem nome fora do dono (número mágico, regra repetida);
- status mudado por fora da transição (atribuição direta, atualização em massa);
- entrada por canal lateral (sessão entre requisições, contexto ambiente); erro engolido ou convertido em vazio; escrever antes de validar.
<!-- se: backend -->
- commit escondido (persistência que confirma, duas transações num caso de uso, transação aninhada); erro seguido de commit;
- efeito externo dentro da transação ou disparado pela entidade; gravação do caso de uso feita por uma reação em outro arquivo;
- domínio anêmico: o caso de uso muda campos em sequência em vez de chamar um método de intenção.
<!-- fim: backend -->
<!-- se: estrutura-kit -->
- handler que só repassa a um service do agregado; sub-roteiro (travar, carregar, salvar) copiado em vários handlers.
<!-- fim: estrutura-kit -->

### 4.2 Pastas

A árvore está no [CODEBASE_MAP.md](CODEBASE_MAP.md); aqui ficam os princípios e as regras de dependência, numeradas para a §9.

- **Um nome de negócio em toda a cadeia,** igual e no mesmo número gramatical, da rota ao evento (`cancelar` → `CancelarPedido` → transição `CANCELAR` → `PedidoCancelado`).
- **Tudo o que roda está ligado à vista** no registro do framework; código morto e alternativa comentada saem.
<!-- se: estrutura-kit -->
- **Mesmo gabarito:** o prefixo diz o conceito, o sufixo diz o papel e a pasta (`*Exception` → `exceptions/`); pasta só com arquivo.
- **Árvore rasa:** nenhuma pasta de camada técnica dentro da fatia (`http/`, `dto/`); cada operação, inclusive cada transição, é uma fatia.
- **Variante aceita** em base com pastas por tipo do framework: o mesmo subcaminho `Conceito/Verbo` em todas as árvores, espelhamento verificado (§9).
<!-- fim: estrutura-kit -->

**Regras de dependência:**

1. Outro módulo só usa a API pública do módulo.
2. HTTP e SDK de sistema externo ou LLM só na integração externa.
3. Interface só nos [casos previstos](CODING_GUIDELINES.md#interfaces-só-quando-há-motivo); nada de despacho por string, método mágico ou troca de classe por varredura de pasta.
<!-- se: backend -->
4. A entrada e a validação não acessam a persistência nem o ORM.
5. ORM e SQL só na persistência, inclusive leituras (exceção: health check e instrumentação do ORM).
6. Reações e jobs não gravam pela persistência; delegam a um caso de uso.
7. O domínio não depende da persistência, da integração externa, de HTTP nem de SDK (recursos do framework do modelo idiomático são permitidos).
8. A persistência não depende de outra persistência, de caso de uso, de reação nem de autorização.
<!-- fim: backend -->
<!-- se: estrutura-kit -->

Na estrutura do kit: uma fatia não importa outra (o que duas usam sobe para a pasta do tipo); outro módulo só importa `api/` e injeta `<Modulo>Api`; as pastas de domínio não importam `repositories/`, `mappers/`, `clients/`, `jobs/`, `features/` nem `listeners/`; a facade não importa `repositories/`, `clients/` nem ORM; bindings só para `Port` e API pública.
<!-- fim: estrutura-kit -->
<!-- se: estrutura-projeto -->

{{AGENTE: como as regras acima aparecem nas pastas reais e as regras próprias do projeto, numeradas a partir da última, 1 linha cada; regra que o código antigo não segue é "meta", com as exceções em §11}}
<!-- fim: estrutura-projeto -->

## 5. Fluxos principais

### 5.1 Comando (escrita)

A escrita valida a forma na borda, roda o roteiro no caso de uso e aplica a regra no domínio; regras independentes são avaliadas todas e devolvidas juntas ([erros](CODING_GUIDELINES.md#4-erros)).

<!-- se: estrutura-kit -->
O handler tem sempre a mesma forma: (1) **carregar** pelo repository; (2) **pré-condições**, falhando cedo: existe, `Policy`, o estado permite; (3) **domínio** aplica as regras; (4) **transição** pela tabela (§5.4); (5) **gravar** num bloco curto, na transação; (6) **efeitos depois do commit**; (7) **responder** com identificador ou status, nunca a projeção de leitura.
<!-- fim: estrutura-kit -->
<!-- se: estrutura-projeto -->
{{AGENTE: forma real de uma escrita, com 1 `arquivo` de exemplo: onde a entrada é validada, onde está a regra, onde a transação abre e fecha}}
<!-- fim: estrutura-projeto -->
<!-- se: backend -->

**Transação**, à vista no caso de uso, com o recurso do framework ou do ORM:
- **Uma por caso de uso,** com os registros do mesmo módulo que o negócio exige consistentes (histórico, itens); de outro módulo, nunca: entre módulos, consistência eventual, por evento.
- **A persistência nunca abre nem confirma:** grava; quem confirma é o caso de uso. Sem aninhar: o caso de uso chamado usa a transação de quem chamou.
- **Validar e calcular antes da primeira escrita; efeito externo só depois do commit.**

**Concorrência.** Falha sem aviso: cada transação sozinha parece correta.
- **Limite contado** ("a soma das reservas não passa do saldo do `Estoque`"): contar e gravar na mesma transação, travando antes a linha do agregado dono do limite, ou restrição no banco. Sem isso, duas requisições contam N-1 juntas e as duas gravam.
- **Fato gravado por um caso de uso e lido como regra por outro** (*write skew*). Ex.: `EstornarPagamento` grava o estorno; `FaturarPedido` recusa pedido estornado. Os dois serializam no **mesmo** ponto: a mesma trava (a linha do `Pedido`) ou uma restrição. Ao escrever uma regra que lê um fato, pergunte quem grava esse fato e que trava os dois compartilham.
- **A linha da trava é de outro módulo:** não trave a tabela dele; use trava consultiva (*advisory lock*) com chave nomeada pelo conceito, num método da persistência do módulo da regra (`travarSaldoEstoque(estoqueId)`), ou uma cópia local mantida por evento. Dado de outro módulo lido fora da trava pode mudar antes do commit: risco aceito só se registrado em §11.
- Cada caso tem um teste que dispara as operações em paralelo e falha sem a proteção ([TESTING.md](TESTING.md#4-escrevendo-bons-testes)). Nesta stack: {{AGENTE: RECURSOS_DE_TRAVA_DE_LINHA_E_CONSULTIVA}}.

**Carregar uma vez, já travado,** dentro da transação, pelo id (`obterTravado(id)`), e autorizar depois. Um objeto, um nome: nunca `pedidoEncontrado` e `pedidoTravado` para o mesmo agregado.
<!-- fim: backend -->

### 5.2 Consulta (leitura)

Leitura não passa pela regra de escrita: devolve uma projeção pronta.
<!-- se: backend -->
- Um método de leitura da persistência devolve DTOs; uma forma só para toda leitura, mesmo curta.
- Autorização e escopo com nome no caso de consulta (`listarPorUnidadeUsuario`), nunca escondidos na persistência.
- Filtros em lista fechada; o nome revela todo filtro de negócio (`listarPendentesPorPedido`, não `listarTodos` que filtra).
- Armazenamento de leitura próprio só quando a carga justificar (ADR).
<!-- fim: backend -->

### 5.3 Eventos: passo do caso de uso × reação a um fato

O que faz parte da consistência da operação é passo explícito do caso de uso; o que pode acontecer depois é reação a um fato.
<!-- se: backend -->
O passo fica dentro da transação; a reação roda **após o commit** e nunca grava o agregado que disparou o evento.
<!-- fim: backend -->
<!-- se: eventos -->
Reação que grava estado precisa de entrega garantida (fila com retry e idempotência, ou reconciliação); a que só avisa pode rodar em processo. O mapa evento → reações fica num só lugar: [docs/EVENTS.md](docs/EVENTS.md#reação-que-grava-estado--reação-que-só-avisa).
<!-- fim: eventos -->

### 5.4 Estados e transições

Toda entidade com status muda de estado só por uma tabela de transições declarada num lugar só.
<!-- se: estados -->
A tabela (ação → origem → destino) fica no enum de estado ou ao lado da entidade.
- **Porta única:** só um método de transição que consulta a tabela muda o estado; HTTP, job, lote e console chamam a mesma transição. Exceções também são dados da tabela.
- **Guarda com motivo:** recusa lança "estado não permite" com mensagem de negócio.
- **Mesma fonte para servidor e tela:** as ações permitidas saem da tabela e vão na resposta da API; a tela não recria a máquina.
- **Histórico de toda transição** (quem, quando, origem, destino, motivo), registrado pelo método de transição numa lista do agregado e gravado junto com ele. O caso de uso nunca monta o registro: montado ali, a transição que o esquece fica sem histórico sem nenhum teste falhar.

  ```
  transicionar(acao, ator, motivo):
    destino = PedidoStatusEnum.transicoes.destino(acao, this.status)   // lança se a tabela recusa
    this.transicoes.adicionar(HistoricoPedido(de: this.status, para: destino, quem: ator, motivo))
    this.status = destino
  ```
- **Alcance:** toda entidade com status, inclusive a interna de um agregado. Guarda espalhada (`se status != ATIVO: lançar`) é uma segunda máquina.
- **Transição pelo tempo** (expirar, vencer): um job chama o caso de uso que transiciona; nunca grava o status por fora.
- **Teste:** matriz de transições válidas e inválidas ([TESTING.md](TESTING.md#4-escrevendo-bons-testes)). {{AGENTE: MAQUINA_DE_ESTADOS_DO_FRAMEWORK}} vale se for a única porta.
<!-- fim: estados -->

## 6. Comunicação entre módulos

| Necessidade | Mecanismo |
|---|---|
| Consulta ou comando síncrono | API pública do outro módulo (facade), que só delega; só DTOs públicos |
| Reagir a algo que aconteceu | evento; consumidor idempotente |
| Dado de outro módulo lido com frequência | cópia local alimentada por eventos |
| Sistema externo | integração que traduz nomes e erros (*anticorruption layer*) |

**Erros na API do módulo:** exceções públicas de categorias fechadas, documentadas na API. O verbo diz o desfecho da ausência (`obter*` lança "não encontrado"; `buscar*`/`existe*` devolvem vazio ou booleano). O consumidor deixa a exceção atravessar, ou a traduz só quando o significado muda.
<!-- se: backend -->

Proibido: escrever em tabela de outro módulo, transação entre módulos.
<!-- fim: backend -->
<!-- se: estrutura-kit -->

Na estrutura do kit: interface `<Modulo>Api` injetada pelo nome (`estoqueApi: EstoqueApi`), implementada pela `<Modulo>Facade`, com as exceções públicas em `api/`; reação por `Subscriber` em `listeners/`; sistema externo por `Port` + `Client`.
<!-- fim: estrutura-kit -->
<!-- se: estrutura-projeto -->

{{AGENTE: como um módulo (ou área) usa outro hoje: chamada direta, serviço compartilhado, evento; 1 exemplo `arquivo`}}
<!-- fim: estrutura-projeto -->

## 7. Dados

Dados pessoais classificados em [SECURITY.md](SECURITY.md); retenção: a definir.
<!-- se: backend -->
- Um schema (ou prefixo de tabela) por módulo; só o dono escreve.
- Migrações versionadas e retrocompatíveis: adicionar → migrar dados → remover em release posterior.
- Nome físico opaco de base legada (`TAB18101`) só no mapeamento do ORM; o resto usa nomes do domínio.
- IDs gerados na aplicação pelo recurso do ORM, do framework ou da linguagem.
<!-- fim: backend -->

## 8. Capacidades transversais

Pelo recurso do framework ou de biblioteca documentada, sem wrapper próprio.

| Capacidade | Recurso |
|---|---|
| Autenticação | {{AGENTE: MECANISMO_DE_AUTENTICACAO}} |
| Autorização | {{AGENTE: MECANISMO_DE_AUTORIZACAO}}; checada antes da operação, nunca só na tela |
| Configuração | {{AGENTE: MECANISMO_DE_CONFIGURACAO}}, validada na inicialização |
| Feature flags | {{AGENTE: MECANISMO_DE_FEATURE_FLAGS}} |
| Resiliência | timeout e retry com backoff pelo cliente HTTP ({{AGENTE: CLIENTE_HTTP}}) e pela fila |
<!-- se: observabilidade -->

Observabilidade: [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md).
<!-- fim: observabilidade -->

## 9. Fitness functions

Como cada regra de arquitetura e de código é garantida, da mais forte para a mais fraca: `lint`, `tipos`, `teste`, `CI`, `revisão` ou `ainda não existe`. Regra só de revisão é candidata a virar verificação; comentário de review que se repete vira lint.

{{AGENTE: ajuste cada linha ao que o projeto usa de fato (ferramenta e regra); sem verificação, "ainda não existe"}}

| Regra | Garantida por |
|---|---|
| §4.2 regras 1 a 3 | lint de fronteiras; interfaces também por revisão |
<!-- se: backend -->
| §4.2 regras 4 a 8 | lint de fronteiras |
| Transação só no caso de uso | lint ou revisão |
| Limite contado e *write skew* | teste de concorrência |
| Caso de uso com banco real | teste + CI |
| Consulta ao formatar a saída | ORM proibindo lazy loading em desenvolvimento |
<!-- fim: backend -->
<!-- se: estrutura-kit -->
| Fatia não importa fatia; pastas do kit | lint de fronteiras |
| Variante por tipo: `Conceito/Verbo` espelhado | script no CI |
<!-- fim: estrutura-kit -->
<!-- se: estados -->
| Status só pela transição; todo enum de status declara a tabela | busca no CI + teste que percorre os enums |
<!-- fim: estados -->
| Regra de negócio fora do domínio; um conceito, duas definições | revisão |
| Tamanho e complexidade por papel | lint |
| Orientação a objetos: sem funções soltas na lógica | lint ou revisão |
| Versões e sintaxe atual: nada de API obsoleta | lint + tipos |
| Framework first; interfaces só quando há motivo; nomes | revisão |
| Erros com categoria fechada | tipos + teste |
| Teste primeiro, falhando pelo motivo certo | revisão (saída do teste no PR) |
| Formatação | lint |
| Links e caminhos citados nos documentos | CI |
| Suíte unitária rápida (a definir) | CI |
<!-- se: verificacao-arquitetura -->

Ferramenta de fronteiras: `{{AGENTE: CMD_ARCH_CHECK}}`. O que os documentos afirmam sobre a configuração é verdade nela; regra nova só entra depois de vista falhando num caso sabotado ([TESTING.md](TESTING.md#10-regras-de-arquitetura)).

**Mensagem de cada verificação:** o que foi violado · por quê (uma linha) · faça isto · link para a seção; onde uma exceção pode ser legítima, "não desative nem mude a configuração: pergunte". Na falha, o agente lê a mensagem. Campo da ferramenta: {{AGENTE: CAMPO_DE_MENSAGEM_DA_FERRAMENTA}}.

**Baseline em código legado:** violações existentes congeladas numa baseline versionada ({{AGENTE: RECURSO_DE_BASELINE}}); violação nova ou agravada bloqueia o PR; a dívida fica em §11 e só diminui. Regravar só ao adotar a regra, depois de perguntar. Regra com baseline é "meta, com N exceções", nunca "cumprida".
<!-- fim: verificacao-arquitetura -->

## 10. Decisões registradas

Índice e critério das ADRs: [docs/adr/README.md](docs/adr/README.md).

## 11. Riscos e débitos conhecidos

Dívida achada no código, divergência entre o padrão do projeto e um princípio (§4), regra que é meta, risco aceito.

| Item | Impacto | Plano |
|---|---|---|
| {{AGENTE: ex.: módulo X escreve em tabela do módulo Y (`arquivo`)}} | {{AGENTE: impacto}} | a definir |

## 12. Pacotes base compartilhados

Pacote usado por várias aplicações tem propósito no README, contrato no tipo (nunca em convenção interna), erros externos traduzidos, exemplos verificados no CI e versão comum; adotar um é decisão em ADR.
<!-- se: estrutura-projeto -->
{{AGENTE: pacotes internos compartilhados e o que cada um exige do consumidor, ou "nenhum"}}
<!-- fim: estrutura-projeto -->
