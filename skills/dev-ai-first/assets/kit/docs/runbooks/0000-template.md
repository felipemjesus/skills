# Runbook: {{nome do alerta ou situação}}

- **Severidade:** {{SEV1 / SEV2 / SEV3}}
- **Dono:** {{time}}
- **Alerta relacionado:** {{nome/link}}
- **Última revisão:** {{AAAA-MM-DD}}

## Sintoma

{{O que se observa: alerta, reclamação, métrica.}}

## Impacto

{{Quem é afetado e como.}}

## Diagnóstico

1. {{Verificar dashboard X: link}}
2. {{Consultar logs/traces com filtro Y}}
3. {{Possíveis causas e como distinguir entre elas}}

## Mitigação

| Causa | Ação imediata |
|---|---|
| {{ex.: fila acumulando jobs}} | {{verificar se o worker de fila está rodando; reiniciar; checar jobs falhos e conexão com a fila}} |
| {{ex.: DLQ crescendo}} | {{inspecionar mensagens; corrigir consumidor; reprocessar}} |

## Escalonamento

{{Quem acionar e quando.}}

## Depois do incidente

- Postmortem sem culpados se SEV1/SEV2.
- Atualizar este runbook com o que se aprendeu.
