# Como contribuir

> Vale para pessoas e agentes de IA. Agentes também seguem [AGENTS.md](AGENTS.md).

## Fluxo

1. **Issue primeiro.** Toda mudança parte de uma issue com contexto e critério de aceitação. Funcionalidade grande: [design doc](docs/design-docs/0000-template.md) antes do código.
2. **Branch** a partir de `{{AGENTE: BRANCH_PRINCIPAL}}`: `<tipo>/<issue>-<descricao-curta>`, ex.: `feat/123-aprovar-pedido`.
3. **Desenvolva com TDD** ([TESTING.md](TESTING.md)) seguindo as [diretrizes de código](CODING_GUIDELINES.md).
4. **Rode a verificação completa:** `{{AGENTE: CMD_CHECK}}`.
5. **Abra o PR** preenchendo o template.
6. **Revisão:** pelo menos {{USUARIO: N}} aprovação(ões); revisão de segurança quando aplicável ([SECURITY.md](SECURITY.md#8-checklist-de-revisão-de-segurança)).
7. **Merge** com {{USUARIO: squash / rebase}}, CI verde.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/), escopo = módulo:

```
feat(pedidos): aprovar pedido respeitando limite de crédito
fix(suporte): tratar resposta vazia do classificador
refactor(pedidos): extrair value object Dinheiro
```

Commits pequenos e coesos. Refatoração e mudança de comportamento em commits separados.

## Pull requests

- **Pequenos:** idealmente até ~400 linhas alteradas (sem contar gerados). Divida se passar disso.
- **Um assunto por PR.**
- Descrição com: o quê, por quê, como foi verificado, riscos e plano de rollback.
- PR feito por agente de IA indica isso na descrição e lista o que não foi verificado.

## Revisão de código

Quem revisa não é quem escreveu. Quando o autor é um agente, a revisão é feita em outra conversa ou subagente com contexto limpo, focada na [matriz de responsabilidades](ARCHITECTURE.md#41-responsabilidades) e no [checklist de design](AGENTS.md#checklist-de-design). O pedido de revisão leva a demanda, o plano ou design doc com os critérios e o intervalo do diff; não leva as justificativas do autor nem o que aceitar. Por quê: o revisor que recebe os argumentos do autor tende a conferir os argumentos, não o diff.

Quem revisa olha, nesta ordem:
1. **Correção:** faz o que a issue pede? Casos de borda e de erro? As afirmações da descrição do PR (o que mudou, como foi verificado) batem com o diff? **O que foi decidido foi feito?** Percorra a lista de critérios, decisões e suposições (tabela do [design doc](docs/design-docs/0000-template.md#critérios-de-aceitação); sem design doc, as respostas do checklist e as decisões na descrição do PR) e marque cada linha **atendida**, **parcial** ou **ausente**, citando-a; liste também o que o diff faz sem ter sido pedido.
2. **Design:** respeita fronteiras de módulo e a [matriz de responsabilidades](ARCHITECTURE.md#41-responsabilidades) (fatia não importa fatia, ORM só no repository, controller e request sem repository)? A regra de negócio está no domínio e não no handler nem no controller? Usa o recurso do framework em vez de solução própria? Nomes seguem a linguagem ubíqua e a convenção de sufixos? A mesma montagem ou sub-roteiro repetido em handlers do diff é `sugestão:` citando o [passo comum](CODING_GUIDELINES.md#passo-comum-a-vários-casos-de-uso); é `bloqueante:` quando o diff traz a repetição que essa seção já manda extrair.
3. **Testes, por critério:** para cada linha da tabela de critérios, qual teste a prova e se ele falharia se a afirmação fosse falsa (sim/não). Aponte asserção mais frouxa que o critério (só verifica que existe, cobre 2 de 9 casos). Tente dois valores que ninguém nomeou (o outro lado do limite, o conjunto vazio) num teste descartável, sem commit.
4. **Segurança e dados.**
5. **Código típico de IA:** abstração especulativa, verbosidade, comentário que repete o código, tratamento de erro genérico, duplicação de algo que já existe no projeto ou no framework.
6. **Gambiarras e bypasses:** teste pulado ou isolado (`skip`/`only`), lint desativado (exceto a [exceção aprovada de tamanho e complexidade](CODING_GUIDELINES.md#tamanho-e-complexidade-por-papel), numa função e com o motivo), tipo frouxo sem motivo (`any`, `mixed`), supressão do verificador de tipos ({{AGENTE: ex.: `@ts-ignore`, `@phpstan-ignore`}}), workaround sem issue.
7. **Sintaxe ou API obsoleta:** quando a versão instalada tem forma recomendada, aponte-a com o link da documentação dessa versão.
8. **Legibilidade.** Estilo é trabalho do lint, não da revisão.

**Evidência ou silêncio.** Comentários `bloqueante:` e `sugestão:` citam `arquivo:linha` ou um link da documentação oficial; achado grave descreve o cenário concreto de falha. Comentários `dúvida:` dispensam evidência, mas apontam a linha a que se referem. Não comente o que o CI ou o lint já pegam; se deveriam ter pegado e não pegaram, proponha a regra. Zero achados é um resultado válido. Falsos positivos comuns: estilo coberto pelo formatador, preferência pessoal, "poderia ser mais genérico".

**"Perguntar antes" conferido pelo diff.** O relato do autor não basta: quem revisa procura no diff cada item de [Perguntar antes](AGENTS.md#perguntar-antes). Por quê: o agente que pulou a pergunta também tende a não citá-la no relato; o diff não omite.

| Item do "Perguntar antes" | Onde aparece no diff |
|---|---|
| Dependência nova ou atualizada | manifesto de dependências e lockfile ({{AGENTE: MANIFESTO_E_LOCKFILE}}) |
| Migração ou schema | pasta de migrações e schema ({{AGENTE: PASTA_DE_MIGRACOES}}) |
| Contrato de módulo | membro novo ou alterado na `<Modulo>Api` em `api/` |
| Contrato HTTP | diff da especificação da API gerada contra `{{AGENTE: BRANCH_PRINCIPAL}}` (status trocado, campo removido ou renomeado) |
| Evento | `events/` público do módulo e o catálogo em [docs/EVENTS.md](docs/EVENTS.md) |
| Configuração de verificação | configuração de lint, de arquitetura e de tipos, baseline, testes de arquitetura ({{AGENTE: ARQUIVOS_DE_VERIFICACAO}}) |
| Convenção documentada | `*.md` do kit (`AGENTS.md`, `ARCHITECTURE.md`, `CODING_GUIDELINES.md`, ...) |
| Interface nova | interface fora de `ports/` e `api/` |
| Serviço de infraestrutura | arquivo do ambiente local ({{AGENTE: ARQUIVO_DO_AMBIENTE_LOCAL}}), CI, deploy |

Cada ocorrência sem autorização (no PR ou em [Decisões registradas](AGENTS.md#decisões-registradas)) é `bloqueante:`; o que a demanda necessariamente exige (migração aditiva, endpoint, método da `<Modulo>Api` ou evento novos, [Perguntar antes](AGENTS.md#perguntar-antes)) e está listado no relato não bloqueia. A conferência do que foi decidido (item 1) sai num bloco próprio, antes e separado dos achados de padrão: um eixo não esconde o outro (um diff impecável pode não fazer o que foi decidido, e vice-versa). A revisão termina com um veredito: **pronto**, **mudanças** (lista dos `bloqueante:`) ou **precisa de decisão** (lista das decisões, cada uma com a recomendação). Vale para revisão humana e por agente. **A revisão tem fim:** uma rodada de correção; a re-revisão só reabre o que divergiu; o que continua falhando vai ao usuário no veredito "precisa de decisão".

Achado que se repete em PRs diferentes vira proposta de regra automática (lint ou arquitetura).

Comentários de revisão: prefixe com `bloqueante:`, `sugestão:` ou `dúvida:`.

## Decisões de arquitetura

Mudou algo estrutural (estilo, tecnologia, fronteira entre módulos)? Registre uma [ADR](docs/adr/README.md).
