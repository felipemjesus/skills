# {{Título da funcionalidade ou mudança}}

- **Autor(es):** {{nomes}}
- **Status:** Rascunho | Em revisão | Aprovado | Implementado | Abandonado
- **Data:** {{AAAA-MM-DD}}
- **Issue:** {{link}}
- **Revisores:** {{nomes}}

> Design doc é para pensar antes de construir e alinhar o time. Escreva o suficiente para revisores apontarem problemas; não mais. Seções que não se aplicam podem ser removidas.

## 1. Contexto e problema

{{Qual problema, para quem, e por que agora? Dados que mostram o problema.}}

## 2. Objetivos e não objetivos

- **Objetivos:** {{resultados mensuráveis}}
- **Não objetivos:** {{o que fica explicitamente de fora}}

Releia o pedido frase a frase: cada frase cai num objetivo, num critério, num não objetivo ou numa [questão em aberto](#10-questões-em-aberto). A que não cai em lugar nenhum é requisito que some.

### Critérios de aceitação

Cada critério tem a verificação que vai prová-lo e 1–3 exemplos, um deles o caso-limite em que uma implementação ingênua quebra (o valor exato do limite, o conjunto vazio, o dado ausente). Formato opcional: "quando X, o sistema deve Y". Cada decisão respondida (checklist, [questões em aberto](#10-questões-em-aberto)) e cada suposição registrada também vira uma linha; suposição só para detalhe com uma resposta claramente defensável ou delegado pelo usuário, com as palavras dele ([como perguntar](../../CODING_GUIDELINES.md#8-regras-para-código-escrito-por-agentes-de-ia)): é esta lista que a [revisão](../../CONTRIBUTING.md#revisão-de-código) percorre, marcando cada uma como atendida, parcial ou ausente.

| Critério | Exemplos | Verificação (teste, cenário BDD, métrica) |
|---|---|---|
| {{quando o analista aprova um pedido dentro do limite, o sistema deve mudar o status para aprovado}} | {{limite 1.000: total 1.000,00 → aprovado; 1.000,01 → recusado; pedido sem itens → recusado}} | {{teste de integração do handler + cenário "Pedido dentro do limite é aprovado"}} |
| {{decisão: pedido cancelado não conta para o limite}} | {{2 em aberto + 1 cancelado → o próximo é aceito}} | {{teste de integração "terceiro pedido com um cancelado é aceito"}} |
| {{suposição (usuário: "a ordem da lista você decide"): pedidos do cliente listados do mais recente ao mais antigo}} | — | {{teste de integração da consulta "lista em ordem decrescente de criação"}} |

## 3. Comportamento esperado

{{Cenários BDD principais, em linguagem ubíqua.}}

```gherkin
Cenário: …
  Dado …
  Quando …
  Então …
```

## 4. Proposta

### 4.1 Domínio
{{Agregados, invariantes, eventos novos ou alterados. Atualizações em docs/DOMAIN.md.}}

### 4.2 Arquitetura
{{Módulos afetados, fatias novas ou alteradas em `features/`, mudanças nas pastas de domínio (agregados em `entities/`, `Port` em `ports/`, ...), em `repositories/` e `clients/`, `listeners/`. Diagrama de sequência se ajudar.}}

### 4.3 Contratos
{{Endpoints, eventos, schemas de tools. Compatibilidade com consumidores existentes.}}

### 4.4 Dados
{{Tabelas, migrações (expand and contract), volume, retenção.}}

## 5. Checklist de design

{{Resposta curta a cada item do [checklist de design](../../AGENTS.md#checklist-de-design), na ordem e com o número do item: uma linha por item; "n/a" só com o motivo. Fato com a evidência buscada no código; decisão com a recomendação.}}

## 6. Alternativas consideradas

{{2–3 alternativas, com uma **recomendação explícita** e o motivo de cada uma descartada.}}

## 7. Impacto e release

| Item | Detalhe |
|---|---|
| Dados | {{migração, volume afetado, backfill}} |
| Contratos | {{endpoints, eventos, API de módulo, tools alterados}} |
| Conceito redefinido | {{termo cujo sentido muda e cada leitor atual (consultas, regras, telas, relatórios, eventos), cada um com seu critério ou a decisão do usuário, citada (leitor mantido na definição antiga ganha nome próprio)}} |
| Janela de compatibilidade | {{por quanto tempo as duas versões convivem}} |
| Efeitos irreversíveis | {{e-mails enviados, cobranças, dados apagados}} |
| Rollback | {{como desfazer cada passo}} |

Migração ou mudança de contrato sem rollback definido bloqueia a aprovação.

## 8. Segurança, privacidade e observabilidade

{{Riscos, mitigação, métricas e alertas novos.}}

## 9. Plano de entrega

- Fases e feature flags.
- Plano de rollout ({{interno → % de usuários → todos}}) e critério para avançar.
- Plano de rollback.

## 10. Questões em aberto

- {{…}}
