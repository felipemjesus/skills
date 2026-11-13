# Diretrizes de API

> Convenções HTTP. A especificação de cada endpoint fica em {{AGENTE: ex.: openapi.yaml}}, gerada ou mantida junto com o código.

## Princípios

- **Contrato primeiro:** a especificação muda no mesmo PR que o código.
- **Recursos com nomes do domínio**, no plural: `/pedidos`, `/pedidos/{id}/itens`.
- **Ação de negócio que não é CRUD** vira sub-recurso com verbo: `POST /pedidos/{id}/aprovar`. O verbo é o mesmo em toda a cadeia (rota, caso de uso, transição, evento).
- **Entrada fina:** a rota ou o controller valida a forma com o recurso do framework, chama o caso de uso e devolve a resposta; sem acesso a dados nem regra de negócio ([responsabilidades](../ARCHITECTURE.md#41-responsabilidades)).
- **Forma da resposta visível no ponto de entrada:** a entrada (ou o formatador que ela chama, com nome próprio) mostra os campos devolvidos.
- **Ações permitidas no recurso:** recurso com ciclo de vida devolve o que o usuário pode fazer naquele registro, calculado pelas mesmas transições e guardas que validam a requisição, com o motivo quando bloqueada: `"acoesPermitidas": [{ "acao": "cancelar", "permitida": false, "motivo": "O pedido já foi faturado." }]`.
<!-- se: estados -->
  Transições: [ARCHITECTURE.md](../ARCHITECTURE.md#54-estados-e-transições).
<!-- fim: estados -->

## Métodos e status

| Operação | Método | Sucesso |
|---|---|---|
| Listar / obter | `GET` | `200` |
| Criar | `POST` | `201` + `Location` |
| Ação de negócio | `POST /recurso/{id}/acao` | `200`, ou `202` se assíncrona |
| Atualizar | `PUT` / `PATCH` | `200` ou `204` |
| Remover | `DELETE` | `204` |

## Erros

Formato, categorias e nome da regra: [CODING_GUIDELINES.md](../CODING_GUIDELINES.md#4-erros). Status por categoria:

| Categoria | Status |
|---|---|
| Entrada inválida (corpo ilegível, formato), lista por campo em `errors` | `400` |
| Não autenticado / sem permissão | `401` / `403` |
| Não encontrado (ou sem permissão para saber que existe) | `404` |
| Estado não permite; conflito de versão; unicidade de negócio | `409` |
| Regras de negócio violadas, todas juntas em `violacoes` | `422` |
| Limite de uso | `429` + `Retry-After` |
| Dependência externa indisponível | `503` |

## Paginação, filtros e ordenação

- **Cursor keyset:** `?limit=20&cursor=…` → `nextCursor`. O cursor é opaco e carrega a chave de ordenação desempatada pelo id (`(criadoEm, id)`); a página seguinte é `WHERE (criadoEm, id) < (:criadoEm, :id)` com os mesmos filtros. Nunca dependa de o registro do cursor existir nem use `skip 1`: se ele saiu do filtro ou foi apagado, a página quebra ou repete. Nesta stack: {{AGENTE: RECURSO_DE_PAGINACAO_KEYSET_DO_ORM}}.
- **Filtros e ordenação em lista fechada** declarada na consulta (`?status=pendente&sort=-criadoEm`). Parâmetro, valor ou campo fora da lista → 400; nunca deduzido nem ignorado.
- **Limite máximo de página:** {{USUARIO: N}}; acima dele → 400, nunca reduzido em silêncio.

**Testes mínimos de endpoint de listagem**, cada um esperando 400 com o parâmetro em `errors`: filtro com valor fora da lista (status fora do enum); ordenação por campo não permitido; `limit` acima do máximo; cursor inválido ou adulterado; parâmetro desconhecido. Somam-se aos de comportamento: filtro aplicado, ordem, página seguinte sem repetir nem pular.

## Idempotência, concorrência e versões

- Comandos aceitam `Idempotency-Key`; a repetição devolve o resultado original.
- Recurso editável usa `ETag` / `If-Match`; conflito → 409.
- Mudança compatível (campo ou endpoint novo) não muda versão; incompatível → {{USUARIO: /v2 no caminho ou cabeçalho}}, com `Deprecation` e prazo de convivência a definir.
- Operação longa: `202` + `GET /operacoes/{id}` (ou webhook), nunca conexão aberta por minutos.

## Segurança

Autenticação em todo endpoint, exceto os listados como públicos; autorização pelo {{AGENTE: MECANISMO_DE_AUTORIZACAO_DO_FRAMEWORK}} antes de executar, nunca só no frontend; limite de taxa por usuário ou tenant. Mais em [SECURITY.md](../SECURITY.md).
