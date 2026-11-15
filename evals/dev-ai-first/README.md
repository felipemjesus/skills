# Avaliação da dev-ai-first

Avaliação no formato do [agentskills.io](https://agentskills.io/skill-creation/evaluating-skills), com **projetos sintéticos**: nenhum projeto real entra aqui. Fica fora da pasta da skill, para a skill instalada não carregar estes arquivos.

| Arquivo | O que é |
|---|---|
| `evals.json` | 5 casos (preparar com código, preparar projeto governado, corrigir um bug, validade do cupom, recusa de quantidade), cada um com asserções conferidas por script; a do teste oco roda os testes novos contra mutantes |
| `projetos/pedidos/` | projeto sintético em Python, só biblioteca padrão; tem um bug conhecido e um trecho duplicado fora do escopo |
| `projetos/governado/` | camada sobre `pedidos/` com um `AGENTS.md` do time |
| `rodar.py` | roda cada caso com e sem a skill (`claude -p`), confere as asserções e grava `benchmark.json` (acerto, tokens e tempo, com o delta) |
| `ativacao.json` | 20 pedidos: 10 que devem ativar a skill e 10 parecidos que não devem, separados em treino e validação |
| `ativacao.py` | roda cada pedido 3 vezes e mede a taxa de ativação |

## Como rodar

Gasta tokens da conta do Claude Code: rode sob demanda, nunca no CI. A pasta de saída deve ficar fora do repositório.

```bash
python3 -I evals/dev-ai-first/rodar.py --saida ../evals-saida/iteracao-1
python3 -I evals/dev-ai-first/ativacao.py --saida ../evals-saida/ativacao-1
```

`--execucoes 2` repete cada caso para reduzir o ruído; `--bracos com` mede só a skill (o braço sem ela não muda entre versões). `rodar.py --so-conferir` refaz só as asserções. Para comparar versões da skill, rode a mesma iteração antes e depois e compare os `benchmark.json`.

## Regras

- **Asserção boa exige evidência concreta.** Remova a que sempre passa nos dois braços: ela não mede nada.
- **Na descrição, ajuste olhando só o grupo `treino`.** Escolha a versão pelo acerto em `validacao`, e não copie para a descrição as palavras dos pedidos que falharam, porque isso é sobreajuste.
- **O que o script não confere** (qualidade das perguntas, aderência ao padrão) vai para um juiz às cegas, como nos relatórios A/B de [docs/avaliacao.md](../../docs/avaliacao.md).
