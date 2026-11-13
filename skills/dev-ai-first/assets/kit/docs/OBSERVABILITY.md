# Observabilidade

> Traces, métricas e logs exportados para {{AGENTE: BACKEND_DE_OBSERVABILIDADE}}, com {{AGENTE: ex.: OpenTelemetry}}.

- **Logs** estruturados com `traceId`, `module` e `useCase` {{AGENTE: demais campos fixos}}; nunca segredos, tokens, documentos ou dado pessoal sem redação ({{AGENTE: onde a redação é configurada}}). Logue fatos com contexto: `pedido aprovado {pedidoId, total}`.
- **Traces:** todo request, mensagem e job cria ou continua um trace; o `correlationId` segue nos eventos. Span manual só onde a instrumentação oficial não cobre.
<!-- se: frontend -->
- **No navegador:** erros não tratados e falhas de rede reportados com a rota e o `traceId` da requisição; métricas de carregamento ({{AGENTE: ex.: Web Vitals}}) por página.
<!-- fim: frontend -->
- **Métricas de negócio:** a definir (ex.: pedidos aprovados por minuto).

## SLOs

Metas a definir; preencha quando o time decidir.

| Capacidade | SLI | SLO (30 dias) |
|---|---|---|
| API | requisições sem 5xx | a definir |
| API | p95 abaixo de um limite (a definir) | a definir |
<!-- se: backend -->
| Consumidores e jobs | atraso abaixo de um limite (a definir) | a definir |
<!-- fim: backend -->

Alerta por queima do orçamento de erro, não por limiar instantâneo. Todo alerta tem dono e [runbook](runbooks/0000-template.md); alerta que ninguém precisa atender é ajustado ou removido.
