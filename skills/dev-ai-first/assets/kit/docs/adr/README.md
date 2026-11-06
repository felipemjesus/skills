# Architecture decision records

Uma ADR registra **uma** decisão arquitetural significativa: o contexto, a decisão e as consequências. Ela é imutável depois de aceita; para mudar, crie outra ADR que a substitui.

## Quando escrever

Escreva uma ADR quando a decisão atende às três condições: é **difícil de reverter**, seria **surpreendente sem contexto** e é **fruto de um trade-off real**. Exemplos típicos:

- Escolha de estilo arquitetural, banco, mensageria, framework.
- Mudança de fronteira entre módulos.
- Padrão que todos devem seguir (ou deixar de seguir).
- Exceção a uma regra do `AGENTS.md` ou de outra ADR.

Antes de propor mudança estrutural, leia as ADRs ativas: siga-as ou proponha explicitamente substituir uma delas.

ADR curta é aceitável para decisão pontual: contexto em poucas linhas, decisão e consequências.

**ADR de rejeição.** Quando uma alternativa é avaliada e recusada (ex.: "usar microsserviços"), registre-a com status `Rejeitada` e o motivo, para que não seja proposta de novo sem fato novo.

## Antipadrões

- Título em forma de pergunta ("Usar fila?") em vez de decisão ("Usar a fila do framework para eventos").
- Contexto vago, sem as forças em jogo.
- Consequências só positivas, sem o custo aceito.
- Alternativas sem o "por que não".
- Editar uma ADR aceita em vez de criar outra que a substitui.

## Como

1. Copie [0000-template.md](0000-template.md) para `NNNN-titulo-curto.md` (próximo número).
2. Status inicial `Proposta`; abra PR para discussão.
3. Ao aprovar, mude para `Aceita` e atualize a tabela abaixo e a seção de decisões do [ARCHITECTURE.md](../../ARCHITECTURE.md#10-decisões-registradas).

Status possíveis: `Proposta`, `Aceita`, `Rejeitada`, `Descontinuada`, `Substituída por NNNN`.

## Índice

| # | Título | Status | Data |
|---|---|---|---|
| [0001](0001-registrar-decisoes-de-arquitetura.md) | Registrar decisões de arquitetura | Aceita | {{USUARIO: DATA}} |
| [0002](0002-monolito-modular-com-fatias-verticais.md) | Monolito modular com fatias verticais e domínio rico | Proposta | {{USUARIO: DATA}} |
| [0003](0003-eventos-com-recursos-do-framework.md) | Transação no caso de uso e eventos com os recursos do framework; outbox só como exceção | Proposta | {{USUARIO: DATA}} |
| [0004](0004-interfaces-so-em-fronteiras.md) | Interfaces só em fronteiras | Proposta | {{USUARIO: DATA}} |
| [0005](0005-framework-first.md) | Framework first | Proposta | {{USUARIO: DATA}} |
