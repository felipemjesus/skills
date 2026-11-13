# Preparar com o kit completo

Use em pasta vazia, ou quando o dev pede um documento longo específico num projeto existente (então siga só as partes desse documento). Para projeto existente, o padrão é [preparar.md](preparar.md), enxuto.

Objetivo: o agente achar contexto, regras e comandos sem adivinhar, seguir o padrão do projeto **e** os princípios de arquitetura e de código, e o dev saber o que falta para entregar com agentes. Resultado: os documentos do kit que se aplicam ao projeto, preenchidos a partir do código e das respostas do dev, o mapa de verificação e um diagnóstico de prontidão.

O kit tem três camadas:
- **princípios**, que valem sempre;
- **estrutura**: a do projeto, identificada pelo agente, ou a proposta pelo kit, em projeto novo;
- **perfil**: `backend`, `frontend` (`spa` ou `servidor`) ou `fullstack`.

No projeto existente, o código novo segue o padrão do projeto, e os princípios valem dentro dele. Onde o padrão contraria um princípio, isso vira dívida registrada e pergunta, nunca uma "correção" por conta própria.

## Sumário
- [Regras do preenchimento](#regras-do-preenchimento)
- [Passo a passo](#passo-a-passo)
- [Pasta vazia](#pasta-vazia)
- [Código existente](#código-existente)
- [Projeto já governado](#projeto-já-governado)
- [Onde buscar cada marcador](#onde-buscar-cada-marcador)
- [Verificar o que foi gerado](#verificar-o-que-foi-gerado)
- [Diagnóstico de prontidão](#diagnóstico-de-prontidão)
- [Relatório final](#relatório-final)

## Regras do preenchimento

| Marcador | Quem resolve | Como |
|---|---|---|
| AGENTE | você, a partir do projeto | com evidência (`arquivo:linha`, saída de comando) |
| USUARIO | o dev: decisão, regra de negócio, meta, prazo, dono, política | pergunte em rodadas; sem resposta, fica como está |
| VERIFICAR | o dev confirma um fato que você não alcança (pacote fora do repositório, configuração de servidor, valor em produção) | registre o que viu e o que falta confirmar |

A sintaxe é sempre `{{TIPO: o que falta}}`, por exemplo `{{VERIFICAR: versão do framework no servidor; o repositório não tem lockfile}}`. Você pode criar marcadores novos nesse formato.

Os modelos (`0000-template.md`, modelos de PR/MR) usam `{{...}}` sem prefixo e são preenchidos a cada documento novo.

1. **O documento descreve o projeto como ele é.** O que o projeto não tem (varredura de segredos, regra de arquitetura no CI, teste de aceitação) vira "ainda não existe" com um marcador USUARIO, ou sai. O próximo agente confia no que lê.
2. **Sem evidência, não preencha.** Nunca escolha uma ferramenta para preencher um marcador: isso é decisão do dev.
3. **Separe regra cumprida, meta e dívida.** Regra que o código viola nunca aparece como cumprida; vira meta, com as exceções em `ARCHITECTURE.md` §11.
4. **Nomes ilustrativos do kit** (`Pedido`, `Venda`, `src/modules/vendas/...`) viram casos reais do código ou saem. `verificar-citacoes.sh` acusa os que sobrarem.
5. **Apague o que não se aplica junto com os links para ele.** Ao trocar um título, procure links para a âncora antiga (`grep -rn '#ancora'`).
6. **Nunca sobrescreva arquivo do projeto.** `README.md` não é tocado. Arquivo que já existe é mesclado: o conteúdo atual é fato do projeto e entra na seção certa; mostre o diff ao dev antes de gravar.
7. **`AGENTS.md` curto: até 5,5 KB** (`wc -c`). Ele é carregado em toda sessão; o detalhe vai para os documentos linkados. Se o projeto já tem limite próprio, vale o dele.
8. **Versão instalada.** Ao citar recurso do framework, confira a versão no lockfile e, se houver ferramenta de documentação disponível, a documentação dessa versão. Sem lockfile ou sem acesso: escreva "a confirmar na documentação da versão X" em vez de supor.
9. **Codificação.** Se o detector avisar arquivos fora de UTF-8, busque com `grep -a` (sem ele a busca volta vazia em silêncio) e preserve a codificação ao editar código. Os documentos do kit são UTF-8.
10. **Estrutura identificada, não prescrita.** Com `--estrutura projeto`, os documentos descrevem a organização real em poucas linhas e apontam um exemplo de referência por tipo. Não escreva como o código "deveria" estar organizado: isso só existe com `--estrutura kit`.

## Passo a passo

A ordem evita copiar o que vai ser apagado e ler o projeto duas vezes.

1. **Detecte** com `detectar-projeto.sh` (já feito pelo `SKILL.md`): situação, linguagens, ambiente local, forja, codificação, instruções para agentes que já existem, `perfil_sugerido`, `modulos_sugeridos` e possíveis segredos versionados.
2. **Faça a rodada inicial de perguntas, numa mensagem só, antes de copiar qualquer coisa.** Cada pergunta leva uma recomendação:
   - **Estrutura:**
     - `projeto` (padrão em código existente): os documentos descrevem a estrutura que o código já usa, e o código novo imita o exemplo de referência;
     - `kit` (padrão em pasta vazia): o kit propõe fatias verticais (ADRs 0002 a 0005).
     - Em código existente, recomende `kit` só se o dev já quer migrar.
   - **Perfil:** confirme o `perfil_sugerido`: `backend`, `frontend` ou `fullstack`, e a variante do frontend (`spa`: componentes no cliente; `servidor`: telas renderizadas no servidor). Se o detector disser "os dois aparecem", pergunte qual predomina no código novo.
   - **Módulos:** confirme os `modulos_sugeridos` e pergunte o que o detector não vê: `estados` (agregado com status e transições), `claude` (o dev usa Claude Code). A lista sai em `copiar-kit.sh --listar`.
   - **Subprojeto:** se houver aviso de subprojetos, pergunte qual preparar.
   - **Branch e alterações não commitadas:** se houver alterações, pergunte antes de seguir.
3. **Copie só o que se aplica:**

   ```bash
   bash <pasta da skill>/scripts/copiar-kit.sh <projeto> --estrutura projeto|kit --perfil backend|frontend|fullstack [--frontend spa|servidor] --modulos a,b,c
   ```

   - Deixe `claude` de fora agora: o `CLAUDE.md` importa o `AGENTS.md`, e copiá-lo antes de preencher põe o modelo vazio no seu contexto.
   - Os trechos de módulos inativos já saem na cópia.
   - O script lista os arquivos que já existiam no projeto: mescle-os (regra 6).
   - O script grava `.dev-ai-first/kit.lst` com o que a skill copiou; os scripts de verificação usam esse manifesto.
4. **Liste os marcadores** com `listar-marcadores.sh <projeto>`. A lista é o roteiro da leitura: leia o projeto para responder a ela, não para conhecê-lo inteiro.
5. **Leia o projeto e preencha os marcadores AGENTE.** Veja [Código existente](#código-existente) e [Onde buscar cada marcador](#onde-buscar-cada-marcador).
6. **Pergunte os USUARIO e VERIFICAR** em rodadas de até 7, agrupadas por tema, cada uma com recomendação e com o que acontece se ficar em branco. Comece pelos que o agente precisa para entregar: verificação, branch, convenções, autorizações, riscos. Metas (SLO, cobertura, prazos) já vêm como "a definir" e não viram pergunta. O que o dev não souber fica marcado: é melhor que inventado.
7. **Monte o mapa de verificação** (`docs/VERIFICACAO.md`): como subir o sistema, com que dados, e como chegar e o que observar nas funcionalidades principais que a leitura mostrou (de 5 a 10, não todas). Confirme rodando o que der; o que não rodou fica marcado "não verificado".
8. **Verifique** ([Verificar o que foi gerado](#verificar-o-que-foi-gerado)).
9. **Por último,** se o dev usa Claude Code: `copiar-kit.sh <projeto> <mesmas flags> --arquivos CLAUDE.md --modulos claude`. Se o projeto usa outro agente (`.github/copilot-instructions.md`, `.cursor/rules`), o arquivo dele vira um **link** para o `AGENTS.md`, nunca uma cópia.
10. **Proponha** incluir `.dev-ai-first/` no `.gitignore` (é onde o modo Entregar guarda o estado). É decisão do dev.
11. **Faça o diagnóstico e o relatório,** e grave os dois em `.dev-ai-first/preparar.md`, para outra sessão retomar.

**Dev indisponível** (ele pediu para seguir sem perguntas, ou a sessão é automática): siga a recomendação de cada pergunta, registre cada suposição no relatório, em "Decisões tomadas sem o dev", e deixe os marcadores USUARIO como estão. Uma suposição nunca vira regra de negócio.

## Pasta vazia

Não há código: as respostas do dev são a fonte. Use a ferramenta de pergunta do agente, se houver; senão, perguntas numeradas. O dev pode responder "ok" para aceitar todas as recomendações.

**Rodada 1, projeto e domínio:**
1. O nome do projeto e o problema que ele resolve, em uma frase.
2. Quem usa e como o sistema gera valor.
3. De 3 a 8 termos do negócio, com uma linha cada: viram o glossário e os nomes no código.
4. As áreas que parecem independentes, que viram os módulos iniciais. Recomende começar com poucas.

**Rodada 2, stack, perfil e estrutura (depende da 1):**
1. Linguagem e framework. Recomende a versão estável mais recente e um framework com injeção de dependência, ORM, validação, filas e eventos de fábrica.
2. Banco de dados. Recomende o relacional padrão do framework.
3. Mensageria. Recomende o mecanismo do framework.
4. Frontend: tem? No mesmo repositório?
5. Algo já decidido por fora: nuvem, login corporativo, restrições de dados.
6. Perfil: backend, frontend (spa ou servidor) ou fullstack.
7. A estrutura proposta pelo kit? Em pasta vazia, recomende `kit`.

Depois, siga o [passo a passo](#passo-a-passo) a partir do passo 3:
- os marcadores que dependem de código (comandos, caminhos, configuração de lint) continuam AGENTE e são preenchidos na primeira entrega;
- as ADRs 0002 a 0005 ficam `Aceita` com a data de hoje;
- **sem exemplo de referência no projeto,** use os de [exemplos.md](exemplos.md) como ponto de partida;
- a primeira demanda recomendada é "iniciar o projeto", pelo modo Entregar: criar a aplicação com o comando único de verificação funcionando.

## Código existente

- **Branch:** se é repositório git, crie `dev-ai-first/preparar`. Não commite.
- **Leitura em projeto grande** (centenas de arquivos de código ou vários módulos): divida entre subagentes em paralelo, cada um com escopo fechado, devolvendo só a conclusão com evidência:

  | Frente | Lê | Devolve |
  |---|---|---|
  | Stack e comandos | manifesto, lockfile, scripts, `Makefile`, `docker-compose`, CI, README | versões, comandos reais, serviços locais |
  | Estrutura | árvore, pontos de entrada, rotas, registro de dependências | organização real, onde fica cada tipo de arquivo |
  | Domínio | entidades, enums, migrações, rotas e telas | termos, agregados, estados, regras visíveis |
  | Qualidade | testes, lint, tipos, CI, `.gitignore`, `.env.example` | o que a máquina verifica, tempo da suíte, segredos expostos |

- **Estrutura do projeto: identificar, não reescrever.** Preencha os marcadores com o padrão real e curto:
  - onde fica cada papel (entrada, validação, caso de uso, domínio, persistência, integração, tela);
  - o fluxo de uma requisição ou tela;
  - a árvore até o nível que o agente imita;
  - um exemplo `arquivo` por tipo.
- **Princípios × padrão:** confira o padrão contra os princípios (`ARCHITECTURE.md` §4.1, `CODING_GUIDELINES.md`). Onde o código contraria um princípio (ex.: regra de negócio na entrada, ORM espalhado), registre em `ARCHITECTURE.md` §11 com `arquivo:linha` e uma pergunta ao dev. Não reescreva o princípio para caber no código, nem o código para caber no princípio.
- **Estrutura do kit em código existente** (o dev quer migrar): para cada ADR de 0002 a 0005, classifique o código como **segue**, **segue em parte** ou **não segue**, com `arquivo:linha`. O que não segue vira dívida em §11, e o `CODEBASE_MAP.md` mostra qual forma imitar.
- **Exemplos de referência:** para cada tipo de operação da tabela do `CODEBASE_MAP.md`, escolha **uma** fatia real, de preferência com teste, e diga por quê. Tipo sem exemplo bom fica "ainda não existe"; não escolha um exemplo ruim só para preencher.
- **Ambiente sem as ferramentas do projeto** (dependências não instaladas, runtime ausente): não instale nada. Preencha os comandos a partir do manifesto e do CI, marque-os como "não executado" e registre no relatório.
- **Segredo encontrado** (`possiveis_segredos_versionados` do detector, ou na leitura): confira, não copie o valor para nenhum documento, registre arquivo e linha no diagnóstico, item 13, com prioridade alta.
- **Plugin ou extensão de um sistema hospedeiro** (framework, banco, rotas ou agendador fora do repositório) **e projeto sem comandos:** a seção Comandos do `AGENTS.md` vira uma linha ("não há comandos no repositório; o projeto roda dentro de X"), e os fatos do hospedeiro viram VERIFICAR, agrupados numa só rodada. Não preencha comando por comando com "ainda não existe".

## Projeto já governado

`situacao: governado`: o projeto já tem instruções para agentes (`AGENTS.md` ou `CLAUDE.md` próprios, `.claude/`, `.cursor/rules`, skills locais, `AGENTS.md` em subpastas). Essas instruções são fato do projeto e mandam. Este roteiro **substitui** os passos 2 a 6 do [passo a passo](#passo-a-passo):

1. Crie a branch `dev-ai-first/preparar`, se é repositório git.
2. Leia as instruções existentes e liste o que elas já cobrem: comandos, limites, fluxo, definição de pronto, estrutura, princípios.
3. Compare com o kit pelo índice (`copiar-kit.sh --listar`), sem abrir os modelos, e monte a lista do que falta, por documento e com o motivo (ex.: "não há exemplos de referência", "não há mapa de verificação").
4. Faça uma rodada única de perguntas: perfil, documentos que entram, e se o dev quer as seções que faltam no `AGENTS.md` dele.
5. Copie só o aceito: `copiar-kit.sh <projeto> --estrutura projeto --perfil ... --arquivos a,b`.
6. Preencha os marcadores. **Não troque o `AGENTS.md` do projeto pelo do kit:** proponha o trecho que falta. Limites do próprio projeto (tamanho, formato) vencem a regra 7.
7. Links dos documentos copiados que apontam para documentos não copiados: aponte para o equivalente do projeto, ou o link sai.
8. Siga o passo a passo a partir do passo 7 (mapa de verificação, verificação, diagnóstico, relatório).

## Onde buscar cada marcador

| Marcadores | Onde buscar |
|---|---|
| nome, linguagem, framework, banco, mensageria, frontend, manifesto e lockfile | manifesto e lockfile (versão instalada, não a faixa), `docker-compose`, `.env.example`, configuração do ORM |
| branch principal | `git symbolic-ref refs/remotes/origin/HEAD` ou a branch dos workflows de CI |
| comandos (`CMD_*`) | scripts do manifesto, `Makefile`/`justfile`, CI, README. Preencha só os que existem; rode os que são só leitura (lint, testes unitários), se o dev permitir. Sem comando único de verificação, `CMD_CHECK` fica "ainda não existe" e entra no diagnóstico com prioridade alta |
| mecanismos e recursos do framework, entidade, helpers de teste | o que o código **usa** (imports e chamadas), não só o que o framework oferece |
| bibliotecas e ferramentas (e2e, mock de rede, mutação, fronteiras) | dependências instaladas e seus arquivos de configuração |
| verificações de lint, tipos e arquitetura | configuração e CI. Costumam não existir: regra 1, e um item no diagnóstico |
| módulos, caminhos, migrações, arquivos gerados, configuração | árvore de pastas e registro de rotas e dependências |
| termos e invariantes do domínio | entidades, enums de estado, migrações, validações |
| sistemas externos, observabilidade | clientes HTTP, SDKs, variáveis de ambiente com URL ou chave, configuração de log |

## Verificar o que foi gerado

Rode e mostre só os totais no relatório:

```bash
bash <pasta da skill>/scripts/listar-marcadores.sh <projeto> --resumo
bash <pasta da skill>/scripts/verificar-links.sh <projeto> --alterados
bash <pasta da skill>/scripts/verificar-citacoes.sh <projeto> --alterados
bash <pasta da skill>/scripts/verificar-citacoes.sh <projeto> --alterados --mostrar
wc -c <projeto>/AGENTS.md
```

- `listar-marcadores.sh` olha só os arquivos do manifesto `.dev-ai-first/kit.lst`.
- `--alterados` confere só o que você gerou ou mudou. Links quebrados que o projeto já tinha não são seus.
- `verificar-citacoes.sh` reprova citação `arquivo:linha` inexistente e nome ilustrativo do kit que sobrou: corrija tudo.
  - Com `--mostrar`, ele imprime cada linha citada: confira se ela diz o que o documento afirma (o erro comum é apontar a linha vizinha).
  - Os avisos de caminho inexistente são para conferir; caminho de exemplo que não existe sai.
- Se o projeto formata Markdown (prettier, markdownlint no CI), rode o formatador nos documentos gerados.

**Revisão independente, uma rodada:** um subagente sem o histórico da conversa recebe só a lista dos documentos gerados e a pergunta "quais afirmações destes documentos não são sustentadas pelo código? Cite documento:linha e a evidência contrária". Não passe a ele suas justificativas. Corrija o que ele provar. O que ficar em dúvida vira VERIFICAR.

## Diagnóstico de prontidão

O que falta para um agente entregar com qualidade neste projeto. Avalie cada item com evidência; **proponha, não instale**: cada item aceito vira uma demanda do modo Entregar.

| # | Item | Por que importa | Como verificar |
|---|---|---|---|
| 1 | `AGENTS.md` curto, sem AGENTE pendente | é o contexto de toda sessão | `listar-marcadores.sh`, `wc -c` |
| 2 | Comando único de verificação que passa | é a definição de pronto do agente | existe; roda verde |
| 3 | Teste de um arquivo só | feedback rápido no teste primeiro | comando existe |
| 4 | Testes unitários rápidos | o agente roda a suíte muitas vezes | tempo da suíte |
| 5 | Teste de integração com banco real | o caso de uso testado de verdade | existe e roda localmente |
| 6 | Lint e formatador configurados | estilo resolvido por máquina | configuração + comando |
| 7 | Verificação de tipos | erro pego antes de rodar | typecheck na verificação |
| 8 | Regras de arquitetura verificadas | a arquitetura não se degrada em silêncio | verificação de fronteiras ou testes de arquitetura |
| 9 | CI roda a verificação em todo PR/MR | o pronto não depende de memória | workflow do CI |
| 10 | Exemplos de referência nomeados | o agente imita o certo | tabela do `CODEBASE_MAP.md` |
| 14 | Mapa de verificação com as funcionalidades principais | o agente prova o pronto rodando o sistema, não só os testes | `docs/VERIFICACAO.md` preenchido e conferido |
| 15 | Regras garantidas por máquina | regra só de revisão se perde com o tempo | tabela "regra → garantida por" em `ARCHITECTURE.md` §9: quantas são só "revisão" |
| 11 | Links dos documentos verificados no CI | documento quebrado ensina errado | `verificar-links.sh` no CI |
| 12 | Ambiente local reproduzível | o agente consegue rodar a integração | `docker compose` ou equivalente |
| 13 | Segredos fora do repositório | o agente lê tudo o que está versionado | `.env` no `.gitignore`; busca por chaves |

**Status:** **ok**, **parcial**, **falta** ou **não se aplica** (ex.: sem banco, o item 5 não se aplica).

**Prioridade pelo efeito, não pelo número do item:**
- **alta:** o agente não tem como provar que terminou (sem verificação, sem teste rodável, sem ambiente), ou há risco ativo (segredo versionado, dado sensível exposto);
- **média:** a qualidade depende da revisão humana (lint, tipos, fronteiras, CI, exemplos, regras só de revisão);
- **baixa:** melhora, mas não bloqueia.

Itens que o dev aceita como dívida vão para `ARCHITECTURE.md` §11.

## Relatório final

Grave em `.dev-ai-first/preparar.md` e mostre na conversa, nesta ordem:
1. **Resultado em uma frase:** quantos arquivos foram gerados, em que branch, quantas decisões aguardam o dev.
2. **Diagnóstico:** item, status, evidência, prioridade e próxima demanda proposta.
3. **Decisões pendentes:** USUARIO e VERIFICAR agrupados, com recomendação.
4. **Decisões tomadas sem o dev,** se houve.
5. **O que foi apagado ou ficou "ainda não existe",** com o motivo.
6. **Arquivos criados e mesclados,** e os totais dos scripts de verificação.
7. **O que não foi verificado:** comandos não rodados e afirmações conferidas só por amostragem.
8. **Próximo passo:** em geral, a primeira demanda de prioridade alta, pelo modo Entregar.

Não commite. Pergunte se o dev quer revisar o diff.
