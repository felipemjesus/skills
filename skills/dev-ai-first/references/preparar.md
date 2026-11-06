# Preparar o repositório

Objetivo: o agente encontrar contexto, regras e comandos sem adivinhar, e o dev saber o que ainda falta para entregar com qualidade usando agentes. O resultado é o kit de `assets/kit/` copiado para o projeto, com os marcadores preenchidos, mais um diagnóstico de prontidão.

## Sumário
- [Regras do preenchimento](#regras-do-preenchimento)
- [Pasta vazia](#pasta-vazia)
- [Código existente](#código-existente)
- [Onde buscar cada marcador](#onde-buscar-cada-marcador)
- [Verificar o que foi gerado](#verificar-o-que-foi-gerado)
- [Diagnóstico de prontidão](#diagnóstico-de-prontidão)
- [Relatório final](#relatório-final)

## Regras do preenchimento

Os documentos do kit têm dois tipos de marcador:

| Marcador | Quem preenche | Como |
|---|---|---|
| `{{AGENTE: ...}}` | você, a partir do projeto | com evidência (`arquivo:linha`, saída de comando) |
| `{{USUARIO: ...}}` | o dev | pergunte em rodadas; sem resposta, o marcador fica como está |

Os modelos (`docs/adr/0000-template.md`, `docs/design-docs/0000-template.md`, `docs/runbooks/0000-template.md`, `.github/pull_request_template.md`) usam `{{...}}` sem prefixo e ficam como estão: são preenchidos a cada documento novo.

1. **O documento descreve o projeto como ele é.** Frase que afirma algo que o projeto não tem (varredura de segredos, regra de arquitetura no CI, teste de aceitação) vira `ainda não existe: {{USUARIO: ...}}`, ou sai do documento com registro no relatório. Por quê: o agente seguinte confia no que lê e deixa de verificar o que o documento diz que já está garantido.
2. **Sem evidência, não preencha.** `{{AGENTE: ...}}` sem correspondente no projeto cai na regra 1. Nunca escolha uma ferramenta para preencher o marcador ("o projeto não tem lint de arquitetura, vou pôr dependency-cruiser" é decisão do dev, não preenchimento).
3. **Separe regra cumprida, meta e dívida.** Regra que o código segue: afirme. Regra que o código novo deve seguir mas o antigo não: "meta" com as exceções em `ARCHITECTURE.md` §11. Nunca apresente como cumprida uma regra que o código viola.
4. **Exemplos do kit viram exemplos do projeto.** Nomes ilustrativos (`Pedido`, `Venda`, `src/modules/vendas/...`, `totalIgualSomaItens`) são trocados por casos reais do código; sem caso real equivalente, o exemplo sai ou fica marcado como ilustrativo.
5. **Apague o que não se aplica**, e os links para ele (sem frontend no repositório: `docs/FRONTEND.md` sai e o `AGENTS.md` aponta para o repositório do frontend). Documento desatualizado é pior que documento ausente.
6. **Nunca sobrescreva arquivo do projeto.** `README.md` do projeto não é tocado. Se `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md` ou o modelo de PR já existem, mescle: o conteúdo atual é fato do projeto e entra na seção certa do documento do kit; mostre o diff ao dev antes de gravar.
7. **`AGENTS.md` curto** (até ~165 linhas). Ele é carregado em toda sessão; detalhe vai para os documentos linkados.
8. **Versões e sintaxe da versão instalada.** Ao citar recurso do framework, confira a versão no lockfile e a documentação oficial dessa versão (se houver ferramenta de documentação disponível, como ctx7, use-a). Nunca descreva API obsoleta como o caminho do projeto.

## Pasta vazia

Não há código para ler: as respostas do dev são a fonte. Use a ferramenta de pergunta do agente, se houver; senão, perguntas numeradas na conversa. Cada pergunta traz uma recomendação; o dev pode responder "ok" para aceitar todas.

**Rodada 1 — projeto e domínio**
1. Nome do projeto e o problema que resolve, em uma frase.
2. Quem usa e como o sistema gera valor (um parágrafo curto).
3. Termos principais do negócio, de 3 a 8, com uma linha cada (viram o glossário de `docs/DOMAIN.md` e os nomes no código).
4. Áreas do negócio que parecem independentes (viram os módulos iniciais). Recomende começar com poucas: módulo se divide depois, junção é cara.

**Rodada 2 — stack** (depende da rodada 1)
1. Linguagem e framework do backend. Recomende a versão estável mais recente e um framework que traga de fábrica injeção de dependência, ORM, validação, filas e eventos (o kit é *framework first*).
2. Banco de dados. Recomende o relacional padrão do framework, salvo motivo do domínio.
3. Filas e mensageria: o mecanismo do framework basta? Recomende que sim (ADR 0003).
4. Frontend: tem? Mesmo repositório ou outro? Qual framework?
5. Algo já decidido por fora: provedor de nuvem, login corporativo (IdP), restrições de dados.

**Depois das respostas**
1. Copie o kit para a raiz do projeto: `bash <pasta da skill>/scripts/copiar-kit.sh <projeto>`.
2. Preencha os marcadores que as respostas decidem: nome, descrição, domínio, glossário, módulos, linguagem, framework, banco, mensageria, frontend.
3. Os marcadores que dependem de código (comandos, caminhos, configuração de lint) **continuam** `{{AGENTE: ...}}`: ainda não há o que descrever. Eles serão preenchidos na primeira entrega.
4. Ajuste as ADRs 0002 a 0005: o dev aceitou o estilo do kit? Status `Aceita` com a data de hoje; recusou algo? ajuste a ADR e o documento afetado.
5. [Verifique](#verificar-o-que-foi-gerado), rode o [diagnóstico](#diagnóstico-de-prontidão) e faça o [relatório](#relatório-final). A primeira demanda recomendada é sempre "iniciar o projeto": criar a aplicação na stack escolhida com o comando único de verificação funcionando, pelo modo Entregar.

## Código existente

### 1. Antes de escrever
- Se há alterações não commitadas, pergunte antes de seguir: os documentos novos se misturariam a elas.
- Se é repositório git, crie uma branch (`dev-ai-first/preparar`). Não commite.
- Se `detectar-projeto.sh` listou subprojetos, pergunte qual preparar. Repositórios separados recebem cada um o seu kit; monorepo recebe um kit na raiz e `CLAUDE.md` local por subprojeto, se precisar.

### 2. Ler o projeto
Em projeto grande, divida a leitura entre subagentes em paralelo, cada um com escopo fechado e devolvendo só a conclusão com evidência:

| Frente | Lê | Devolve |
|---|---|---|
| Stack e comandos | manifesto, lockfile, scripts, `Makefile`, `docker-compose`, CI, README | versões, comandos reais e se rodam, banco, filas, serviços locais |
| Estrutura | árvore de pastas, pontos de entrada, rotas, registro de dependências | organização real (por camada, por módulo, por feature), módulos candidatos, onde fica cada tipo de arquivo |
| Domínio | entidades, models, enums, migrações, nomes de rotas e telas | termos do negócio, agregados, estados e transições, regras visíveis |
| Qualidade | testes, configuração de lint, tipos, formatador, CI, `.gitignore`, `.env.example` | o que é verificado por máquina, cobertura aparente, tempo da suíte, onde há segredo exposto |

Tabela completa em [Onde buscar cada marcador](#onde-buscar-cada-marcador).

### 3. Comparar o código com o estilo do kit
O kit propõe um estilo (monolito modular, fatias verticais por caso de uso, domínio rico, matriz de responsabilidades; ADRs 0002 a 0005). O código existente quase nunca segue tudo. Para cada ADR, classifique: **segue**, **segue em parte** (onde sim, onde não) ou **não segue**, com exemplos `arquivo:linha`.

Leve ao dev a decisão central, com recomendação:

> **Código novo segue o estilo atual do projeto ou o estilo do kit?**
> - *Estilo atual:* os documentos descrevem o padrão que o código já usa; as ADRs do kit ficam `Proposta` ou `Rejeitada`. Mais simples; o agente imita o vizinho.
> - *Estilo do kit para código novo:* as ADRs aceitas viram meta; o código antigo fica como dívida em `ARCHITECTURE.md` §11 e o `CODEBASE_MAP.md` mostra as duas formas, com a referência indicando qual imitar.
> - Recomendação: estilo atual, quando o código é consistente; kit para código novo, quando o código atual mistura formas ou o dev já quer migrar.

Até a resposta, não escreva `ARCHITECTURE.md` §4 nem `CODING_GUIDELINES.md`: eles dependem dela.

### 4. Escolher os exemplos de referência
Para cada tipo de operação da tabela "Exemplos de referência" do `CODEBASE_MAP.md` (escrita, leitura, transição de estado, integração externa, reação a evento, API pública de módulo), escolha **uma** fatia real que o agente deve imitar: a mais próxima do estilo escolhido, com teste. Diga por que escolheu. Tipo sem exemplo bom: `ainda não existe: {{USUARIO: ...}}`; não escolha um exemplo ruim só para preencher.

### 5. Perguntar as decisões do dev
Rode `bash scripts/listar-marcadores.sh <projeto>` depois de copiar o kit. Os `{{USUARIO: ...}}` agrupados por tema viram rodadas de até 7 perguntas, cada uma com recomendação e com o que acontece se ficar em branco (o marcador permanece, o documento diz "a definir"). Ordem sugerida: domínio e glossário → metas e limites (SLO, tempo da suíte) → segurança e dados (IdP, LGPD, segredos, contato) → decisões registradas e datas das ADRs. O que o dev não souber agora fica marcado: é melhor que inventado.

### 6. Escrever
1. Copie o kit sem sobrescrever: `bash <pasta da skill>/scripts/copiar-kit.sh <projeto>`. O script lista os arquivos do kit que já existiam no projeto; mescle cada um (regra 6). Use o script em vez de `cp` direto: ler de fora do projeto costuma ser negado pelas permissões.
2. Preencha os `{{AGENTE: ...}}` com o que a leitura encontrou; o que não existe segue as regras 1 e 2.
3. Preencha os `{{USUARIO: ...}}` respondidos.
4. Apague seções e documentos que não se aplicam, com os links para eles.
5. Proponha (é decisão do dev) incluir `.dev-ai-first/` no `.gitignore`: é onde o modo Entregar guarda o estado de cada demanda.
6. Ajuste o `CLAUDE.md` e, se o projeto usa outro agente, o arquivo dele (`.github/copilot-instructions.md`, `.cursor/rules`) como **link** para o `AGENTS.md`, nunca cópia.

## Onde buscar cada marcador

| Marcadores | Onde buscar |
|---|---|
| `NOME_DO_PROJETO`, `LINGUAGEM`, `FRAMEWORK`, `BANCO_DE_DADOS`, `MENSAGERIA`, `FRAMEWORK_FRONTEND`, `RAIZ_DO_FRONTEND`, `MANIFESTO_E_LOCKFILE` | manifesto e lockfile (versão instalada, não a faixa), `docker-compose`, variáveis em `.env.example`, configuração do ORM |
| `BRANCH_PRINCIPAL` | `git symbolic-ref refs/remotes/origin/HEAD` ou a branch dos workflows de CI |
| `CMD_*` (instalar, dev, testes, lint, typecheck, check, gerar tipos) | scripts do manifesto, `Makefile`/`justfile`, passos do CI, README. Preencha só comando que existe; confira rodando os que são só leitura (lint, testes unitários) se o dev permitir, e diga quais não rodou. Sem comando único de verificação: `CMD_CHECK` vira `ainda não existe` e entra no diagnóstico como prioridade alta |
| `MECANISMO_DE_*_DO_FRAMEWORK`, `CLIENTE_HTTP_DO_FRAMEWORK`, `RECURSO_DE_*`, `MAQUINA_DE_ESTADOS_DO_FRAMEWORK`, `ENTIDADE`, `HELPERS_DE_TESTE_DO_FRAMEWORK` | o que o código **usa** (busque imports e chamadas), não só o que o framework oferece; confirme na documentação da versão instalada |
| `BIBLIOTECA_DE_*`, `FERRAMENTA_*` (e2e, mock de rede, acessibilidade, mutação, fronteiras) | dependências instaladas e seus arquivos de configuração |
| `ARQUIVOS_DE_VERIFICACAO`, `ARQUIVO_DE_BASELINE`, `CMD_ARCH_CHECK`, `VERIFICACAO_*`, `CAMPO_DE_MENSAGEM_DA_FERRAMENTA`, `REGRA_DE_*` | configuração de lint, tipos e arquitetura, testes de arquitetura, CI. Costumam não existir: regra 1, e item no diagnóstico |
| módulos (`modulo-a`, `Contexto A`), caminhos de exemplo, `PASTA_DE_MIGRACOES`, arquivos gerados, `ARQUIVOS_DE_CONFIG`, `ARQUIVO_DO_AMBIENTE_LOCAL` | árvore de pastas e registro de rotas e dependências |
| nomes do domínio de exemplo (`Pedido`, `Venda`, `AgregadoNome`, invariantes de exemplo) | entidades, enums de estado, migrações e regras reais (regra 4) |
| `SISTEMAS_EXTERNOS`, `BACKEND_DE_OBSERVABILIDADE` | clientes HTTP, SDKs, variáveis de ambiente com URL ou chave, configuração de log e métricas |

## Verificar o que foi gerado

Rode e mostre a saída no relatório:

```bash
bash scripts/listar-marcadores.sh <projeto>      # o que falta, por quem decide
bash scripts/verificar-links.sh <projeto>        # links e âncoras dos documentos
wc -l <projeto>/AGENTS.md                        # até ~165 linhas
```

E confira à mão, por amostragem: caminhos entre crases citados no `CODEBASE_MAP.md` existem (`ls`); os comandos da tabela do `AGENTS.md` existem no manifesto; nenhum documento afirma uma verificação que a configuração não faz.

Revisão independente: peça a um subagente sem o histórico da conversa que leia os documentos gerados e o código e aponte afirmações sem evidência ou falsas. Corrija antes do relatório.

## Diagnóstico de prontidão

O que falta para um agente entregar com qualidade neste projeto. Avalie cada item com evidência; **proponha, não instale** (instalar ferramenta, mudar CI ou lint é decisão do dev, e cada item aceito vira uma demanda do modo Entregar).

| # | Item | Por que importa para o agente | Como verificar |
|---|---|---|---|
| 1 | `AGENTS.md` curto, sem `{{AGENTE:}}` pendente | é o contexto de toda sessão | `listar-marcadores.sh`, `wc -l` |
| 2 | Comando único de verificação (`CMD_CHECK`) que passa | é a definição de pronto do agente | existe no manifesto; roda verde |
| 3 | Teste de um arquivo só | feedback rápido no ciclo teste primeiro | comando existe |
| 4 | Testes unitários rápidos | o agente roda a suíte muitas vezes | tempo da suíte |
| 5 | Teste de integração com banco real | handler testado de verdade, sem mock do ORM | existe e roda localmente |
| 6 | Lint e formatador configurados | estilo resolvido por máquina, não por prosa | arquivo de configuração + comando |
| 7 | Verificação de tipos | erro pego antes de rodar | typecheck no `CMD_CHECK` |
| 8 | Regras de arquitetura verificadas, com mensagem escrita para o agente | a arquitetura não se degrada em silêncio | `CMD_ARCH_CHECK` ou testes de arquitetura |
| 9 | CI roda a verificação em todo PR | o "pronto" não depende de quem lembrou | workflow do CI |
| 10 | Exemplos de referência nomeados | o agente imita o certo, não o mais frequente | tabela do `CODEBASE_MAP.md` |
| 11 | Links e caminhos dos documentos verificados no CI | documento quebrado ensina errado | `verificar-links.sh` no CI |
| 12 | Ambiente local reproduzível | o agente consegue rodar testes de integração | `docker compose` ou equivalente; `CMD_DEV` |
| 13 | Segredos fora do repositório | o agente lê tudo o que está no repositório | `.env` no `.gitignore`; busca por chaves no histórico recente |

Classifique cada item como **ok**, **parcial** ou **falta**, e dê prioridade:
- **alta:** sem ele o agente não tem como provar que terminou (itens 2, 3, 5, 12);
- **média:** sem ele a qualidade depende da revisão humana (6, 7, 8, 9, 10);
- **baixa:** melhora, mas não bloqueia (4, 11, 13 quando já há `.gitignore`).

Itens que o dev aceita como dívida vão para `ARCHITECTURE.md` §11.

## Relatório final

Mostre na conversa, nesta ordem:
1. **Resultado em uma frase** (ex.: "Kit gerado em 14 arquivos na branch `dev-ai-first/preparar`; 9 decisões aguardando você.").
2. **Diagnóstico de prontidão:** tabela com item, status, evidência, prioridade e proposta de próxima demanda.
3. **Decisões pendentes:** os `{{USUARIO:}}` que ficaram, agrupados, com recomendação.
4. **O que foi apagado ou ficou como "ainda não existe"**, com o motivo.
5. **Arquivos criados e mesclados**, e a saída de `listar-marcadores.sh` e `verificar-links.sh`.
6. **O que não foi verificado** (comandos não rodados, afirmações feitas por amostragem).
7. **Próximo passo recomendado:** em geral, a primeira demanda de prioridade alta do diagnóstico, para rodar com o modo Entregar.

Não commite. Pergunte se o dev quer revisar o diff antes.
