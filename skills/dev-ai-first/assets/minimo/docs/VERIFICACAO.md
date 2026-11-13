# Mapa de verificação

> Como provar que algo funciona rodando o sistema como o usuário usa. Teste verde prova o código; esta verificação prova o comportamento. O agente chega à funcionalidade por aqui, age e observa. Mexeu numa funcionalidade: atualize a linha dela no mesmo PR.

## Como subir

{{AGENTE: comandos para subir localmente (dependências, banco, seed), a URL ou porta e como saber que subiu (rota de saúde, linha de log)}}

## Dados e contas de teste

{{AGENTE: usuários e perfis de teste, como criar dados (seed, factory, comando) e como voltar ao estado inicial; nunca dado ou credencial de produção}}

## Funcionalidades

Uma linha por funcionalidade principal.

<!-- se: backend -->
| Funcionalidade | Como chegar (endpoint, comando) | O que observar |
|---|---|---|
| {{AGENTE: funcionalidade}} | {{AGENTE: ex.: POST /vendas com corpo mínimo}} | {{AGENTE: status, corpo, estado lido pela API, evento ou log}} |
<!-- fim: backend -->

<!-- se: frontend -->
| Funcionalidade | Como chegar (URL, tela, atalho) | O que observar | Seletor estável |
|---|---|---|---|
| {{AGENTE: funcionalidade}} | {{AGENTE: URL e cliques a partir da tela inicial}} | {{AGENTE: texto, estado ou navegação esperados}} | {{AGENTE: papel e nome acessível, ou data-testid}} |

Seletor estável: papel e nome acessível; `data-testid` só sem papel. Nunca classe CSS ou posição.
<!-- fim: frontend -->

## Verificação ponta a ponta

<!-- se: backend -->
- **API ou comando:** chame com {{AGENTE: ferramenta, ex.: curl ou cliente HTTP do projeto}}; confira status, corpo e o estado gravado lido pela própria API; log sem erro.
<!-- fim: backend -->
<!-- se: frontend -->
- **Tela:** com {{AGENTE: ferramenta de automação do navegador, ex.: Playwright}}, abra a URL, aja pelo seletor estável, confira o resultado na tela e o console sem erro. Mudou a tela: captura no PR.
- **Suíte e2e:** `{{AGENTE: CMD_FRONTEND_E2E}}`.
<!-- fim: frontend -->
- No relato, diga o que foi observado e o que ficou sem verificar.

## O que não dá para verificar localmente

{{AGENTE: integrações sem ambiente de teste, tarefas agendadas, e-mail ou pagamento reais; para cada um, como se cobre (fake, teste de contrato, homologação)}}
