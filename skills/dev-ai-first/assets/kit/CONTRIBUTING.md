# Como contribuir

> Vale para pessoas e agentes; estes também seguem o [AGENTS.md](AGENTS.md).

## Fluxo

1. **Issue primeiro**, com critério de aceitação; funcionalidade grande: [design doc](docs/design-docs/0000-template.md) antes.
2. **Branch** a partir de `{{AGENTE: BRANCH_PRINCIPAL}}`: `<tipo>/<issue>-<descricao-curta>`, ex.: `feat/123-aprovar-pedido`.
3. **Teste primeiro** ([TESTING.md](TESTING.md)), [verificação completa](AGENTS.md#comandos) e o sistema rodado como o usuário usa, conforme [docs/VERIFICACAO.md](docs/VERIFICACAO.md), antes do PR.
4. **Revisão:** {{AGENTE: aprovações exigidas pela proteção da branch, ou "a definir"}}; de segurança se aplicável ([checklist](SECURITY.md#8-checklist-de-revisão-de-segurança)).
5. **Merge** com {{AGENTE: squash / rebase, pela configuração do repositório, ou "a definir"}}, CI verde.

## Commits

Conventional Commits, escopo = módulo (`feat(pedidos): aprovar pedido`). Refatoração e comportamento em commits separados.

## Pull requests

Um assunto, até ~400 linhas (sem gerados). Descrição: o quê, por quê, como foi verificado (conforme [docs/VERIFICACAO.md](docs/VERIFICACAO.md)), riscos, rollback; PR de agente diz isso e lista o não verificado.

## Revisão de código

Quem revisa não escreveu nem recebe as justificativas do autor: confere o diff contra os critérios. Comentários com `bloqueante:`, `sugestão:` ou `dúvida:`; os dois primeiros citam `arquivo:linha` ou a documentação. Nada do que o lint pega. Zero achados vale.

1. **Decidido × feito:** cada critério e decisão (do design doc ou das respostas do [checklist de design](docs/CHECKLIST_DESIGN.md) no PR) marcado **atendido**, **parcial** ou **ausente**; e o que o diff faz sem ter sido pedido. Bloco próprio, antes dos achados.
2. **Design:** segue o padrão do projeto, sem misturar duas formas no mesmo módulo? Divergência de um princípio está registrada em [riscos e débitos](ARCHITECTURE.md#11-riscos-e-débitos-conhecidos), e não "corrigida" por conta própria? Depois: [responsabilidades](ARCHITECTURE.md#41-responsabilidades), regra no domínio, recurso do framework. Montagem repetida entre casos de uso é `sugestão:` ([passo comum](CODING_GUIDELINES.md#passo-comum-a-vários-casos-de-uso)), ou `bloqueante:` se a seção já manda extrair.
3. **Testes por critério:** qual teste prova cada um e se falharia com ele falso; asserção mais frouxa é achado.
4. **Gambiarras:** `skip`/`only`, lint desligado (salvo a [exceção de tamanho](CODING_GUIDELINES.md#tamanho-e-complexidade-por-papel)), tipo frouxo ou suprimido, workaround sem issue.
5. **API obsoleta** na versão instalada, com o link.

### Perguntar antes no diff

O relato não basta: procure no diff cada item de [Perguntar antes](AGENTS.md#perguntar-antes).

| Item | Onde aparece |
|---|---|
| Dependência | manifesto e lockfile ({{AGENTE: MANIFESTO_E_LOCKFILE}}) |
<!-- se: backend -->
| Migração ou schema | {{AGENTE: PASTA_DE_MIGRACOES}} |
<!-- fim: backend -->
| Contrato de módulo | membro novo ou alterado na API pública do módulo |
<!-- se: api -->
| Contrato HTTP | diff da especificação da API contra a branch principal |
<!-- fim: api -->
<!-- se: eventos -->
| Evento | eventos públicos e o catálogo em [docs/EVENTS.md](docs/EVENTS.md) |
<!-- fim: eventos -->
| Configuração de verificação | arquivos de lint, arquitetura, tipos e baseline ([Nunca](AGENTS.md#nunca)) |
| Convenção documentada | `*.md` do kit |
| Interface nova | interface com uma só implementação |
| Infraestrutura | {{AGENTE: ARQUIVO_DO_AMBIENTE_LOCAL}}, CI, deploy |

Sem autorização (no PR ou em [Decisões registradas](AGENTS.md#decisões-registradas)) é `bloqueante:`; o que a demanda exige e o relato lista não bloqueia.

**Veredito:** **pronto**, **mudanças** (os `bloqueante:`) ou **precisa de decisão** (cada uma com recomendação). Uma rodada de correção; a re-revisão só reabre o que divergiu. Achado repetido vira proposta de regra automática.

## Decisões de arquitetura

Mudança estrutural ganha uma [ADR](docs/adr/README.md).
