---
name: dev-ai-first
description: Torna o repositório IA first e conduz as entregas do dev com agentes de código, com qualidade. Em pasta vazia, entrevista o dev sobre projeto, domínio e stack; em codebase existente, lê o código e gera AGENTS.md, ARCHITECTURE.md, CODEBASE_MAP.md, CODING_GUIDELINES.md, TESTING.md e ADRs descrevendo o projeto como ele é, mais um diagnóstico do que falta para o agente entregar bem. No dia a dia, conduz cada demanda: entender, planejar com checklist de design, teste primeiro, verificar, revisão independente, descrição do PR e documentação atualizada. Use quando o dev pedir para preparar o projeto para agentes, criar ou atualizar AGENTS.md/CLAUDE.md, implementar uma demanda, história ou bug, retomar uma tarefa, revisar um diff ou escrever a descrição de um PR. Also triggers on "make this repo agent-ready", "AI-first setup", "implement this ticket", "write the PR description".
license: MIT
compatibility: Agentes de código com suporte a Agent Skills (Claude Code, Codex, Cursor). Os scripts usam bash, git e ferramentas POSIX; testados em Linux e macOS.
metadata:
  author: Felipe Martins
  github: https://github.com/felipemjesus
  repository: https://github.com/felipemjesus/skills
  version: "1.0.0"
---

# dev-ai-first

Duas funções: **preparar** o repositório para ser desenvolvido com agentes, e **entregar** as demandas do dev nele com qualidade. A base é um kit de documentos agnóstico de stack em `assets/kit/`.

Caminhos como `scripts/...`, `references/...` e `assets/...` são relativos à pasta deste `SKILL.md`. Rode os scripts pelo caminho absoluto, um comando por chamada e sem `cd` antes (`bash /caminho/da/skill/scripts/x.sh <projeto>`): comando composto costuma cair fora das permissões liberadas pelo dev.

## 1. Descubra a situação

```bash
bash <pasta da skill>/scripts/detectar-projeto.sh <pasta do projeto>
```

A saída diz `situacao` (`vazio`, `codigo` ou `preparado`), manifestos, subprojetos, documentos para agentes já existentes e se há alterações não commitadas. Se aparecer `aviso` sobre subprojetos, pergunte qual preparar antes de seguir.

## 2. Escolha o modo

| Pedido do dev | Situação | Leia e siga |
|---|---|---|
| `preparar`, "deixar pronto para agentes", "criar AGENTS.md" | `vazio` | [references/preparar.md](references/preparar.md) §Pasta vazia |
| idem | `codigo` | [references/preparar.md](references/preparar.md) §Código existente |
| idem | `preparado` | [references/preparar.md](references/preparar.md) §Diagnóstico de prontidão |
| uma demanda, história, bug ou tarefa | `preparado` | [references/entregar.md](references/entregar.md) |
| uma demanda | `vazio` ou `codigo` | ofereça preparar antes (sem os documentos o agente adivinha); se o dev recusar, siga [references/entregar.md](references/entregar.md) com o que o projeto já tiver |
| `retomar` | qualquer | [references/entregar.md](references/entregar.md) §Retomar |
| `revisar` | qualquer | [references/revisar.md](references/revisar.md) |
| `pr` | qualquer | [references/pr.md](references/pr.md) |

Sem argumento e sem pedido claro: mostre a situação detectada e pergunte qual modo, com a recomendação.

## 3. Regras de todos os modos

- **O projeto manda.** Com o kit adotado, `AGENTS.md` do projeto e os documentos que ele aponta são a fonte das regras; esta skill conduz o processo e não repete nem substitui essas regras. Quando discordarem, vale a [ordem de verdade](assets/kit/AGENTS.md#ordem-de-verdade) do projeto.
- **Fato se busca, decisão se pergunta.** O que o código responde (stack, comandos, caminhos, quem chama quem), descubra com evidência `arquivo:linha`. Regra de negócio, meta, prazo, limite, dono, política: pergunte, numerado, cada pergunta com recomendação; nunca invente.
- **Nada irreversível sem pedido:** não commite, não faça push, não sobrescreva arquivo existente, não instale dependência, não mude CI nem configuração de lint ou de arquitetura. Proponha e pergunte.
- **Pronto é evidência.** Diga o comando rodado e o que ele mostrou; diga o que não pôde ser verificado.
- **Estado em arquivo, não na conversa:** decisões e progresso vão para o arquivo da tarefa no turno em que acontecem, para outra sessão continuar.
