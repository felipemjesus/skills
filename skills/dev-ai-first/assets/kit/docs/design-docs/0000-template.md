# {{Título da funcionalidade ou mudança}}

- **Autor(es):** {{nomes}} · **Revisores:** {{nomes}}
- **Status:** Rascunho | Em revisão | Aprovado | Implementado | Abandonado
- **Data:** {{AAAA-MM-DD}} · **Issue:** {{link}}

## 1. Contexto e problema

{{Problema, para quem, por que agora.}}

## 2. Objetivos e não objetivos

- **Objetivos:** {{resultados mensuráveis}}
- **Não objetivos:** {{o que fica de fora}}

Releia o pedido frase a frase: cada frase cai num objetivo, num critério, num não objetivo ou numa [questão em aberto](#10-questões-em-aberto). A que não cai em lugar nenhum é requisito que some.

### Critérios de aceitação

Cada critério tem a verificação que vai prová-lo e 1–3 exemplos, um deles o caso-limite em que uma implementação ingênua quebra (o valor exato do limite, o conjunto vazio, o dado ausente). Cada decisão respondida e cada suposição também viram uma linha; suposição só para detalhe com uma resposta claramente defensável ou delegado pelo usuário, com as palavras dele ([como perguntar](../../CODING_GUIDELINES.md#8-regras-para-código-escrito-por-agentes-de-ia)). É esta lista que a [revisão](../../CONTRIBUTING.md#revisão-de-código) percorre, marcando cada linha como atendida, parcial ou ausente.

| Critério | Exemplos | Verificação |
|---|---|---|
| {{quando o pedido é aprovado com estoque suficiente, o estoque é reservado}} | {{estoque 10: pedido de 10 → aprovado; 11 → recusado; pedido sem itens → recusado}} | {{teste de integração do caso de uso; verificado conforme docs/VERIFICACAO.md}} |
| {{suposição (usuário: "a ordem você decide"): pedidos do mais recente ao mais antigo}} | — | {{teste da consulta}} |

## 3. Comportamento esperado

{{Cenários principais, em linguagem ubíqua (Dado / Quando / Então).}}

## 4. Proposta

- **Domínio:** {{agregados, invariantes, eventos; o que muda em docs/DOMAIN.md}}
- **Arquitetura:** {{módulos e arquivos afetados}}. Segue o padrão do projeto? {{sim, com o exemplo de referência imitado; ou a divergência de princípio e se vai para [riscos e débitos](../../ARCHITECTURE.md#11-riscos-e-débitos-conhecidos)}}
- **Contratos:** {{endpoints, eventos, API de módulo; compatibilidade}}
<!-- se: backend -->
- **Dados:** {{tabelas, migrações (expand and contract), volume, retenção}}
<!-- fim: backend -->
<!-- se: frontend -->
- **Telas:** {{telas novas ou alteradas, estados de erro e carregamento}}
<!-- fim: frontend -->
- **Verificação:** {{como provar rodando o sistema, conforme [VERIFICACAO.md](../VERIFICACAO.md); linhas novas ou alteradas lá}}

## 5. Checklist de design

{{Uma linha por item do [checklist de design](../CHECKLIST_DESIGN.md), na ordem e com o número; "n/a" só com o motivo. Fato com a evidência buscada no código; decisão com a recomendação.}}

## 6. Alternativas consideradas

{{2–3 alternativas, com uma **recomendação explícita** e o motivo de cada descarte.}}

## 7. Impacto e release

| Item | Detalhe |
|---|---|
<!-- se: backend -->
| Dados | {{migração, volume, backfill}} |
<!-- fim: backend -->
| Contratos | {{o que muda e para quem}} |
| Conceito redefinido | {{termo cujo sentido muda e cada leitor atual (consultas, regras, telas, relatórios, eventos), cada um com seu critério ou a decisão do usuário citada; leitor mantido na definição antiga ganha nome próprio}} |
| Efeitos irreversíveis | {{e-mails, cobranças, dados apagados}} |
| Rollback | {{como desfazer cada passo}} |

Migração ou mudança de contrato sem rollback definido bloqueia a aprovação.

## 8. Segurança, privacidade e observabilidade

{{Riscos, mitigação, alertas.}}

## 9. Plano de entrega

{{Fases, flags, rollout e critério para avançar.}}

## 10. Questões em aberto

- {{…}}
