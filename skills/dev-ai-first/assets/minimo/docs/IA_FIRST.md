# Plano IA first

O que falta para um agente entregar neste projeto com segurança, do mais importante ao menos. Cada item aceito vira uma demanda. Gerado pela skill dev-ai-first em {{AGENTE: data}}; revise e pode à vontade.

## Resumo

{{AGENTE: em 2 ou 3 frases, o que hoje impede o agente de provar que terminou e o que mais ajudaria}}

## Verificação executável

O agente só prova que terminou se conseguir rodar o sistema e os testes.

| # | Item | Status | Evidência | Próxima demanda |
|---|---|---|---|---|
| 1 | Comando único de verificação que passa | {{AGENTE: ok, parcial, falta ou não se aplica}} | | |
| 2 | Teste de um arquivo só | | | |
| 3 | Testes do comportamento que roda em produção (integração, com banco real quando houver) | | | |
| 4 | Ambiente local reproduzível | | | |
| 5 | Lint e formatador | | | |
| 6 | Verificação de tipos | | | |
| 7 | CI roda a verificação em todo PR/MR | | | |
| 8 | Mapa de verificação ([VERIFICACAO.md](VERIFICACAO.md)) com as funcionalidades principais | | | |

## Arquitetura amigável para agentes

Onde o atalho não é o caminho certo hoje. O agente imita o vizinho, então um padrão inconsistente vira código inconsistente.

{{AGENTE: até 6 itens, cada um com `arquivo:linha`: funcionalidade espalhada por muitos lugares; mais de um lugar gravando o mesmo dado; duas formas convivendo para a mesma coisa (qual imitar?); dependência proibida que nada impede; tipo de operação sem exemplo bom; regra que só a revisão humana garante e uma ferramenta poderia garantir}}

## Segurança

{{AGENTE: segredos versionados (arquivo e linha, nunca o valor), dados sensíveis expostos; ou "nada encontrado"}}

## Próximas demandas

{{AGENTE: os itens acima em ordem de prioridade. Alta: sem eles o agente não prova que terminou, ou há risco ativo. Média: a qualidade depende da revisão humana. Baixa: melhora, não bloqueia}}
