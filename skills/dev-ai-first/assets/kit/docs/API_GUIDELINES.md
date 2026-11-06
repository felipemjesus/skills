# Diretrizes de API

> Convenções para APIs HTTP. A especificação de cada endpoint fica em {{AGENTE: ex.: openapi.yaml}}, gerada ou mantida junto com o código.

## Princípios

- **Contrato primeiro.** A especificação muda no mesmo PR que o código; mudança de contrato passa por revisão.
- **Recursos com nomes do domínio**, no plural: `/pedidos`, `/pedidos/{id}/itens`.
- **Ações de negócio** que não são CRUD viram sub-recursos com verbo: `POST /pedidos/{id}/aprovar`. Isso reflete o command da fatia (`AprovarPedidoCommand`), e o verbo é o mesmo em toda a cadeia (rota, command, handler, transição, evento).
- **Controllers finos:** o `Request` valida a entrada com o recurso de validação do framework → o controller monta o command/query e despacha ao handler (direto ou pelo barramento do framework) → devolve o `Resource`. Sem repository, sem ORM, sem regra de negócio, sem try/catch de regra ([matriz de responsabilidades](../ARCHITECTURE.md#41-responsabilidades)).
- **Forma da resposta declarada no ponto de entrada.** O controller (ou o Resource que ele usa, nomeado na fatia) deixa visível quais campos devolve, sem precisar abrir o formatador para saber do que a tela depende.
- **Ações permitidas no recurso.** Recursos com ciclo de vida devolvem as ações permitidas ao usuário para aquele registro, calculadas pela mesma tabela de transições e pelas mesmas guardas que validam a requisição, com o motivo quando uma ação está bloqueada ([ARCHITECTURE.md](../ARCHITECTURE.md#54-estados-e-transições)):

  ```json
  "acoesPermitidas": [
    { "acao": "aprovar", "permitida": true },
    { "acao": "cancelar", "permitida": false, "motivo": "O pedido já foi faturado." }
  ]
  ```

## Métodos e status

| Operação | Método | Sucesso |
|---|---|---|
| Listar / obter | `GET` | `200` |
| Criar | `POST` | `201` + `Location` |
| Comando de negócio | `POST /recurso/{id}/acao` | `200` ou `202` (assíncrono) |
| Substituir / atualizar parcialmente | `PUT` / `PATCH` | `200` ou `204` |
| Remover | `DELETE` | `204` |

## Erros

Formato [Problem Details (RFC 9457)](https://www.rfc-editor.org/rfc/rfc9457):

```json
{
  "type": "https://{{USUARIO: dominio}}/erros/limite-credito-excedido",
  "title": "Limite de crédito excedido",
  "status": 422,
  "detail": "O pedido de R$ 1.200,00 excede o limite disponível de R$ 1.000,00.",
  "instance": "/pedidos/123/aprovar",
  "traceId": "…"
}
```

**Tipo do erro.** O `type` termina no nome da exceção em kebab-case, sem o sufixo `Exception` (`LimiteCreditoExcedidoException` → `limite-credito-excedido`), a mesma forma do `type` dos eventos. É derivado do nome da classe num único lugar, o tradutor de erros para HTTP; nenhuma exceção repete o próprio nome em string. Por quê: o `type` é contrato com o cliente; não expõe o nome interno do código e se lê como URL.

| Situação | Status |
|---|---|
| Entrada inválida: corpo ilegível ou validação de formato na borda, com a lista de erros por campo em `errors` | `400` |
| Não autenticado / sem permissão | `401` / `403` |
| Recurso não encontrado (ou sem permissão para saber que existe) | `404` |
| Conflito de versão; **estado atual não permite a operação** (transição recusada pela tabela); **unicidade de negócio violada** (código já cadastrado) | `409` |
| **Regra de negócio violada** (uma ou várias, devolvidas juntas em `violacoes`) | `422` |
| Limite de uso | `429` + `Retry-After` |
| Dependência externa indisponível | `503` |

Cada categoria de exceção de domínio tem um status ([CODING_GUIDELINES.md](../CODING_GUIDELINES.md#4-erros)); "entrada inválida" (400), "estado não permite" (409) e "regra violada" (422) são categorias distintas. Regras de negócio independentes violadas voltam juntas no campo de extensão `violacoes` (lista de `{ regra, mensagem, campo? }`), separado do `errors` por campo da validação de entrada; a exceção base de regra violada carrega essa lista.

**Nome da regra.** `regra` é o nome da regra em camelCase afirmativo, dizendo o que ela exige (`limiteCreditoRespeitado`, `clienteSemBloqueio`, `maximoRenovacoesRespeitado`, `estoqueSuficiente`): o mesmo da tabela de invariantes em [DOMAIN.md](DOMAIN.md#5-agregados-e-invariantes) e o do predicado do domínio quando ele existe (para um predicado negativo, como `excedeLimite()`, a regra é a forma afirmativa). Nunca um código numérico nem uma constante em maiúsculas. Por quê: o nome se lê como linguagem do negócio no teste, no JSON e no frontend. Dois gates que verificam o mesmo conceito citam o mesmo nome. Nunca retorne stack trace, SQL ou mensagens internas de dependências.

## Paginação, filtros e ordenação

- Paginação por cursor: `?limit=20&cursor=…` → resposta com `nextCursor`. O cursor é opaco e carrega os valores da chave de ordenação, desempatada pelo id (ex.: `(criadoEm, id)`); a página seguinte é uma consulta *keyset*, `WHERE (criadoEm, id) < (:criadoEm, :id)` na ordem decrescente, com os mesmos filtros. Não dependa de o registro do cursor ainda existir nem de pular "o registro do cursor" (`skip 1`): se ele saiu do filtro ou foi apagado, a página quebra ou repete. Nesta stack: {{AGENTE: RECURSO_DE_PAGINACAO_KEYSET_DO_ORM}} (ou `where` com a comparação equivalente, `criadoEm < x OU (criadoEm = x E id < y)`). Cursor ilegível ou adulterado → 400.
- Filtros explícitos, numa **lista fechada** declarada na Query da fatia: `?status=pendente&criadoApos=2026-01-01`. Parâmetro ou valor não listado (filtro desconhecido, status fora do enum) é rejeitado com 400, não deduzido da requisição nem ignorado.
- Ordenação: `?sort=-criadoEm`, só pelos campos de uma lista fechada declarada na Query; campo fora dela → 400.
- Limite máximo de página: {{USUARIO: N}}; `limit` acima dele → 400, nunca reduzido em silêncio.

## Idempotência e concorrência

- `POST` de comandos aceita cabeçalho `Idempotency-Key`; repetição com a mesma chave retorna o resultado original.
- Concorrência otimista com `ETag` / `If-Match` em recursos editáveis; conflito → `409`.

## Versionamento

- Mudanças compatíveis (novo campo, novo endpoint) sem nova versão.
- Mudança incompatível → nova versão ({{USUARIO: /v2 no caminho ou cabeçalho}}), com período de descontinuação de {{USUARIO: N}} meses e cabeçalho `Deprecation`.

## Operações longas

Tarefas que levam mais que alguns segundos usam `202 Accepted` + recurso de status (`GET /operacoes/{id}`) ou webhook, não conexão aberta por minutos. Para progresso em tempo real, Server-Sent Events.

## Segurança

- Autenticação em todos os endpoints, exceto os listados explicitamente como públicos.
- Autorização pela `Policy` no mecanismo do framework ({{AGENTE: MECANISMO_DE_AUTORIZACAO_DO_FRAMEWORK}}), checada no `Request` ou no handler antes de executar; nunca só no frontend.
- Limite de taxa por usuário/tenant.
- Mais em [SECURITY.md](../SECURITY.md).
