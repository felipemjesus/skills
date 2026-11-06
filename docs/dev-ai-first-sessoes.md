# Dump: dev-ai-first em uso real

Sessões do Claude Code usando a skill num backend real em produção (Node/Express/Sequelize; nome do produto, termos do domínio e caminhos anonimizados), num clone isolado do repositório, com configuração limpa (sem memórias, hooks ou plugins pessoais) e permissões restritas a comandos simples. Cada parte mostra o pedido do dev, as ações do agente (recolhidas) e a resposta final.

Anonimização: o nome do produto virou `Produto`, os termos que identificariam o cliente viraram genéricos (organização cliente, unidade, perfil independente), o caminho do projeto virou `<projeto>`, o da skill virou `<skill>` e os caminhos temporários e pessoais foram encurtados. Um achado de segurança foi descrito de forma genérica. Nenhum segredo foi lido: o `.env` real não estava no clone.

---

## 1. Preparar: leitura do projeto

**Dev:**

> /dev-ai-first preparar

<details><summary>16 ações do agente</summary>

- `$ cd <skill> && bash scripts/detectar-projeto.sh <projeto>`
- Read `<skill>/scripts/detectar-projeto.sh`
- Read `<skill>/references/preparar.md`
- Glob `*`
- Glob `{*.json,*.lock,*.toml,*.md,*.xml,*.yml,*.yaml,Makefile,.env*,.git*,Dockerfile*,docker-compose*,artisan,*.php,*.js,*.ts}`
- Glob `*/*/{composer.json,package.json,go.mod,pyproject.toml,pom.xml}`
- Glob `{AGENTS.md,CLAUDE.md,CODEBASE_MAP.md,ARCHITECTURE.md,CODING_GUIDELINES.md,.cursorrules,.cursor/**,.github/**,.windsurfrules,GEMINI.md}`
- Glob `**/*`
- Read `<projeto>/package.json`
- subagente: Stack e comandos
- subagente: Estrutura e arquitetura
- subagente: Domínio do negócio
- subagente: Qualidade e testes
- Read `<skill>/assets/kit/AGENTS.md`
- Read `<skill>/assets/kit/docs/adr/0002-monolito-modular-com-fatias-verticais.md`
- Read `<skill>/assets/kit/CODEBASE_MAP.md`

</details>

**Agente (resposta final):**

A leitura do projeto terminou. Antes de gravar qualquer arquivo preciso de algumas decisões suas, e de uma permissão.

### O que encontrei

- **Stack:** Node 20 · Express 4.22 · Sequelize 6.37 · PostgreSQL · Redis (ioredis) · cron dentro do processo · outbox de e-mail própria · zod (joi só em 3 arquivos). O frontend fica em outro repositório (`../produto-frontend`).
- **Organização:** convivem 4 estilos:
  1. **Legado por camada:** `routes/ → controllers/ → services/ → helpers/ / query/`, com SQL cru. É a maior parte do código e ainda recebe a maioria dos commits.
  2. **`src/app/agenda-digital`:** Controller → Action → uma query por arquivo, com injeção de dependência manual. O `agendar.js` tem 2.750 linhas.
  3. **`src/app/integracao` e `integracoes-parceiro`:** a mesma base, com `repositories/`, `schemas.js`, erro tipado e cliente HTTP isolado.
  4. **`src/app/plantoes`:** funções-fábrica, transições de estado puras e testes com banco real. É o estilo mais recente.
- **Comparado ao estilo do kit:** a ADR 0002 (módulos com fatias verticais e domínio rico) não é seguida. As ADRs 0003, 0004 e 0005 são seguidas em parte. Uma área de `src/app` importa arquivos internos de outra, e não há fachada pública entre elas.
- **Qualidade:**
  - Não existe comando único de verificação, e `npm test` sai com erro de propósito.
  - O CI só faz deploy: não roda lint nem testes.
  - Os testes com banco só rodam se uma variável de ambiente estiver ligada.
  - Os testes de 15 arquivos usam vitest, mas nenhum script npm chama o vitest.
  - O prettier tem configuração, mas não está instalado.
  - Não há verificação de tipos nem de arquitetura.
- **Domínio:**
  - "Cliente" no código é o **organização cliente** (é o tenant).
  - O isolamento entre clientes é feito consulta a consulta.
  - O status da guia é o par `status` + `presenca`, em inteiros espalhados pelo código, sem enum central.

### Decisões (cada uma com recomendação)

1. **Permissão de shell.** O Bash está bloqueado nesta sessão. Sem ele não consigo criar a branch `dev-ai-first/preparar`, copiar o kit nem rodar `listar-marcadores.sh`, `verificar-links.sh` e `npm run lint`. **Recomendo liberar o Bash** para esses comandos. A alternativa é você criar a branch; aí eu gravo os cerca de 20 arquivos um a um e o relatório sai sem a verificação automática.

