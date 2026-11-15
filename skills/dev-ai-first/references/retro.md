# Retro: melhorar o ambiente do agente

Só quando o dev pedir (`/dev-ai-first retro`). Olha a sessão que acabou e propõe mudanças no **ambiente** do agente (checks, instruções, ponteiros, acesso), não no código entregue. O sinal de que funciona: o `AGENTS.md` do projeto encolhe com o tempo, porque o que é mecânico vira check.

## Fontes

1. O arquivo da tarefa (`.dev-ai-first/<branch>.md`): decisões, evidências, achados da revisão, o que não foi verificado.
2. A conversa atual: correções que o dev precisou fazer, comandos que falharam, buscas repetidas, voltas no plano.
3. `git log` e `git diff` da branch contra a principal.

Sem arquivo da tarefa nem histórico útil, diga isso e pergunte ao dev o que incomodou na sessão.

## Procurar

| O que aconteceu | Proposta |
|---|---|
| erro que uma máquina pegaria (tipo, import proibido, formato, teste pulado) | um check: lint, hook, teste de arquitetura ou CI, com o comando; vira demanda no `docs/IA_FIRST.md` |
| decisão de julgamento que o dev corrigiu e que vai se repetir | uma linha nas regras inegociáveis do `AGENTS.md` (com `arquivo:linha`), ou no documento de padrões que o `AGENTS.md` aponta |
| o agente demorou para achar algo | um ponteiro curto no `AGENTS.md`: "quando X, leia Y" |
| linha do `AGENTS.md` que não mudou nada na sessão, ou que o código já mostra | remoção |
| o agente não tinha como ver ou rodar algo (log, banco de teste, comando) | demanda de acesso no `docs/IA_FIRST.md` |
| a verificação não pegou um erro que o dev pegou | linha nova em `docs/VERIFICACAO.md` ou um teste |
| erro do agente ao seguir esta skill | sugestão para a seção Armadilhas do `SKILL.md` da skill, só no relatório |

Uma ocorrência só não vira regra: proponha quando o dev corrigiu a mesma coisa duas vezes, ou quando o custo de repetir é alto (dado, segurança, contrato).

## Relatório

Em ordem de severidade, cada item com:
- o que aconteceu, com a evidência (comando, correção do dev, achado da revisão);
- o destino (tabela acima) e o texto ou comando proposto;
- o custo: linhas a mais no `AGENTS.md` (meta: zero ou negativo) ou o comando a configurar.

Não aplique nada: o dev escolhe os itens; aplique só os escolhidos, um por vez, e rode `verificar-links.sh` e `verificar-citacoes.sh --alterados` no fim. Mudança de lint, CI ou hook é ação de "Perguntar antes".
