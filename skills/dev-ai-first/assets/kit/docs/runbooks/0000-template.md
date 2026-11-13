# Runbook: {{alerta ou situação}}

- **Severidade:** {{SEV1 / SEV2 / SEV3}} · **Dono:** {{time}} · **Alerta:** {{nome/link}} · **Revisado em:** {{AAAA-MM-DD}}

## Sintoma e impacto

{{O que se observa (alerta, reclamação, métrica) e quem é afetado.}}

## Diagnóstico

1. {{Dashboard: link}}
2. {{Logs/traces com o filtro}}
3. {{Causas possíveis e como distinguir}}

## Mitigação

| Causa | Ação imediata |
|---|---|
| {{ex.: taxa de erro subiu logo após um deploy}} | {{comparar com a versão anterior; rollback se confirmado}} |

## Escalonamento

{{Quem acionar e quando.}}

Depois do incidente: postmortem sem culpados (SEV1/SEV2) e este runbook atualizado.