2. **Que estilo o código novo segue?** Esta é a decisão central.
   - **(a) Estilo do kit puro** (`src/modules/<x>/features/...`, entidades ricas, Ports): fica muito distante do código atual.
   - **(b) Estilo atual:** são 4 estilos, e o agente imitaria o vizinho, qualquer que seja.
   - **(c) Recomendo:** o código novo vai em `src/app/<área>/` com pastas por tipo (`routes/`, `controllers/`, `actions/`, `queries/` ou `repositories/`). É a variante "opção 6" que a ADR 0002 aceita. As regras do kit entram como meta: controller fino, regra fora do controller, cliente externo isolado e uma área chamando outra só por um ponto de entrada nomeado. O legado vai para a lista de dívidas (`ARCHITECTURE.md` §11).

3. **Qual área de `src/app` é a referência a imitar?** **Recomendo `app/integracao/agendamentos`** para escrita, com `repositories/`, `schemas.js` e erro tipado. Para transição de estado, recomendo `app/plantoes`. Não recomendo `agenda-digital` por causa do `agendar.js` gigante.

4. **Descrição em uma frase.** Proposta: *"Backend do Produto: agendamento e faturamento de serviços para organizações clientes e suas unidades, estabelecimentos e profissionais."* Está certa?

5. **Frontend.** Proposta: remover o `docs/FRONTEND.md` e as linhas de frontend do `AGENTS.md`, apontando para o repositório `produto-frontend`. Ok?

6. **Perfil `userType = 4`.** Não achei o significado no código. Você sabe qual é? Se ficar em branco, sai no glossário como "a definir".

7. **Branch de deploy.** Push na `main` vai para produção e push na `develop` vai para o beta. Recomendo registrar no `AGENTS.md` a regra: "nunca dar push em `main` nem em `develop` sem pedido explícito". Ok?

Pode responder "ok" para aceitar todas as recomendações. Nada foi gravado nem commitado até agora.


---

## 2. Preparar: decisões aceitas, documentos gerados

**Dev:**

> ok, pode seguir com as recomendações. Sobre a 1: liberei o Bash para comandos simples; rode um comando por chamada, sem laços for. Sobre a 6: não sei, deixe como a definir.

<details><summary>93 ações do agente</summary>

