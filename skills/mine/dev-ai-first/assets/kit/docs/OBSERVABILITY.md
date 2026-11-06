# Observabilidade

> Como sabemos o que o sistema está fazendo em produção. Padrão: [OpenTelemetry](https://opentelemetry.io/) para traces, métricas e logs, exportados para {{AGENTE: BACKEND_DE_OBSERVABILIDADE}}.

## Logs

- **Estruturados** (JSON), com campos fixos: `timestamp`, `level`, `message`, `traceId`, `spanId`, `tenantId`, `module`, `useCase`.
- Níveis: `error` (alguém precisa agir), `warn` (anômalo, mas tratado), `info` (eventos de negócio relevantes), `debug` (desligado em produção por padrão).
- **Nunca** registrar: segredos, tokens, senhas, documentos de identidade, PII sem redação. Use o recurso de redação/mascaramento do framework ou da biblioteca de logs, configurado em `src/platform/observability`.
- Logue fatos com contexto, não frases soltas: `pedido aprovado {pedidoId, total}` em vez de `entrou no if`.

## Traces

- Todo request HTTP, mensagem consumida e job cria ou continua um trace (`correlationId` propagado nos eventos).
- Spans pela instrumentação oficial do framework e das bibliotecas (OpenTelemetry), mais spans manuais só onde faltar: handler de cada caso de uso, consultas ao banco, chamadas HTTP externas, publicação e consumo de mensagens.

## Métricas

| Categoria | Métricas |
|---|---|
| Serviços (RED) | taxa de requisições, taxa de erros, duração (p50/p95/p99) por endpoint |
| Recursos (USE) | uso, saturação e erros de CPU, memória, conexões de banco, filas |
| Filas e mensageria | atraso de consumo, jobs falhos / tamanho da DLQ, idade do job mais antigo pendente |
| Negócio | {{USUARIO: ex.: pedidos aprovados/min, conversão}} |

## SLOs

| Serviço / capacidade | SLI | SLO | Janela |
|---|---|---|---|
| API | requisições sem erro 5xx | {{USUARIO: 99,9%}} | 30 dias |
| API | p95 de latência < {{USUARIO: 300 ms}} | {{USUARIO: 99%}} | 30 dias |
| Consumidores | atraso de consumo < {{USUARIO: N}} s | {{USUARIO: 99%}} | 30 dias |

Alertas por **queima de orçamento de erro**, não por limiar instantâneo, para evitar ruído.

## Alertas

- Todo alerta tem dono e runbook ([runbooks/](runbooks/)).
- Se um alerta dispara e ninguém precisa agir, ajuste ou remova.
