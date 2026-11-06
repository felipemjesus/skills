# dev-ai-first

Skill que torna o repositório **IA first** e conduz as entregas do dev com agentes de código (Claude Code, Codex, Cursor, Copilot) **com qualidade**.

Autor: Felipe Martins ([@felipemjesus](https://github.com/felipemjesus)) · criada para o Desafio Elevate da [Tech Leads Club](https://www.techleads.club) · código em [skills/mine/dev-ai-first](../skills/mine/dev-ai-first)

**Demo (4min51, narrada e com legendas):** [youtu.be/E3Ixk_QQfMU](https://youtu.be/E3Ixk_QQfMU). Mostra como a skill surgiu, o uso na prática (preparar um backend legado e entregar uma demanda) e as vantagens.

## O problema

O dev pede algo ao agente e recebe código fora da arquitetura, sem teste, com regra de negócio inventada e documentação esquecida. Faltam duas coisas:

1. **Contexto no repositório:** o agente não sabe a stack, os comandos, onde fica cada coisa, qual código imitar, o que precisa perguntar. Então adivinha.
2. **Um ciclo de entrega:** sem um roteiro, o "pronto" vira "os testes passaram" (quando há testes), e ninguém confere o diff contra o que foi pedido.

Já existe um kit de documentos para isso (`AGENTS.md`, `ARCHITECTURE.md`, `CODEBASE_MAP.md`, ADRs...), mas adotá-lo é manual: copiar arquivos, preencher centenas de marcadores e, depois, lembrar de seguir o kit a cada demanda.

## O que a skill faz

| Modo | Quando | O que faz |
|---|---|---|
| **Preparar** · pasta vazia | projeto novo | entrevista em 2 rodadas (projeto e domínio → stack), com recomendação em cada pergunta; gera os documentos para agentes |
| **Preparar** · código existente | projeto que já roda | lê o código com subagentes em paralelo (stack, estrutura, domínio, qualidade); preenche o que o código responde, com evidência `arquivo:linha`; pergunta só o que é decisão do dev; descreve o projeto **como ele é**, separando regra cumprida, meta e dívida |
| **Preparar** · já preparado | qualquer momento | diagnóstico de prontidão IA first: o que falta para o agente provar que terminou, por prioridade |
| **Entregar** | toda demanda | entender → planejar com checklist de design (fato se busca, decisão se pergunta) → teste primeiro → implementar → verificar → revisão independente por subagente → descrição do PR e documentação atualizada |
| `retomar` | sessão nova ou contexto resumido | continua a demanda pelo arquivo de estado, conferindo com `git log`/`git diff` |
| `revisar` | qualquer diff | revisão por subagente sem o histórico da conversa: "decidido × feito" e achados com `arquivo:linha` |
| `pr` | antes de abrir o PR | descrição a partir do diff: o quê, por quê, como foi verificado (com o teste falhando antes), o que não foi verificado, autorizações |

Princípios que valem em todos os modos:
- **O projeto manda.** Depois de preparado, as regras estão no `AGENTS.md` do projeto; a skill conduz o processo e não repete as regras.
- **Fato se busca, decisão se pergunta.** Nunca inventa regra de negócio, meta, limite ou dono.
- **Nada irreversível sem pedido:** não commita, não dá push, não sobrescreve arquivo, não instala dependência, não muda CI ou lint sozinha.
- **Pronto é evidência:** comando rodado e o que ele mostrou, mais o que não foi verificado.
- **Estado em arquivo:** a demanda fica em `.dev-ai-first/<branch>.md` (fora do versionamento), para outra sessão continuar.

## Como usar

**Instalar** com a CLI [`skills`](https://www.npmjs.com/package/skills), que detecta o agente (Claude Code, Codex, Cursor...):

```bash
npx skills add felipemjesus/skills --skill dev-ai-first
```

Ou à mão, a partir de um clone deste repositório:

```bash
cp -r skills/mine/dev-ai-first ~/.claude/skills/dev-ai-first
```

**Exemplos de prompt:**

```
/dev-ai-first preparar
```
```
/dev-ai-first Criar o comando único de verificação do backend: lint dos arquivos alterados e as suítes unitárias, e rodar no CI nos PRs.
```
```
/dev-ai-first retomar
/dev-ai-first revisar
/dev-ai-first pr
```

Sem a barra, a skill também é acionada por pedidos como "prepara este repositório para agentes", "implementa esta história", "escreve a descrição do PR".

## Estrutura

```
skills/mine/dev-ai-first/
├── SKILL.md                  # detecta a situação e roteia (curto)
├── references/
│   ├── preparar.md           # entrevista, leitura do código, onde buscar cada marcador, diagnóstico
│   ├── entregar.md           # ciclo de entrega, arquivo da tarefa, retomar
│   ├── revisar.md            # pedido do revisor independente
│   └── pr.md                 # descrição do PR
├── scripts/
│   ├── detectar-projeto.sh   # vazio / código / preparado; manifestos, subprojetos
│   ├── copiar-kit.sh         # copia o kit sem sobrescrever; lista conflitos
│   ├── listar-marcadores.sh  # o que falta preencher, por quem decide
│   └── verificar-links.sh    # links e âncoras dos documentos existem
└── assets/kit/               # kit dev-por-agentes agnóstico de stack
```

O `SKILL.md` tem ~45 linhas e carrega só a referência do modo em uso. O kit em `assets/` só é lido quando o modo Preparar copia ou consulta um documento.

## Como evoluiu

A skill é a última etapa de um trabalho de cerca de 9 dias (28/10 a 05/11), feito com o Claude Code.

### 1. Do princípio ao kit (28/10 a 01/11)

- **Ponto de partida:** os princípios que eu queria ver no código (SOLID, DDD, TDD, arquitetura hexagonal, CQRS) e a pergunta: que documentos fazem um agente de código seguir esses princípios?
- **Dois kits:** `dev-por-agentes`, para repositório desenvolvido com agentes, e `aplicacao-de-ia`, para produto com LLM. Cada um em três versões: agnóstico, TypeScript e PHP.
- **Decisões de direção**, cada uma registrada com o porquê:
  - **framework first:** nada artesanal se o framework já oferece;
  - **interfaces só nas fronteiras** (sistema externo, LLM, API pública entre módulos);
  - **matriz de responsabilidades:** controller sem repository, ORM só no repository, regra de negócio nas entidades;
  - **versão estável mais recente e sintaxe atual**, sem número de versão nos documentos;
  - **nomes sem preposição** (`ItemPedido`, `ConsultaCreditoPort`);
  - **tamanho de código por papel**, não um número único.
- **Análise de cerca de 27 aplicações reais** (PHP e TypeScript, de produção e de estudo), para o kit descrever problemas que aparecem de verdade. No meio dela, corrigi o rumo: o foco é arquitetura e legibilidade, não a escolha de ferramentas.

### 2. Ensaios: medir o kit em vez de confiar nele (02/11 a 05/11)

Para saber se o kit funcionava, montei um ensaio automatizado:
- um agente recebe um projeto vazio só com o kit TypeScript;
- implementa uma trilha de **9 demandas** num domínio diferente dos exemplos do kit: iniciar o projeto, cadastro, fluxo de aprovação, listagem, devolução, bug, contribuição externa, demanda ambígua e pressão por atalho;
- tudo numa sessão contínua, com configuração isolada e sem ver a rubrica;
- **um agente avaliador**, em contexto limpo, mede o resultado contra a rubrica.

Foram **6 rodadas completas**, de 3h a 3h30 e cerca de US$ 70 cada. Cada falha que se repetia virou mudança no kit, e a rodada seguinte conferia se a falha sumiu:

| O agente fazia | O kit passou a ter |
|---|---|
| Aceitou que o lint barrava os exemplos do próprio kit, trocou classes por 68 funções soltas e **reescreveu o `CODING_GUIDELINES.md` sem perguntar** | exemplos validados contra o lint do kit; orientação a objetos verificada por máquina; mudar convenção virou "perguntar antes" → **0 funções soltas** |
| Copiava os nomes dos exemplos para as dependências (até `pedido` num domínio de biblioteca): só 21% tinham o nome do tipo | regra "dependência leva o nome do tipo", com os exemplos corrigidos → **97%, depois 100%** |
| Preenchia os marcadores `{{...}}` inventando: o `SECURITY.md` afirmava recursos que não existiam, e sobraram 112 marcadores | marcadores `{{AGENTE:}}` (o agente preenche com evidência) e `{{USUARIO:}}` (o dev decide; nunca inventar) e a regra "o documento descreve o projeto como ele é" |
| Ignorava o "perguntar antes" a partir da segunda demanda (dependências, docker, migrações) | "perguntar é não fazer a mudança"; a demanda autoriza só o que necessariamente exige, citando as palavras exatas |
| Editou a configuração do lint "porque o documento mandava" | **ordem de verdade:** configuração e verificações > ADR > documentos. Nunca mudar a configuração para seguir um documento |
| Contornou o lint trocando a API do ORM por SQL cru | trocar a API recomendada para escapar de uma regra exige pergunta |
| Escrevia handlers de 56 a 60 linhas, com a mesma montagem copiada em 7 handlers | limite verificado por papel e regra do "passo comum" → **maior método caiu para 26 linhas** |
| Deu três sentidos para "aguardando" e dois para "bloqueado" | "um conceito, uma definição": quem muda um conceito lista todos os leitores; deixar um leitor na definição antiga vira pergunta, nunca suposição |
| Deixou entidade com status sem tabela de transições e pôs regra no repository | tabela de transições obrigatória e verificada; repository não usa outro repository |

**A lição que mais influenciou a skill: regra só escrita não mudou o comportamento do agente; limite verificado mudou.** Por isso a skill traz scripts de verificação e um diagnóstico de prontidão centrado no "comando único de verificação".

**Limites dos ensaios**, para não superestimar:
- A nota da rubrica ficou entre 94% e 97,5% nas 6 rodadas porque a própria rubrica foi endurecida no caminho. A evolução aparece nas métricas acima, não na nota.
- Não rodei a condição "sem kit". Por isso não afirmo quanto do resultado se deve ao kit.
- Só o kit TypeScript foi ensaiado.

### 3. Do kit à skill (05/11)

Adotar o kit ainda era manual: copiar arquivos, preencher centenas de marcadores e lembrar de seguir o kit a cada demanda. A skill automatiza a adoção (Preparar) e o uso diário (Entregar). Ela foi testada num projeto real, um backend real em produção, em Node/Express/Sequelize, com legado e 4 estilos de código convivendo. Rodou num clone isolado, com configuração limpa e permissões restritas como as de um dev:

| Execução | O que aconteceu | O que mudou na skill |
|---|---|---|
| **Preparar** (leitura) | Detectou "código existente", leu o projeto com 4 subagentes em paralelo e parou **antes de gravar** com 7 decisões, cada uma com recomendação. Achou 4 estilos de código convivendo, CI que só faz deploy, `npm test` que sai com erro de propósito, testes vitest que nenhum script roda, e que "cliente" no código é o tenant. | O agente rodou `cd <skill> && bash scripts/...`: comando composto é negado quando o dev libera só comandos simples. O `SKILL.md` passou a mandar rodar os scripts pelo caminho absoluto, um por chamada. |
| **Preparar** (escrita) | 22 documentos, `AGENTS.md` com 145 linhas, nenhum marcador do agente pendente e 58 decisões do dev marcadas "a definir" em vez de inventadas. Diagnóstico: o agente não tem como provar que terminou. A **revisão independente** conferiu ~140 afirmações dos documentos contra o código e achou **16 erradas**, corrigidas antes do relatório; achou também um possível furo de isolamento entre clientes num endpoint. | O `cp` do kit foi negado (lê de fora do projeto) e o agente gravou 22 arquivos um a um. Nasceu o `scripts/copiar-kit.sh`, que copia sem sobrescrever e lista conflitos. |
| **Correção do dev** | Informei o significado de um perfil de usuário que a skill tinha deixado "a definir". A skill achou a referência no código que a leitura inicial tinha perdido, **admitiu o erro** e abriu uma pergunta nova (relação com uma flag do cadastro de clientes) em vez de presumir. | — |
| **Entregar** (planejamento) | Demanda: *"Criar o comando único de verificação do backend: lint dos arquivos alterados e as suítes unitárias, e rodar no CI nos PRs."* Antes de propor, mediu: 844 testes unitários verdes, 15 falhas em arquivos sem script, 675 erros de lint. Parou com 5 decisões, cada uma com cenário de borda (*"corrigir uma linha num arquivo legado com 57 erros de lint obriga a limpar o arquivo inteiro?"*). | O arquivo de estado da demanda ficava em `.git/`, e o agente bloqueia escrita ali. Mudou para `.dev-ai-first/<branch>.md`, com proposta de `.gitignore` no Preparar e proibição de `git add -A` enquanto não estiver ignorado. |
| **Entregar** (implementação) | `npm run verificar` (lint dos alterados com a regra "não pode piorar" + todas as suítes `test:*:unit`) e workflow de CI nos PRs, **sem dependência nova**. Teste primeiro com RED pela asserção; **sabotagem** para provar que o comando falha (erro de lint plantado, asserção invertida), desfeita depois; revisão independente em duas rodadas; documentos do projeto atualizados no mesmo diff. Quando o lint reclamou, **trocou o código em vez de afrouxar a configuração**. Declarou o que não verificou (Actions no GitHub, Node 20, `npm ci`). | — |

Custo total das sessões: cerca de US$ 23 (preparar US$ 14,37; entregar US$ 8,38).

Lições que ficaram:
- **A revisão independente compensa:** 16 de ~140 afirmações dos documentos gerados estavam erradas. Sem ela, o agente seguinte confiaria nelas.
- **"Fato se busca, decisão se pergunta" segura o agente:** nas duas sessões ele parou antes de gravar ou implementar, com perguntas concretas, e não inventou regra de negócio.
- **Permissões reais quebram roteiros ingênuos:** os três defeitos achados no uso foram de ambiente (comando composto, leitura fora do projeto, escrita em `.git/`), não de conteúdo. Só apareceram rodando com as permissões restritas que um dev usaria.

A conversa completa, anonimizada, está em [dev-ai-first-sessoes.md](dev-ai-first-sessoes.md).

### 4. Publicação (06/11)

Ao preparar a skill para este repositório público:
- **Portabilidade:** três trechos dos scripts só funcionavam no GNU/Linux (`find -printf`, `sed \L`, `xargs -r`), e o locale `C.UTF-8` não existe no macOS, o que faria âncoras com acento serem acusadas como quebradas. Foram reescritos com recursos POSIX, com `perl` como alternativa no macOS.
- **Testes:** 20 testes automatizados dos scripts e do validador de skills, cobrindo os casos que deram problema no uso real (arquivo existente não é sobrescrito, `AGENTS.md` de outra origem não conta como kit, âncora com acento). Uma sabotagem confirmou que os testes pegam regressão.
- **CI:** `make verify` roda em Linux e macOS a cada push e pull request.

## Próximos passos

- Kit `aplicacao-de-ia` (prompts versionados, evals, guardrails) como modo opcional, para produtos com LLM.
- Kits prontos de TypeScript e PHP como referência quando a stack bate.
- `sincronizar`: apontar a documentação que o diff deixou desatualizada, no CI.
