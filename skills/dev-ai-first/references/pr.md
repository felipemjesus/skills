# Descrição do PR (ou MR)

Objetivo: uma descrição que o revisor humano confere contra o diff sem precisar perguntar nada. Toda afirmação dela é verificável no diff ou na saída de um comando.

## Coletar
1. Branch base: a principal do projeto (`AGENTS.md` ou `CONTRIBUTING.md`; senão `git symbolic-ref refs/remotes/origin/HEAD`).
2. `git log --oneline <base>..HEAD` e `git diff --stat <base>...HEAD`; leia o diff inteiro, não só o resumo. Alterações não commitadas: avise que ficam fora do PR.
3. O arquivo da tarefa (`.dev-ai-first/<branch>.md`), se existir: critérios, decisões, evidências, não verificado.
4. O modelo do projeto (`.github/pull_request_template.md`, `.gitlab/merge_request_templates/` ou equivalente). Sem modelo, use as seções abaixo.

## Escrever
Preencha o modelo do projeto; sem modelo, use:

- **O quê:** 1 a 3 frases.
- **Por quê:** a issue e o contexto que o código não mostra.
- **Como foi verificado:** comandos rodados; o que foi observado; a saída do RED (teste falhando pelo motivo certo antes da implementação); por último, o que não foi verificado e por quê.
- **Impacto, riscos e rollback:** dados e migrações, contratos públicos (endpoints, eventos, API de módulo), compatibilidade, como desfazer.
- **Checklist de design:** as respostas, uma linha cada.
- **Perguntar antes:** cada item do diff que exigia autorização (dependência, migração, contrato, configuração), com a autorização citada literalmente (a frase da demanda que o exige, a resposta do dev, ou a linha de "Decisões registradas" do `AGENTS.md`).
- **Feito com agente de IA:** sim.

Regras:
- Sem dados do arquivo da tarefa (`/dev-ai-first pr` avulso), não invente o RED nem as decisões: escreva "não registrado" e pergunte ao dev o que souber.
- Confira cada frase contra o diff antes de entregar: afirmação que o diff não sustenta sai.
- PR com mais de ~400 linhas alteradas (sem gerados) ou com mais de um assunto: sugira dividir.

## Entregar
Mostre a descrição ao dev e grave-a no arquivo da tarefa. Abra o PR/MR (`gh pr create`, `glab mr create`) só se o dev pedir; push é ação dele.
