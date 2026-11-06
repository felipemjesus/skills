# AGENTS.md

> Ponto de entrada para agentes de código e para pessoas novas no projeto. Leia inteiro antes de alterar qualquer coisa. É curto de propósito: os detalhes estão nos documentos linkados.

## Sobre o projeto

**{{AGENTE: NOME_DO_PROJETO}}**: {{USUARIO: DESCRICAO_EM_UMA_FRASE}}.

- **Domínio:** {{USUARIO: RESUMO_DO_DOMINIO}}. Linguagem ubíqua e regras de negócio em [docs/DOMAIN.md](docs/DOMAIN.md).
- **Stack:** {{AGENTE: LINGUAGEM}} · {{AGENTE: FRAMEWORK}} · {{AGENTE: BANCO_DE_DADOS}} · {{AGENTE: MENSAGERIA}} · frontend em {{AGENTE: FRAMEWORK_FRONTEND}}, com módulos e fatias espelhando os do backend
- **Arquitetura:** monolito modular, **framework first** (recursos nativos de {{AGENTE: FRAMEWORK}} antes de solução própria); cada módulo organizado em fatias verticais por caso de uso (`features/`) sobre um domínio rico, com uma pasta por tipo de arquivo (`entities/`, `enums/`, `events/`, `ports/`, `repositories/`, `clients/`, ...) e reações a eventos em `listeners/`; separação de responsabilidades estrita ([matriz](ARCHITECTURE.md#41-responsabilidades)); DDD tático no domínio; CQRS leve; eventos pelo mecanismo do framework. Nomes em português com sufixo técnico em inglês (`CriarVendaHandler`, `VendaCriadaEvent`). Detalhes em [ARCHITECTURE.md](ARCHITECTURE.md).

<!-- Se o projeto também usa o kit aplicacao-de-ia, cole aqui as seções de docs/ai/AGENTS_SNIPPET.md. -->

## Comandos

| Ação | Comando |
|---|---|
| Instalar dependências | `{{AGENTE: CMD_INSTALL}}` |
| Subir ambiente local | `{{AGENTE: CMD_DEV}}` |
| Testes unitários | `{{AGENTE: CMD_TEST_UNIT}}` |
| Testes de um arquivo | `{{AGENTE: CMD_TEST_FILE}} <caminho>` |
| Testes de integração (banco real) | `{{AGENTE: CMD_TEST_INTEGRATION}}` |
| Teste de integração de uma fatia | `{{AGENTE: CMD_TEST_INTEGRATION}} <caminho do teste do handler>` |
| Testes de aceitação (BDD) | `{{AGENTE: CMD_TEST_ACCEPTANCE}}` |
| Lint e formatação | `{{AGENTE: CMD_LINT}}` |
| Checagem de tipos / análise estática | `{{AGENTE: CMD_TYPECHECK}}` |
| Regras de arquitetura | `{{AGENTE: CMD_ARCH_CHECK}}` |
| Frontend: subir em modo de desenvolvimento | `{{AGENTE: CMD_FRONTEND_DEV}}` |
| Frontend: testes de componente | `{{AGENTE: CMD_FRONTEND_TEST}}` |
| Frontend: testes e2e | `{{AGENTE: CMD_FRONTEND_E2E}}` |
| Frontend: lint e regras de fronteira | `{{AGENTE: CMD_FRONTEND_LINT}}` |
| **Verificação completa** (rodar antes de concluir) | `{{AGENTE: CMD_CHECK}}` |

Prefira rodar o teste do arquivo que você alterou antes da suíte inteira. Handlers são testados com banco real: ao alterar uma fatia, rode o teste de integração dela.

## Mapa de documentos

- Onde fica cada coisa / como adicionar algo: [CODEBASE_MAP.md](CODEBASE_MAP.md) · módulos, dependências e fluxos: [ARCHITECTURE.md](ARCHITECTURE.md) · código no padrão: [CODING_GUIDELINES.md](CODING_GUIDELINES.md) · testes: [TESTING.md](TESTING.md)
- Regras de negócio e termos: [docs/DOMAIN.md](docs/DOMAIN.md) · eventos: [docs/EVENTS.md](docs/EVENTS.md) · endpoints: [docs/API_GUIDELINES.md](docs/API_GUIDELINES.md) · frontend: [docs/FRONTEND.md](docs/FRONTEND.md) · logs, métricas, tracing: [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) · segurança: [SECURITY.md](SECURITY.md)
- Por que algo é como é: [docs/adr/](docs/adr/) · pacote compartilhado entre aplicações: [ARCHITECTURE.md §12](ARCHITECTURE.md#12-pacotes-base-compartilhados) · revisão e PR: [CONTRIBUTING.md](CONTRIBUTING.md)

## Fluxo de trabalho

1. **Entender.** Leia o `CODEBASE_MAP.md`, o código do módulo afetado e os testes existentes. Procure antes de presumir: se algo parece não existir, busque por nome e por conceito; antes de criar consulta ou regra, procure a existente. **Ao retomar** (sessão nova ou contexto resumido), releia do disco os arquivos que vai editar e os documentos da tarefa (design doc, descrição do PR) e confira o estado com `git log`/`git diff` (commit é fato; nota é intenção); nunca edite a partir de trecho lembrado. Por quê: ao resumir, o que se perde é o texto literal, e decisões tomadas sobre a lembrança dele saem piores.
2. **Planejar.** Antes de apresentar o plano, releia o pedido frase a frase: cada frase vira critério, não objetivo ou pergunta; a que não cai em lugar nenhum é requisito que some. Dimensione a demanda e responda o [checklist de design](#checklist-de-design):
   - **pequena** (uma fatia, sem contrato novo): checklist;
   - **média** (várias fatias do mesmo módulo): checklist + plano curto no formato "passo → como verificar", cada passo uma fatia completa verificável sozinha (nunca uma camada) e, se a mudança é difícil no código atual, a [preparação](CODING_GUIDELINES.md#passo-comum-a-vários-casos-de-uso) como primeiro passo;
   - **grande** (cruza módulos, contrato público ou migração) ou **complexa** (domínio novo, incerteza alta): design doc em `docs/design-docs/` com 2–3 alternativas e uma recomendação.
3. **Teste primeiro, em todo nível.** Todo comportamento novo começa por um teste que falha pelo motivo certo: unitário no domínio **e** integração do handler no caso de uso. Para bug: um teste que reproduz o sintoma exato relatado, com hipóteses ordenadas antes de instrumentar ([TESTING.md §9](TESTING.md#9-corrigindo-bugs)); depois procure a mesma causa nos outros pontos que usam o mesmo conceito (outros gates, outros handlers) e relate o que encontrou: corrija só o pedido, liste o resto. A saída do RED vai no relato; se a infraestrutura do teste ainda não existe, o RED é o primeiro teste que roda, e diga isso.
4. **Implementar o mínimo** para o teste passar.
5. **Refatorar** com os testes verdes.
6. **Verificar.** Rode `{{AGENTE: CMD_CHECK}}`.
7. **Atualizar a documentação** afetada (tabela no fim deste arquivo).

## Checklist de design

Responda antes de escrever código em toda demanda que muda comportamento (ajuste de texto, estilo ou dependência de desenvolvimento dispensa). Registre as respostas, uma linha cada, na descrição do PR ou no design doc; sem nenhum dos dois, no relato final. **Separe fato de decisão:** o que é fato você responde sozinho, com evidência buscada no código (quem importa, quem chama, onde está o teste), sem deduzir pelo nome da pasta; leve ao usuário só as decisões (regra de negócio com mais de uma resposta defensável é pergunta, nunca suposição), numeradas, cada uma com sua recomendação e um cenário de borda, em rodadas por dependência ([como perguntar](CODING_GUIDELINES.md#8-regras-para-código-escrito-por-agentes-de-ia)). A sigla entre parênteses é o conceito por trás da pergunta.

**Domínio e fronteiras**
1. **Qual o problema de negócio e com quais termos?** Use a linguagem ubíqua de [docs/DOMAIN.md](docs/DOMAIN.md); termo novo entra lá primeiro. (DDD)
2. **Qual módulo é o dono?** Se precisar de dados ou regras de outro módulo, use a API pública dele ou reaja a um evento; nunca tabelas ou classes internas. (bounded context, baixo acoplamento)
3. **É escrita ou leitura?** Escrita → Command + Handler na forma fixa (carregar → pré-condições → domínio → transição → gravar → efeitos após o commit → responder); leitura → Query + Handler com método de leitura no repository, mesmo que curto. Siga o [exemplo de referência](CODEBASE_MAP.md#exemplos-de-referência) do tipo. (CQS/CQRS, uma forma por operação)

**Responsabilidades**
4. **Quais artefatos e onde?** Liste cada arquivo novo ou alterado com seu papel segundo a [matriz de responsabilidades](ARCHITECTURE.md#41-responsabilidades). Fatia nova em `features/` ou alteração de uma existente? A lista final é registro do que o código pediu, não compromisso do plano. (SRP, separação de responsabilidades, vertical slice)
5. **Onde fica a regra de negócio? Este conceito já tem definição no código?** Na entidade/agregado, value object, enum ou domain service; nunca em controller, request, handler, listener ou repository. Busque o conceito ("disponível", "bloqueado") e o nome da regra antes de escrever a condição: se existe, use (dois gates do mesmo conceito chamam a mesma definição e citam o mesmo nome de regra); se precisa mudar, mude no único lugar. Condição de negócio montada no handler (`||`/`&&` de consultas ou predicados) é uma segunda definição. Se a demanda muda o sentido de um conceito (ex.: "pedido em aberto" passa a incluir rascunho), busque todos os leitores atuais (consultas, regras, telas, relatórios, eventos): cada um ganha um critério. Deixar um leitor na definição antiga cria duas definições do mesmo termo: é decisão, perguntada com a recomendação de unificar, nunca não objetivo nem suposição; se o usuário mantiver, o leitor antigo ganha nome próprio (outro termo no glossário de [docs/DOMAIN.md](docs/DOMAIN.md), outra consulta com outro nome), nunca o mesmo termo com dois sentidos. (domain model, information expert, uma definição por conceito)
6. **Quais invariantes podem quebrar?** Liste-as; a entidade as protege e cada uma tem teste. (fail fast)

**Framework e dependências**
7. **O framework ou uma biblioteca já adotada resolve isso?** Consulte a documentação oficial antes de criar abstração, utilitário ou infraestrutura (ex.: {{AGENTE: MECANISMO_DE_COMANDOS_E_EVENTOS_DO_FRAMEWORK}}, {{AGENTE: MECANISMO_DE_AUTORIZACAO_DO_FRAMEWORK}}, {{AGENTE: CLIENTE_HTTP_DO_FRAMEWORK}}, factories e fakes de teste do framework). Já existe arquivo ou recurso no projeto com o mesmo propósito? Existe forma mais atual na versão instalada? Solução própria só com justificativa. (framework first, KISS, DRY)
8. **Precisa de interface?** Só para sistema externo ou LLM (Port), mais de uma implementação real ou API pública entre módulos; fora disso, classe concreta. (ADR 0004, YAGNI)
9. **Há dependência nova, migração ou mudança de contrato público** (endpoint, evento, API de módulo, tool de agente)? Se sim, veja "Perguntar antes" (o aditivo que a demanda exige só é listado no relato). Contrato muda de forma compatível. (versionamento, expand and contract)

**Efeitos e falhas**
10. **Muda estado? O que é atômico e o que acontece depois?** Qual transição da tabela é usada; o que entra na transação do caso de uso (agregado, histórico, registros do mesmo módulo, nunca de outro módulo); o que é reação a evento, após o commit, registrada no mapa evento → reações; reação que grava estado de negócio tem entrega garantida (fila com retry ou reconciliação), não só o evento em processo. Outros módulos sabem por evento; consumidores idempotentes. Limite contado ou regra que lê um fato: algum outro caso de uso grava o fato que esta regra lê? Qual trava ou restrição os dois compartilham, e qual teste de concorrência prova? (máquina de estados, transação no caso de uso, EDA, write skew)
11. **O que acontece quando algo falha?** Sistema externo fora, timeout, entrada inválida, estado que não permite, regras violadas, execução repetida: qual categoria de erro e qual status? (ausência: [verbos com contrato de retorno](CODEBASE_MAP.md#verbos-com-contrato-de-retorno)) Pré-condições falham cedo; regras independentes voltam juntas. (resiliência, Problem Details)
12. **Quem pode executar e quais dados envolve?** Autorização pela `Policy` no mecanismo de autorização do framework; isolamento por tenant; dado pessoal segue [SECURITY.md](SECURITY.md). (segurança)

**Verificação e decisão**
13. **Como provar que funciona?** Quais testes: unitário da entidade/VO/enum, integração do handler com banco real, aceitação (BDD) se o comportamento for visível ao usuário. (TDD, BDD, pirâmide de testes)
14. **É a solução mais simples para o problema de hoje?** Sem generalizar para casos hipotéticos; duplicação de código aceitável até a terceira vez (na terceira, [passo comum](CODING_GUIDELINES.md#passo-comum-a-vários-casos-de-uso)); de conceito de negócio, nunca. (KISS, YAGNI, DRY)
15. **Alguma ADR ativa trata disso? Você está seguindo ou propondo substituir?** ADR nova só quando a decisão é difícil de reverter, surpreendente sem contexto e fruto de um trade-off real; proponha antes de implementar. (ADR)

## Ordem de verdade

Quando dois documentos, ou um documento e a configuração, discordam, vale nesta ordem: (1) a configuração e as verificações (lint, regras de arquitetura, tipos, scripts do `{{AGENTE: CMD_CHECK}}`); (2) ADR aceita; (3) os documentos do kit (`ARCHITECTURE.md`, `CODING_GUIDELINES.md`, ...); entre seções, a mais específica. Por quê: o que roda é o que o código cumpre; a prosa envelhece em silêncio. O de baixo é o defeito: corrija-o no mesmo PR e apresente a correção no relato (é mudança de convenção). **Nunca mude a configuração para seguir um documento:** aponte a divergência e pergunte.

## Limites

### Sempre
- **Framework first:** antes de criar ou escrever algo, conferir a versão no lockfile, consultar a documentação oficial **dessa versão** do framework e das bibliotecas adotadas ({{AGENTE: ex.: via ctx7}}) e usar o recurso nativo com a sintaxe e as APIs que ela recomenda; nunca API obsoleta ([CODING_GUIDELINES.md](CODING_GUIDELINES.md#versões-e-sintaxe-atual)).
- Seguir a [matriz de responsabilidades](ARCHITECTURE.md#41-responsabilidades): ORM e SQL só no repository (inclusive leituras); controller e request nunca recebem repository nem consultam o banco; handler orquestra sem ORM e sem regra de negócio; regra de negócio só em entidade, VO, enum e serviço de domínio; listeners e jobs delegam a handlers.
- Respeitar as regras de dependência: uma fatia de `features/` não importa outra; outros módulos só pela interface `<Modulo>Api` de `api/`, injetada.
- Escrever código de aplicação e de domínio em classes (funções de topo só na borda do framework) e nomear dependências pelo tipo em camelCase ([CODING_GUIDELINES.md](CODING_GUIDELINES.md#orientação-a-objetos)).
- Acessar sistema externo ou LLM sempre por um `Port` (interface em `ports/`, `Client` em `clients/`). "Não precisa de interface" vale para repository, recursos do framework e classes internas, nunca para fronteira externa.
- Validar entradas nas bordas (HTTP, filas, webhooks, arquivos) com schema.
- Guardar o estado da tarefa em arquivo, não na conversa: decisão e resposta do usuário vão para o design doc ou a descrição do PR (para [Decisões registradas](#decisões-registradas), se valem daqui em diante) no turno em que chegam, e os passos do plano são marcados lá ao serem concluídos. Por quê: qualquer sessão continua lendo só os arquivos.
- Fazer mudanças pequenas e focadas, um assunto por PR.
- Seguir a linguagem ubíqua do `docs/DOMAIN.md` em nomes de classes, funções e variáveis.

### Perguntar antes
- **Perguntar é não fazer** aquela mudança: escreva o pedido com a mudança exata (arquivo e trecho), as opções e uma recomendação; siga com o que não depende da decisão; termine o relato como "aguardando decisão", listando o que ficou parado. Avisar depois ("se preferir outra forma, me diga") não é perguntar. **Urgência não transforma decisão em suposição:** sob pressão de prazo, faça uma rodada curta de perguntas, cada uma com recomendação, e siga com o que não depende delas; nunca decida sozinho uma regra de negócio para ganhar tempo. **Alcance:** a autorização vale para a decisão perguntada, naquela demanda; cada nova demanda pergunta de novo, salvo o que estiver em [Decisões registradas](#decisões-registradas). **A demanda que pede a funcionalidade autoriza o que ela necessariamente exige:** migração aditiva (tabela, coluna, índice), endpoint novo, método novo na `<Modulo>Api` ou evento novo; liste cada um no relato. Continua sendo pergunta o que apaga, renomeia ou quebra (migração destrutiva, contrato incompatível), dependência nova, configuração de verificação e tudo o que a demanda não pede.
- Adicionar ou atualizar dependência; serviço novo de infraestrutura (ex.: no ambiente local); upgrade de versão **major** de dependência ou runtime.
- Migração de banco destrutiva (apaga ou renomeia) ou que a demanda não exige.
- Mudar contrato público de forma incompatível, ou criar um que a demanda não exige: endpoint, evento, API pública de módulo (inclusive método na `<Modulo>Api`).
- Apagar arquivos ou código cujo propósito você não entendeu.
- Mudar configuração de CI, deploy ou infraestrutura.
- Mudar uma convenção documentada (`CODING_GUIDELINES.md`, `ARCHITECTURE.md`, configuração de lint ou de arquitetura).
- Criar abstração, wrapper, utilitário ou infraestrutura própria para algo que o framework ou uma biblioteca adotada talvez já resolva.
- Criar interface para classe com uma só implementação fora dos casos de [CODING_GUIDELINES.md](CODING_GUIDELINES.md#interfaces-só-quando-há-motivo) (sistema externo, LLM, mais de uma implementação real, API pública). Recursos do framework (autorização, flags, cache, filas, HTTP, relógio) não ganham interface.

### Nunca
- Commitar segredos, `.env`, chaves ou dados reais de clientes.
- Desativar, pular ou enfraquecer testes para fazer a verificação passar.
- Contornar uma regra de lint ou de arquitetura mudando o estilo do código contra a convenção documentada, inclusive trocar a API recomendada do framework ou do ORM por SQL cru (ou outra forma menos segura) para escapar da regra; se a regra e a convenção ou a API do framework se contradizem, pergunte. SQL cru no repository continua permitido quando a API do ORM não expressa a consulta, com o motivo em comentário.
- Afrouxar configuração de lint, arquitetura, tipos ou testes para a verificação passar ({{AGENTE: ARQUIVOS_DE_VERIFICACAO}}, ex.: `.dependency-cruiser.mjs`, `tsconfig.json`, `phpstan.neon`, `tests/Arch`), inclusive regravar a baseline ({{AGENTE: ARQUIVO_DE_BASELINE}}, ex.: `.dependency-cruiser-known-violations.json`, `phpstan-baseline.neon`) para acomodar código novo: a baseline só diminui ([ARCHITECTURE.md §9](ARCHITECTURE.md#9-fitness-functions)).
- Acessar tabelas ou classes internas de outro módulo. Use a API pública do módulo ou eventos.
- Editar à mão `{{AGENTE: RAIZ_DO_FRONTEND}}/shared/api/generated/` (tipos gerados do contrato da API). Regenere com `{{AGENTE: CMD_GERAR_TIPOS}}`.
- Inventar APIs, funções ou opções de biblioteca. Se não tiver certeza, consulte a documentação ou o código.
- Rodar comandos destrutivos (force push, reset de banco compartilhado, `rm -rf`) sem pedido explícito.

## Definição de pronto

- [ ] Comportamento coberto por testes; `{{AGENTE: CMD_CHECK}}` passa; evidência do RED (saída do teste falhando) no PR.
- [ ] Verificado pelo resultado, não pelo rótulo: registre o que foi observado (saída do teste, resposta da API), não só "testes verdes"; diga o que não pôde ser verificado.
- [ ] Plano e decisões conferidos com o diff: nada fora do escopo, nada planejado ou decidido faltando.
- [ ] Nenhum `TODO` sem issue vinculada.
- [ ] Logs, métricas e traces para o fluxo novo, se aplicável.
- [ ] Documentação atualizada conforme a tabela abaixo.
- [ ] Descrição do PR explica o quê, o porquê e como foi verificado.
- [ ] Respostas do checklist de design na descrição do PR (sem PR: no design doc ou no relato).
- [ ] Ações de "perguntar antes" executadas listadas no relato, cada uma citando a autorização com as palavras exatas: a frase da demanda que a exige, a resposta literal do usuário ou a linha de Decisões registradas. Por quê: autorização sem evidência é preenchida com justificativa inventada.

## Decisões registradas

Autorizações que o usuário deu como válidas daqui em diante (data, decisão, alcance). Fora desta tabela, cada demanda pergunta de novo.

| Data | Decisão | Alcance |
|---|---|---|
| {{USUARIO: AAAA-MM-DD}} | {{USUARIO: ex.: pode adicionar dependências de desenvolvimento sem perguntar}} | {{USUARIO: ex.: só dependências de teste}} |

## Mantendo a documentação

| Se você mudou... | Atualize |
|---|---|
| Estrutura de pastas, módulo novo, ponto de entrada | `CODEBASE_MAP.md` |
| Fronteira entre módulos, estilo arquitetural, infraestrutura | `ARCHITECTURE.md` + nova ADR |
| Termo de negócio, regra ou invariante | `docs/DOMAIN.md` |
| Evento publicado ou consumido | `docs/EVENTS.md` |
| Endpoint ou contrato HTTP | `docs/API_GUIDELINES.md` (se mudar convenção) e a especificação da API |
| Comando de build, teste ou execução | este arquivo, seção Comandos |
| Convenção de código | `CODING_GUIDELINES.md` |
| Estrutura, convenção ou ferramenta do frontend | `docs/FRONTEND.md` |
| Ciclo de vida de um agregado | tabela de transições + `docs/DOMAIN.md` §5 |

Fidelidade dos documentos: caminhos e links citados são verificados no CI; um documento local (ex.: `CLAUDE.md` de módulo) não contradiz o global; regra que ainda está na baseline não é apresentada como cumprida; nenhum documento afirma sobre a configuração (lint, arquitetura) o que ela não faz, nem manda mudá-la contra o "Perguntar antes": se o kit precisa de uma exceção, ela já vem na configuração. Marcadores: `{{AGENTE: ...}}` você preenche a partir do projeto; `{{USUARIO: ...}}` é decisão do usuário, que você pergunta ou deixa como está, nunca inventa. Recurso que o projeto ainda não tem aparece como "ainda não existe: {{USUARIO: ...}}", nunca como afirmação.