- `$ git -C <projeto> checkout -b dev-ai-first/preparar`
- `$ ls <projeto>/ <projeto>/docs /ho`
- `$ cp -rn <skill>/assets/kit/. <projeto>/`
- `$ git -C <projeto> status --porcelain`
- `$ cp -n <skill>/assets/kit/CLAUDE.md <projeto>/CLAUDE.md`
- Read `<skill>/assets/kit/ARCHITECTURE.md`
- Read `<skill>/assets/kit/CODEBASE_MAP.md`
- Read `<skill>/assets/kit/CLAUDE.md`
- Read `<skill>/assets/kit/CODING_GUIDELINES.md`
- Read `<skill>/assets/kit/TESTING.md`
- Read `<skill>/assets/kit/docs/DOMAIN.md`
- Read `<skill>/assets/kit/CONTRIBUTING.md`
- Read `<skill>/assets/kit/SECURITY.md`
- Read `<skill>/assets/kit/docs/adr/README.md`
- Read `<skill>/assets/kit/.github/pull_request_template.md`
- Read `<skill>/assets/kit/docs/adr/0003-eventos-com-recursos-do-framework.md`
- Read `<skill>/assets/kit/docs/adr/0004-interfaces-so-em-fronteiras.md`
- Read `<skill>/assets/kit/docs/adr/0005-framework-first.md`
- Read `<skill>/assets/kit/docs/adr/0001-registrar-decisoes-de-arquitetura.md`
- Read `<skill>/assets/kit/docs/adr/0000-template.md`
- Read `<skill>/assets/kit/docs/design-docs/0000-template.md`
- Read `<skill>/assets/kit/docs/runbooks/0000-template.md`
- `$ ls -R <projeto>/src/app/integracao <projeto>`
- `$ ls <projeto>/src <projeto>/src/a`
- `$ npm run lint 2>&1 | tail -n 15`
- `$ npm run test:agenda-digital-agendamentos:unit 2>&1 | tail -n 12`
- Write `<projeto>/AGENTS.md`
- Read `/tmp/sessao/tasks/berh0ainr.output`
- Write `<projeto>/CLAUDE.md`
- Write `<projeto>/CODEBASE_MAP.md`
- Read `/tmp/sessao/tasks/bcaqzxer3.output`
- Edit `<projeto>/AGENTS.md`
- Edit `<projeto>/AGENTS.md`
- Edit `<projeto>/AGENTS.md`
- Edit `<projeto>/AGENTS.md`
- Write `<projeto>/ARCHITECTURE.md`
- Grep `pg_advisory|afterCommit|postSendPushNotifications`
- Write `<projeto>/CODING_GUIDELINES.md`
- Grep `objError|require\('decimal.js'\)`
- Grep `decimal\.js`
- Edit `<projeto>/CODING_GUIDELINES.md`
- Write `<projeto>/TESTING.md`
- Write `<projeto>/docs/DOMAIN.md`
- Write `<projeto>/docs/EVENTS.md`
- Write `<projeto>/docs/API_GUIDELINES.md`
- Write `<projeto>/docs/OBSERVABILITY.md`
- Write `<projeto>/SECURITY.md`
- Write `<projeto>/CONTRIBUTING.md`
- Write `<projeto>/.github/pull_request_template.md`
- Grep `require\('bcrypt'\)|CERTIFICADO_INTEGRACAO_SECRET`
- `$ git -C <projeto> log --merges -5 --format=%s`
- Write `<projeto>/docs/adr/0000-template.md`
- Write `<projeto>/docs/adr/0001-registrar-decisoes-de-arquitetura.md`
- Write `<projeto>/docs/adr/0002-codigo-novo-em-src-app-com-pastas-por-tipo.md`
- Write `<projeto>/docs/adr/0003-transacao-no-caso-de-uso-e-efeitos-apos-commit.md`
- Write `<projeto>/docs/adr/0004-abstracao-so-em-fronteiras.md`
- Write `<projeto>/docs/adr/0005-framework-first.md`
- Write `<projeto>/docs/adr/README.md`
- Write `<projeto>/docs/design-docs/0000-template.md`
- Write `<projeto>/docs/runbooks/0000-template.md`
- `$ bash <skill>/scripts/verificar-links.sh <projeto>`
- `$ bash <skill>/scripts/listar-marcadores.sh <projeto>`
- `$ wc -l <projeto>/AGENTS.md`
- Edit `<projeto>/AGENTS.md`
- Edit `<projeto>/ARCHITECTURE.md`
- Edit `<projeto>/docs/DOMAIN.md`
- Edit `<projeto>/SECURITY.md`
- subagente: Revisar docs gerados vs código
- Edit `<projeto>/CODEBASE_MAP.md`
- Edit `<projeto>/CODEBASE_MAP.md`
- Edit `<projeto>/CODEBASE_MAP.md`
- Edit `<projeto>/ARCHITECTURE.md`
- Edit `<projeto>/ARCHITECTURE.md`
- Edit `<projeto>/ARCHITECTURE.md`
- Edit `<projeto>/ARCHITECTURE.md`
- Edit `<projeto>/ARCHITECTURE.md`
- Edit `<projeto>/ARCHITECTURE.md`
- Edit `<projeto>/ARCHITECTURE.md`
- Edit `<projeto>/SECURITY.md`
- Edit `<projeto>/docs/EVENTS.md`
- Edit `<projeto>/docs/EVENTS.md`
- Edit `<projeto>/docs/adr/0003-transacao-no-caso-de-uso-e-efeitos-apos-commit.md`
- Edit `<projeto>/docs/DOMAIN.md`
- Edit `<projeto>/docs/DOMAIN.md`
- Edit `<projeto>/docs/DOMAIN.md`
- Edit `<projeto>/docs/OBSERVABILITY.md`
- Edit `<projeto>/docs/OBSERVABILITY.md`
- Edit `<projeto>/TESTING.md`
- Edit `<projeto>/CODING_GUIDELINES.md`
- Edit `<projeto>/docs/API_GUIDELINES.md`
- `$ bash <skill>/scripts/verificar-links.sh <projeto> | tai`
- `$ bash <skill>/scripts/listar-marcadores.sh <projeto> | h`
- `$ git -C <projeto> status --short`

</details>

**Agente (resposta final):**

Criei 22 documentos para agentes na branch `dev-ai-first/preparar`. Nada foi commitado e nenhum arquivo existente foi alterado. Restam 58 decisões suas em aberto, marcadas nos documentos como "a definir".

### Prontidão para agentes

O principal problema hoje é que **um agente não tem como provar que terminou**: o CI só faz deploy, não existe comando único de verificação e o lint já está vermelho na `main`.

| # | Item | Status | Evidência | Prioridade |
|---|---|---|---|---|
| 2 | Comando único de verificação | falta | `npm test` sai com erro de propósito | **alta** |
| 3 | Rodar o teste de um arquivo só | ok | `DEBUG=false node --test <arquivo>` | — |
| 4 | Testes unitários rápidos | parcial | a suíte de agenda-digital rodou: 785 testes passaram em cerca de 48 s | baixa |
| 5 | Teste de integração com banco real | parcial | existe em 3 áreas, mas só roda com variável de ambiente ligada e não há banco de teste padrão | **alta** |
| 6 | Lint e formatador | parcial | `npm run lint` acusa **675 erros**; o prettier tem configuração mas não está instalado | média |
| 7 | Checagem de tipos | falta | — | média |
| 8 | Regras de arquitetura verificadas | falta | — | média |
| 9 | CI roda verificação nos PRs | falta | os workflows só fazem migrate e deploy | média |
| 10 | Exemplos de referência nomeados | ok, com ressalvas | tabela no `CODEBASE_MAP.md` | — |
| 12 | Ambiente local reproduzível | parcial | composes separados em `.docker/` | **alta** |
| 13 | Segredos fora do repositório | ok | `.env` está no `.gitignore` | baixa |

