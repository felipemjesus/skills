---
name: dev-ai-first
description: 'Torna o repositório IA first e conduz as entregas do dev com agentes de código, com qualidade. Em codebase existente, lê o código e gera um AGENTS.md enxuto (comandos, regras inegociáveis, armadilhas, definição de pronto), os princípios de arquitetura e de código, um mapa de verificação e um plano para o projeto ficar agent-friendly; documentos longos (ARCHITECTURE.md, CODEBASE_MAP.md, ADRs) só sob pedido ou em pasta vazia, onde entrevista o dev e propõe a estrutura. No dia a dia, conduz cada demanda na medida do tamanho: entender, planejar, teste primeiro, verificar rodando, revisão independente quando há risco, descrição do PR. Use quando o dev pedir para preparar o projeto para agentes, criar ou atualizar AGENTS.md/CLAUDE.md, implementar uma demanda, história ou bug, retomar uma tarefa, revisar um diff ou escrever a descrição de um PR. Also triggers on "make this repo agent-ready", "AI-first setup", "implement this ticket", "write the PR description".'
license: MIT
compatibility: Agentes de código com suporte a Agent Skills (Claude Code, Codex, Cursor). Os scripts usam bash, git, perl e ferramentas POSIX; testados em Linux e macOS.
metadata:
  author: Felipe Martins
  github: https://github.com/felipemjesus
  repository: https://github.com/felipemjesus/skills
  version: "3.2.0"
---

# dev-ai-first

Duas funções: **preparar** o repositório para ser desenvolvido com agentes, e **entregar** as demandas do dev nele com qualidade. Em projeto existente, o preparar é enxuto: um `AGENTS.md` com o que o código não mostra, os princípios de arquitetura e de código como texto fixo, um mapa de verificação e um plano para o projeto ficar agent-friendly. Em pasta vazia, o kit completo de `assets/kit/` propõe a estrutura. O perfil (backend, frontend SPA ou servidor, fullstack) filtra o que se aplica.

## Regras de todos os modos

- **Padrão do projeto + princípios.** O código novo segue o padrão do projeto (o exemplo de referência), e os princípios valem dentro dele. Onde o padrão contraria um princípio, registre e pergunte; não corrija por conta própria.
- **O projeto manda.** `AGENTS.md` do projeto e os documentos que ele aponta são a fonte das regras; esta skill conduz o processo e não repete essas regras. Quando discordarem, vale a [ordem de verdade](assets/kit/AGENTS.md#ordem-de-verdade) do projeto.
- **Fato se busca, decisão se pergunta.** O que o código responde (stack, comandos, caminhos, quem chama quem), descubra com evidência `arquivo:linha`. Regra de negócio, meta, prazo, limite, dono, política: pergunte, numerado, com recomendação; nunca invente.
- **Ações que pedem autorização do dev:** commit, push, sobrescrever arquivo existente, instalar dependência, mudar CI ou configuração de lint e de arquitetura. Proponha e pergunte. Ler, rodar testes e comandos só de leitura, criar branch e escrever os documentos novos não precisam.
- **Pronto é evidência:** o comando rodado e o que ele mostrou, e o que não pôde ser verificado.
- **Estado em arquivo, não na conversa:** decisões e progresso vão para o arquivo da tarefa no turno em que acontecem, para outra sessão continuar.

## Armadilhas

Erros que agentes cometeram usando esta skill. Cada correção que o dev precisar fazer vira uma linha aqui.

- **Documento longo "para ajudar".** Em projeto existente, só o mínimo do [preparar](references/preparar.md); documento longo só se o dev pedir.
- **Editar `docs/PRINCIPIOS.md` para caber no projeto.** É texto fixo; a divergência vai para o `docs/IA_FIRST.md`.
- **Rodar lint ou formatador com `--fix`/`--write` no preparar.** O preparar não altera código: rode sem modo de correção.
- **Esperar a suíte inteira.** Prefira o comando único de verificação ou um arquivo de teste; passou de ~10 minutos, interrompa e registre o tempo.
- **Instalar com credencial versionada.** Não use: rode o que der sem instalar e registre o que ficou de fora.
- **Consertar o que está quebrado fora do pedido** (configuração de teste, lint, CI). Registre como pergunta e não mexa.
- **Concluir que algo não existe sem buscar.** Busque por nome e por conceito antes de criar regra ou função nova.
- **Editar a partir de trecho lembrado** depois de resumo de contexto ou em sessão nova. Releia o arquivo do disco.
- **`git add -A` ou `git add .`** com `.dev-ai-first/` fora do `.gitignore`: adicione arquivo por arquivo.
- **Comando composto** (`cd x && ...`): costuma cair fora das permissões liberadas pelo dev. Rode os scripts pelo caminho absoluto, um comando por chamada: `bash /caminho/da/skill/scripts/x.sh <projeto>`.

Caminhos como `scripts/...`, `references/...` e `assets/...` são relativos à pasta deste `SKILL.md`. Os scripts aceitam `--help`.

## 1. Descubra a situação

```bash
bash <pasta da skill>/scripts/detectar-projeto.sh <pasta do projeto>
```

A saída traz `situacao` (`vazio`, `codigo`, `governado` ou `preparado`), linguagens, manifestos, subprojetos, ambiente local, forja, codificação, instruções para agentes já existentes, perfil e módulos sugeridos, possíveis segredos versionados e avisos. Se houver aviso de subprojetos, pergunte qual preparar.

## 2. Escolha o modo

| Pedido do dev | Situação | Leia e siga |
|---|---|---|
| `preparar`, "deixar pronto para agentes", "criar AGENTS.md" | `codigo` ou `governado` | [references/preparar.md](references/preparar.md) (enxuto: AGENTS.md mínimo, princípios fixos, mapa de verificação, plano IA first) |
| idem | `vazio` | [references/preparar-completo.md](references/preparar-completo.md) §Pasta vazia |
| idem | `preparado` | [references/preparar.md](references/preparar.md) §Diagnóstico de prontidão |
| um documento longo (ARCHITECTURE, CODEBASE_MAP...) | qualquer | [references/preparar-completo.md](references/preparar-completo.md), só para o documento pedido |
| uma demanda, história, bug ou tarefa | qualquer | [references/entregar.md](references/entregar.md); em `vazio` ou `codigo`, ofereça preparar antes, sem insistir |
| `retomar` | qualquer | [references/entregar.md](references/entregar.md) §Retomar |
| `revisar` | qualquer | [references/revisar.md](references/revisar.md) |
| `pr` | qualquer | [references/pr.md](references/pr.md) |

Sem argumento e sem pedido claro: mostre a situação detectada e pergunte qual modo, com a recomendação.
