@AGENTS.md

## Notas específicas do Claude Code

- As regras de `AGENTS.md` valem integralmente. Este arquivo só acrescenta detalhes do Claude Code.
- Delegue a um subagente quando a tarefa exige ler muito e só a conclusão importa (mapear módulos, buscar usos) ou precisa de contexto limpo (revisão). O pedido é autossuficiente e de escopo fechado, sem o histórico da conversa (para revisão, siga o [CONTRIBUTING.md](CONTRIBUTING.md#revisão-de-código)). Quem delega recolhe e confere o resultado antes de relatar.
- Uma demanda por conversa: cada demanda independente começa numa conversa limpa; compacte só entre tarefas, depois de um commit ou passo verificado, nunca no meio de uma edição.
- Um `CLAUDE.md` dentro de `src/modules/<modulo>/` pode acrescentar contexto local daquele módulo. Mantenha-o curto, sem repetir regras globais e sem contradizê-las: o agente segue a última regra que leu.

## Ao compactar

O Claude Code lê este arquivo ao resumir a conversa. Preserve: objetivo e critérios da demanda atual; decisões tomadas e perguntas pendentes; arquivos alterados; últimos resultados de verificação e erros.