### O que a revisão independente encontrou

Um subagente sem o histórico da conversa conferiu cerca de 140 afirmações dos documentos contra o código. 123 estavam corretas e corrigi as outras 16. Duas merecem sua atenção:
- **Um endpoint de leitura por id não filtra pelo tenant:** a busca é feita só pelo id do registro. Pode ser intencional ou um furo de isolamento entre clientes. Registrei como dívida em `ARCHITECTURE.md` §11 e avisei no próprio exemplo que essa parte não deve ser imitada.
- **O push do agendamento sai dentro da transação** (em `agendar.js`): se a transação for desfeita, o aviso já foi enviado.

### Decisões pendentes

Recomendação entre parênteses.
- **Verificação:** criar um script único que roda lint e testes, e colocá-lo no CI (sim). Congelar os 675 erros de lint atuais como referência, para que só piorar falhe (sim).
- **Testes:** padronizar em `node:test` (sim; os 15 arquivos em vitest hoje não rodam em lugar nenhum). Ter um compose de banco de teste padrão para a equipe (sim).
- **Arquitetura:** formalizar um ponto de entrada para outras áreas chamarem a agenda-digital, ou manter `AgendarAction.execute` como contrato (manter por ora).
- **Processo:** PR vai para `develop` ou `main`; quantas aprovações; merge ou squash.
- **Metas, donos, LGPD e e-mail de segurança:** só você pode responder.

### O que ficou de fora

- Removi o documento de frontend do kit, porque o frontend fica em outro repositório.
- Ficaram registrados como "ainda não existe": checagem de tipos, regras de arquitetura, comando único de verificação, varredura de segredos e verificação no CI.
- As ADRs foram adaptadas à decisão que você aceitou: código novo em `src/app/<área>/`, com as regras do kit como meta.

### Verificação

- `listar-marcadores.sh`: nenhum marcador de preenchimento do agente pendente; 58 decisões suas.
- `verificar-links.sh`: 163 links conferidos. Os 20 quebrados são todos de um documento antigo, `docs/auditoria-memoria-conexoes-2026-09-25.md`, que aponta para `/Users/<dev>/...` e que não alterei.
- `AGENTS.md` tem 145 linhas.

**Não verifiquei:**
- as suítes de teste com banco real e o e2e (não há banco de teste configurado);
- os comandos de subir o ambiente local;
- se o deploy de produção encontra o `docker-compose-prod.yml`.

O `cp` do kit foi negado, então gravei cada arquivo com Write.

### Próximo passo

Recomendo como primeira demanda criar o **comando único de verificação** (lint dos arquivos alterados mais as suítes unitárias) e rodá-lo no CI. Sem ele, o agente não tem como provar que terminou.

Quer revisar o diff antes de eu commitar?


---

## 3. Preparar: correção do dev

**Dev:**

> Correção da decisão 6: userType = 4 é perfil independente. Atualize o glossário e onde mais esse perfil aparecer. Ainda não commite.

<details><summary>7 ações do agente</summary>

- Grep `\| 4 \||userType|perfil 4|independente`
- Grep `(?i)independente|userType\s*===?\s*4|userType\s*[!=]==?\s*['"]4`
- Read `<projeto>/src/helpers/verify.js`
- Read `<projeto>/src/database/models/adOrganizacao.js`
- Edit `<projeto>/docs/DOMAIN.md`
- Edit `<projeto>/docs/DOMAIN.md`
- `$ bash <skill>/scripts/listar-marcadores.sh <projeto> | h`

</details>

**Agente (resposta final):**

Atualizei o `docs/DOMAIN.md`: `userType = 4` agora é "Perfil independente". Nenhum outro documento citava esse perfil. Nada foi commitado.

- **Tabela de perfis:** a linha 4 deixou de ser "a definir" e passou a citar a evidência no código.
- **Glossário:** entrou o termo "Perfil independente", com o nome usado no código (`perfilIndependente`) e a distinção para o perfil comum (`userType = 3`).

**Correção do que eu tinha informado antes:** o perfil existe no código. `src/helpers/verify.js:173` traduz o tipo 4 para `'perfilIndependente'`. A leitura anterior tinha errado ao dizer que ele não aparecia em lugar nenhum.

**Uma pergunta nova:** o organização cliente tem um campo `orgIndependente` (`src/database/models/adOrganizacao.js:12`) que talvez tenha relação com esse perfil. Por exemplo, o perfil independente pode ser representado como um "organização cliente" de um unidade só. Não afirmei essa relação no glossário e deixei a definição de negócio marcada "a definir" para você confirmar.

