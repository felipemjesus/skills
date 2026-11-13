# Felipe Martins · Skills

Coleção de **agent skills** para Claude Code e outros agentes de código compatíveis (Codex, Cursor). Cada skill traz conhecimento de domínio, boas práticas e fluxos guiados para o agente executar uma tarefa com qualidade.

Por enquanto a coleção tem **1 skill original** (⭐️): a [dev-ai-first](#dev-ai-first-).

## Instalação

### Rápida (recomendada)

Instale com a CLI [`skills`](https://www.npmjs.com/package/skills), que coloca a skill na pasta certa do seu agente:

```bash
npx skills add felipemjesus/skills
```

Para instalar uma skill específica:

```bash
npx skills add felipemjesus/skills --skill dev-ai-first
```

### Manual

Copie ou crie um link simbólico para a pasta de skills do seu agente:

```bash
# copiar uma skill
cp -r skills/dev-ai-first ~/.claude/skills/dev-ai-first

# ou manter atualizada a partir do clone
ln -s "$(pwd)/skills/dev-ai-first" ~/.claude/skills/dev-ai-first
```

## Uso

O agente escolhe a skill pelo campo `description` do `SKILL.md`, então basta pedir a tarefa em linguagem natural. No Claude Code, também dá para chamar pelo nome: `/dev-ai-first <pedido>`.

## O que são skills

Skills são instruções estruturadas que dão ao agente experiência num domínio específico. Cada uma fica numa pasta própria com um `SKILL.md` (metadados e procedimento) e, se precisar, `references/`, `scripts/` e `assets/`, carregados só quando a tarefa pede. O formato segue a especificação [agentskills.io](https://agentskills.io/specification).

## Catálogo

> ⭐️ = skill original deste repositório

### Minhas ⭐️

#### [dev-ai-first](./skills/dev-ai-first) ⭐️

Torna o repositório **IA first** e conduz as entregas do dev com agentes de código, **com qualidade**.

- **Preparar:** num projeto existente, roda o que o projeto tem e gera um `AGENTS.md` enxuto (comandos, regras inegociáveis, armadilhas, pronto), os princípios de arquitetura e de código como texto fixo, um mapa de verificação e um plano para o projeto ficar agent-friendly. Numa pasta vazia, entrevista o dev e o kit completo propõe a estrutura. Detecta o perfil (backend, frontend, fullstack) e respeita instruções que o projeto já tenha.
- **Entregar:** conduz cada demanda na medida do tamanho: critérios, exemplo de referência, teste primeiro observado, verificação rodando o sistema, revisão por subagente independente quando há risco, descrição do PR.
- **Avaliada às cegas** contra o agente puro em projetos reais: veja a seção 5 de [docs/dev-ai-first.md](docs/dev-ai-first.md).
- **Atalhos:** `retomar`, `revisar` e `pr`.

```text
/dev-ai-first preparar
/dev-ai-first Criar o comando único de verificação: lint dos arquivos alterados e as suítes unitárias, e rodar no CI nos PRs.
```

Demo (4min51, narrada): [youtu.be/E3Ixk_QQfMU](https://youtu.be/E3Ixk_QQfMU) · Documentação, uso real e evolução: [docs/dev-ai-first.md](docs/dev-ai-first.md)

## Estrutura do repositório

```text
.
├── skills/
│   └── dev-ai-first/          # uma pasta por skill
├── scripts/
│   └── validar-skills.py      # confere o frontmatter de toda skill contra a especificação
├── tests/                     # testes dos scripts das skills e do validador
├── docs/                      # documentação longa de cada skill
├── .github/workflows/         # CI: make verify em Linux e macOS
└── Makefile
```

## Desenvolvimento

Requisitos: `bash`, `git`, `make` e `python3` (sem dependências externas).

```bash
make check    # valida as skills: frontmatter, links e sintaxe dos scripts
make test     # roda os testes dos scripts e do validador
make verify   # check + test, o mesmo que o CI roda
```

Toda skill nova entra em `skills/<nome>/`, com `name` igual ao nome da pasta, e precisa passar no `make verify`.

## Licença

[MIT](LICENSE) © Felipe Martins
