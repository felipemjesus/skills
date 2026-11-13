<!-- dev-ai-first -->
# AGENTS.md

{{AGENTE: o que o projeto faz, em uma frase; perfil (backend, frontend, fullstack) e stack em uma linha}}

## Comandos

| Para | Comando |
|---|---|
| Instalar | {{AGENTE: CMD_INSTALAR}} |
| Verificar tudo (pronto = verde) | {{AGENTE: CMD_CHECK}} |
| Rodar um teste | {{AGENTE: CMD_TESTE_ARQUIVO}} |
| Subir localmente | {{AGENTE: CMD_DEV}} |

Comando inexistente: "ainda não existe" ([docs/IA_FIRST.md](docs/IA_FIRST.md)).

## Ordem de verdade

1. O que a máquina verifica (lint, tipos, testes, CI). Nunca afrouxe a verificação para passar.
2. O padrão do projeto: imite o vizinho do mesmo tipo.
3. Os [princípios](docs/PRINCIPIOS.md), dentro do padrão. Conflito: siga o padrão, registre, pergunte.

## Regras inegociáveis

{{AGENTE: até 5 regras que um agente quebraria sem saber, com `arquivo:linha`; ou remova}}

## Armadilhas

{{AGENTE: o que o código não mostra e engana (ambiente, codificação, dado compartilhado, código gerado); ou remova}}

## Perguntar antes

Dependência nova, migração ou dados, contrato público, configuração de verificação ou CI, segredos, apagar código de uso não visível. Perguntar é não fazer: siga com o resto e diga "aguardando decisão".

## Pronto

Verificação verde (ou dito o que não rodou e por quê), comportamento observado como em [docs/VERIFICACAO.md](docs/VERIFICACAO.md), diff só com o pedido.

## Decisões registradas

{{USUARIO: autorizações permanentes do time, ou "nenhuma"}}

Mudou comando, verificação ou regra acima: atualize este arquivo no mesmo PR.