Com isso, as decisões suas em aberto passaram de 58 para 59. Não sobrou nenhuma lacuna que eu pudesse preencher pelo código.


---

## 4. Entregar: planejamento (sessão nova)

**Dev:**

> /dev-ai-first Criar o comando único de verificação do backend: lint dos arquivos alterados e as suítes unitárias, e rodar no CI nos PRs.

<details><summary>25 ações do agente</summary>

- `$ bash <skill>/scripts/detectar-projeto.sh <projeto>`
- Read `<skill>/references/entregar.md`
- `$ node -e 'const p=require("./package.json");console.log(JSON.stringify({scripts:p.scripts,engines:p.engines,devDependencies:p.devDependencies},null,1))'; ls -la `
- `$ cat .github/workflows/develop.yml; ls .github/scripts; cat .eslintignore; cat .eslintrc.json; ls test test/*; ls .git/dev-ai-first 2>/dev/null; git remote -v`
- `$ cat TESTING.md; grep -n -i -A3 "branch\|ci\b\|verifica" CONTRIBUTING.md | head -80`
- `$ ls node_modules | wc -l; ls vitest.config.* 2>/dev/null; find test -name '*.test.js' | wc -l; find test/app -name '*.test.js' | wc -l; grep -rl "from 'vitest'\|`
- `$ mkdir -p /tmp/sessao/scratchpad && S=/tmp/cl`
- `$ npm run -s test:email-outbox --prefix <projeto> 2>&1 | tail -12`
- `$ npm run -s test:integracao-agendamentos:unit --prefix <projeto> 2>&1 | tail -9`
- `$ npm run -s test:integracoes-parceiro:unit --prefix <projeto> 2>&1 | tail -9`
- `$ npm run -s test:integracao-certificado:unit --prefix <projeto> 2>&1 | tail -9`
- Write `/tmp/sessao/scratchpad/medir-todos.js`
- `$ node /tmp/sessao/scratchpad/medir-todos.js /`
- `$ npx --prefix <projeto> eslint --no-inline-config --no-error-on-unmatched-pattern -c ~`
- `$ node -e 'const r=require(process.argv[1]);const c=r.filter(f=>f.errorCount>0);const t=c.reduce((a,f)=>a+f.errorCount,0);console.log("arquivos lintados",r.length`
- `$ cat <projeto>/vitest.config.js`
- `$ npx --prefix <projeto> vitest run --root <projeto>`
- `$ npx --prefix <projeto> vitest run --root <projeto>`
- `$ git -C <projeto> checkout -b chore/verificacao-unica-ci`
- `$ tail -12 /tmp/sessao/scratchpad/todos.tap`
- `$ grep -E "^not ok" /tmp/sessao/scratchpad/tod`
- `$ grep -A12 -E "^not ok" /tmp/sessao/...`
- `$ node --test <projeto>/test/prontuario/registro.test.js 2>&1 | grep -E "^ℹ (pass|fail)|Error|expe`
- Write `<projeto>/.git/dev-ai-first/chore/verificacao-unica-ci.md`
- Write `/tmp/sessao/scratchpad/tarefa-verificacao-unica-ci.md`

</details>

**Agente (resposta final):**

Planejamento feito e medições rodadas. Ainda não escrevi código: algumas decisões mudam o comportamento do comando, e preciso que você responda antes.

### O que medi

| O que | Resultado |
|---|---|
| As 5 suítes unitárias que têm script (`test:*:unit` + `test:email-outbox`) | **844 testes, todos passam**, cerca de 50 s |
| Os outros arquivos de teste sem banco (410 arquivos, sem script) | 1995 testes: **15 falham** em 10 arquivos (ex.: `test/prontuario/registro.test.js`, que também falha rodando sozinho), cerca de 4 min |
| Testes vitest em `test/app/` (nenhum script roda) | 115 de 116 passam; falha `ram/actions/sincronizar.test.js` |
| Lint do projeto | 675 erros em 158 dos 2236 arquivos |

### Plano

O comando seria `npm run verificar`, um script Node sem dependência nova (`scripts/verificar.js`), com teste próprio. Ele roda:
- o lint nos arquivos alterados em relação à base, contando também os não commitados;
- as suítes unitárias.

Se qualquer etapa falhar, o comando falha e diz qual foi. No CI entra um workflow novo, `.github/workflows/verificacao.yml`:
- dispara em `pull_request`;
- usa Node 20, `npm ci`, sem segredos e sem banco;
- compara com a branch de destino do PR.

Os workflows de deploy não mudam. A mudança no CI está autorizada pela própria demanda ("rodar no CI nos PRs").

### Decisões (responder "sim" aceita a recomendação)

