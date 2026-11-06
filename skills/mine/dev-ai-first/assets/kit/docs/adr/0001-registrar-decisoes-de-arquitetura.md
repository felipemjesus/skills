# 0001. Registrar decisões de arquitetura

- **Status:** Aceita
- **Data:** {{USUARIO: AAAA-MM-DD}}

## Contexto

Decisões arquiteturais se perdem em conversas, chats e na memória das pessoas. Pessoas novas e agentes de IA veem o resultado no código, mas não o motivo, e acabam revertendo decisões ou repetindo discussões.

## Decisão

Registrar decisões significativas como ADRs em `docs/adr/`, no formato de [0000-template.md](0000-template.md), versionadas com o código e revisadas por PR.

## Consequências

- O motivo de cada decisão fica acessível a qualquer pessoa ou agente que leia o repositório.
- Custo pequeno de escrita a cada decisão relevante.
- ADRs aceitas não são editadas; mudanças geram nova ADR que substitui a anterior.