1. **Quais testes entram?** Recomendo só as suítes com script `test:*:unit`, descobertas pelo nome. Para isso o `email-outbox` ganha o alias `test:email-outbox:unit`, e uma suíte nova entra só de criar o script.
   - O caso difícil: incluir os 410 arquivos deixaria o CI vermelho desde o primeiro dia por causa das 15 falhas que já existem. Para evitar isso eu teria que criar uma lista de arquivos ignorados, e o `AGENTS.md` proíbe pular teste para a verificação passar.
   - Sugiro abrir uma issue para corrigir esses 10 arquivos e só depois incluí-los.
2. **Os testes vitest de `test/app` entram?** Recomendo que não por enquanto: um deles falha, e o `TESTING.md` ainda tem em aberto se o projeto padroniza em `node:test` ou cria um script para o vitest.
3. **Regra do lint nos alterados:** recomendo "o arquivo não pode ter mais erros do que tinha na base", como o `AGENTS.md` já diz. A alternativa é exigir zero erro.
   - O caso difícil: corrigir uma linha em `FormularioInternacaoService.js`, que tem 57 erros. Com "zero erro", essa correção obrigaria a limpar o arquivo inteiro.
   - A contagem tem uma brecha: corrigir um erro e criar outro no mesmo arquivo passa.
4. **Base local:** recomendo `main` como padrão, com `--base <ref>` para trocar. No CI a base é sempre o destino do PR, então tanto faz se os PRs vão para `main` ou `develop`.
5. **Nome:** `npm run verificar`, em português como os outros scripts (`worker:email`, `pacientes:...`). Ok?

### Outros pontos

- **Branch:** criei `chore/verificacao-unica-ci` a partir de `dev-ai-first/preparar`, porque é nela que estão os documentos do projeto e eles ainda não estão na `main`. O `CONTRIBUTING.md` pede o código da issue no nome da branch. Se houver uma issue (ex.: `ISSUE-xxxx`), me passe que eu renomeio.
- **Arquivo da tarefa:** a permissão bloqueou a escrita em `.git/dev-ai-first/`. Deixei o arquivo em `/tmp/sessao/scratchpad/tarefa-verificacao-unica-ci.md`. Esse lugar não sobrevive a outra sessão; se você liberar a escrita, eu movo o arquivo.
- **Check obrigatório:** fazer o check bloquear o merge é configuração de proteção de branch no GitHub. Isso fica com você depois do primeiro PR.

Aguardando decisão nos pontos 1 a 5. Nada foi implementado ainda.


---

## 5. Entregar: implementação

**Dev:**

> ok, pode seguir com as recomendações nos 5 pontos. Não há issue, mantenha o nome da branch. Sobre o arquivo da tarefa: a skill foi atualizada, ele agora fica em .dev-ai-first/<branch>.md na raiz do projeto; mova-o para lá. Não commite: eu peço quando quiser.

<details><summary>125 ações do agente</summary>

- Grep `dev-ai-first|gitignore|versionar`
- Grep `dev-ai-first`
- Read `/tmp/sessao/scratchpad/tarefa-verificacao-unica-ci.md`
- Write `<projeto>/.dev-ai-first/chore-verificacao-unica-ci.md`
- `$ node -p "require('<projeto>/node_modules/eslint/package.json').version"`
- `$ npx ctx7@latest library ESLint "Node.js API ESLint class lintText filePath overrideConfigFile useEslintrc"`
- `$ npx ctx7@latest docs /eslint/eslint/v8.57.1 "Node.js API ESLint class constructor options overrideConfigFile allowInlineConfig, lintText with filePath option, i`
- `$ head -40 <projeto>/test/scripts/backfill-estabelecimento-cnes.test.js`
- `$ grep -n "require.main\|module.exports\|^async function\|^function" <projeto>/scripts/backfill-es`
- Write `<projeto>/test/scripts/verificar.test.js`
- Write `<projeto>/scripts/verificar.js`
- `$ DEBUG=false node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^✔|^ℹ (tests`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^✔|^ℹ (tests|pass|fail)"`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^\s+(AssertionError|TypeErr`
- Write `<projeto>/scripts/verificar.js`
- Edit `<projeto>/scripts/verificar.js`
- Edit `<projeto>/scripts/verificar.js`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^✔|^ℹ (tests|pass|fail)|`
- Read `<projeto>/package.json`
- Edit `<projeto>/package.json`
- Edit `<projeto>/package.json`
- `$ npm run verificar --prefix <projeto> > /tmp/sessao/...`
- `$ grep -vE "^✔|^\s+✔|^▶|duration_ms|^ℹ (suites|cancelled|todo)" /tmp/sessao/...`
- `$ time (node <projeto>/node_modules/eslint/bin/eslint.js --no-inline-config -c ~/projet`
- Edit `<projeto>/scripts/verificar.js`
- Edit `<projeto>/scripts/verificar.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^ℹ (tests|pass|fail)|Err`
- `$ npm run verificar --prefix <projeto> > /tmp/sessao/...`
- `$ grep -E "^==|^ok|^falhou|^nenhum|→|^ℹ (tests|pass|fail|skipped)" /tmp/sessao/...`
- Read `<projeto>/src/services/FormularioInternacaoService.js`
- Grep `assert\.(equal|deepEqual|strictEqual)`
- Edit `<projeto>/src/services/FormularioInternacaoService.js`
- Edit `<projeto>/test/email-outbox/retry-policy.test.js`
- `$ npm run verificar --prefix <projeto> > /tmp/sessao/...`
- `$ grep -E "^==|^ok|^falhou|^nenhum|→|^    [0-9]+:|^ℹ fail" /tmp/sessao/...`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/scripts/verificar.js`
- Edit `<projeto>/scripts/verificar.js`
- Edit `<projeto>/scripts/verificar.js`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^ℹ (tests|pass|fail)|Ass`
- Edit `<projeto>/scripts/verificar.js`
- Edit `<projeto>/scripts/verificar.js`
- Edit `<projeto>/scripts/verificar.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^ℹ (tests|pass|fail)|Err`
- `$ npm run verificar --prefix <projeto> > /tmp/sessao/...`
- `$ grep -E "^==|^ok|^falhou|^nenhum|→|^    [0-9]+:|^ℹ fail|^✖" /tmp/sessao/...`
- Edit `<projeto>/test/email-outbox/retry-policy.test.js`
- Edit `<projeto>/src/services/FormularioInternacaoService.js`
- Edit `<projeto>/src/services/FormularioInternacaoService.js`
- `$ npm run verificar --prefix <projeto> > /tmp/sessao/...`
- `$ grep -E "^== Lint|^ok|^falhou|→" /tmp/sessao/...`
- Edit `<projeto>/src/services/FormularioInternacaoService.js`
- `$ git -C <projeto> status --short`
- `$ npx ctx7@latest library "actions/checkout" "latest major version fetch-depth usage"`
- `$ npx ctx7@latest docs /actions/checkout/v6 "fetch-depth 0 full history for pull_request, persist-credentials, Node runtime requirements"`
- `$ npx ctx7@latest library "actions/setup-node" "node-version cache npm latest major version"`
- `$ npm ci --dry-run --ignore-scripts --prefix <projeto> 2>&1 | tail -5`
- `$ node -e 'const r=process.argv[1];const p=require(r+"/package.json");const l=require(r+"/package-lock.json");const root=l.packages[""];const d=(a,b)=>JSON.string`
- Glob `.env*`
- Write `<projeto>/.github/workflows/verificacao.yml`
- Edit `<projeto>/.github/workflows/verificacao.yml`
- Glob `node_modules/{js-yaml,yaml}/package.json`
- `$ node -e 'const r=process.argv[1];const y=require(r+"/node_modules/js-yaml");const w=y.load(require("fs").readFileSync(r+"/.github/workflows/verificacao.yml","ut`
- `$ npm run verificar --prefix <projeto> -- --base dev-ai-first/preparar > /tmp/sessao/...`
- `$ ls ~/.nvm/versions/node`
- Glob `*/bin/node`
- `$ grep -E "^== Lint|^ok|^falhou|→|^nenhum" /tmp/sessao/...`
- `$ node <projeto>/scripts/verificar.js --base origin/nao-existe 2>&1 | tail -3; echo "exit=${PIPEST`
- `$ npm run verificar --prefix <projeto> -- --base origin/nao-existe > /tmp/sessao/...`
- Read `/tmp/sessao/scratchpad/verificar-base-invalida.log`
- Grep `CMD_CHECK|CI (não|\*\*não\*\*)|não roda (lint|nenhum)|Verificação completa|Até lá|até existir o comando|lint dos arquivos alterados \+|test:email-outbox|scripts/`
- Read `<projeto>/AGENTS.md`
- Edit `<projeto>/AGENTS.md`
- Edit `<projeto>/AGENTS.md`
- Edit `<projeto>/AGENTS.md`
- Grep `Comportamento coberto por teste`
- Edit `<projeto>/AGENTS.md`
- Read `<projeto>/CONTRIBUTING.md`
- Edit `<projeto>/CONTRIBUTING.md`
- Read `<projeto>/TESTING.md`
- Edit `<projeto>/TESTING.md`
- Edit `<projeto>/TESTING.md`
- Edit `<projeto>/ARCHITECTURE.md`
- Read `<projeto>/CODEBASE_MAP.md`
- Edit `<projeto>/CODEBASE_MAP.md`
- `$ bash <skill>/scripts/verificar-links.sh <projeto>`
- Edit `<projeto>/.dev-ai-first/chore-verificacao-unica-ci.md`
- Read `<skill>/references/revisar.md`
- subagente: Revisão independente do diff
- Read `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/scripts/verificar.js`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^ℹ (tests|pass|fail)|^\s`
- Write `<projeto>/scripts/verificar.js`
- Edit `<projeto>/CONTRIBUTING.md`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^ℹ (tests|pass|fail)|^\s`
- Edit `<projeto>/src/services/FormularioInternacaoService.js`
- `$ npm run verificar --prefix <projeto> > /tmp/sessao/...`
- Edit `<projeto>/src/services/FormularioInternacaoService.js`
- `$ grep -E "^==|^ok|^falhou|→|^    [0-9]+:|^ℹ fail" /tmp/sessao/...`
- `$ npm run verificar --prefix <projeto> > /tmp/sessao/...`
- `$ git -C <projeto> status --short`
- `$ grep -E "^== Lint|^ok|^falhou|^ℹ (tests|fail)" /tmp/sessao/...`
- ToolSearch
- SendMessage
- Edit `<projeto>/.dev-ai-first/chore-verificacao-unica-ci.md`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- Edit `<projeto>/test/scripts/verificar.test.js`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^ℹ (tests|pass|fail)|^\s`
- Edit `<projeto>/scripts/verificar.js`
- `$ node --test <projeto>/test/scripts/verificar.test.js 2>&1 | grep -E "^✖|^ℹ (tests|pass|fail)" | `
- `$ npm run verificar --prefix <projeto> > /tmp/sessao/...`
- `$ grep -E "^== Lint|^ok|^falhou|^ℹ (tests|fail)" /tmp/sessao/...`
- Edit `<projeto>/.dev-ai-first/chore-verificacao-unica-ci.md`

</details>

**Agente (resposta final):**

O comando `npm run verificar` está pronto e testado, e o workflow que o roda em todo PR também. Nada foi commitado, como você pediu.

**Critérios**

| Critério | Situação |
|---|---|
| Comando único | atendido: `npm run verificar` (`scripts/verificar.js`) |
| Lint dos arquivos alterados | atendido: compara com o ponto em que a branch saiu da `main` e conta commits, alterações não commitadas e arquivos novos. Um arquivo só reprova se ficar com mais erros do que tinha |
| Suítes unitárias | atendido: roda todo script `test:*:unit`. Criei o alias `test:email-outbox:unit` e o `test:verificar:unit`, para o próprio comando ser testado |
| CI nos PRs | atendido no código: `.github/workflows/verificacao.yml` roda em todo PR, com Node 20, sem banco e sem segredos. Os workflows de deploy não mudaram |

**Como verifiquei**
- **Teste primeiro:** os testes do script falharam pela asserção antes da implementação e agora passam (12 de 12).
- **Sabotagem:**
  - coloquei um erro de lint em `FormularioInternacaoService.js`: o comando saiu com erro, mostrou "57 → 60 erros" e listou só as regras que aumentaram;
  - inverti uma asserção do email-outbox: o comando também falhou e apontou essa suíte;
  - uma linha limpa nesse mesmo arquivo legado passou. Desfiz a sabotagem e o `git status` voltou limpo.
- **Execução final:** passou o lint e as 6 suítes, 856 testes sem falha, em cerca de 1 minuto.
- **Revisão independente:** um subagente sem o histórico da conversa revisou o diff duas vezes e deu "pronto" nas duas, sem bloqueantes. Ele achou alguns pontos menores, que corrigi:
  - caminhos com acento quebravam a leitura do git;
  - faltava um teste com um repositório git de verdade;
  - o código era assíncrono sem precisar.

**O que não pude verificar**
- O workflow rodando no GitHub Actions: só acontece depois do push.
- Node 20: só há Node 24 nesta máquina.
- `npm ci`: a permissão bloqueou. Conferi que o `package-lock.json` bate com o `package.json`.

**Ações que precisavam de autorização**
- Workflow novo em `.github/`, autorizado pela demanda: "rodar no CI nos PRs".
- Novos scripts no `package.json` e documentação atualizada (`AGENTS.md`, `TESTING.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, `CODEBASE_MAP.md`), autorizados por "ok, pode seguir com as recomendações nos 5 pontos".
- O lint reclamou de um `require('eslint')` em `scripts/`. Em vez de mudar a configuração do lint, troquei para a linha de comando do ESLint.

**Próximos passos (dependem de você)**
1. Posso adicionar `.dev-ai-first/` ao `.gitignore`? O arquivo da tarefa está em `.dev-ai-first/chore-verificacao-unica-ci.md` e hoje aparece como não rastreado. Até lá, ao commitar, evite `git add .`.
2. Depois do primeiro PR, marque o check "✅ Verificação" como obrigatório na proteção de branch do GitHub.
3. Sugiro uma issue para corrigir as 15 falhas em 10 arquivos de teste sem script e o teste vitest que falha. Depois disso, eles podem entrar no CI.
4. Quando quiser, peço para commitar e escrevo a descrição do PR.

