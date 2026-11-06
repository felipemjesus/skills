# Revisar um diff

Quem revisa não é quem escreveu. A revisão roda num subagente (no Claude Code, a ferramenta Agent) ou numa sessão nova, sem o histórico da conversa. Por quê: o revisor que recebe os argumentos do autor tende a conferir os argumentos, não o diff.

## Montar o pedido de revisão

O pedido é autossuficiente e leva **só**:
1. A demanda literal e a tabela de critérios e decisões (do arquivo da tarefa ou do design doc). Sem arquivo da tarefa (`/dev-ai-first revisar` avulso): pergunte ao dev o que a mudança devia fazer, ou use a descrição do PR.
2. O intervalo do diff: `git diff <branch principal>...HEAD`, mais as alterações não commitadas, se houver.
3. Onde estão as regras: `AGENTS.md`, `CONTRIBUTING.md` (seção "Revisão de código"), `ARCHITECTURE.md` §4.1 do projeto.

**Não** leve as justificativas do autor, o que já foi discutido nem o que aceitar.

## Instruções para o revisor

Copie para o pedido:

> Revise o diff abaixo deste repositório. Leia `AGENTS.md` e siga a seção "Revisão de código" do `CONTRIBUTING.md`. Se o projeto não tiver essas seções, olhe nesta ordem: correção (faz o que a demanda pede? casos de borda e de erro?), design (fronteiras e responsabilidades seguidas pelo código vizinho, regra de negócio no lugar certo, recurso do framework em vez de solução própria), testes (cada critério tem teste que falharia se ele fosse falso?), segurança e dados, código típico de IA (abstração especulativa, comentário que repete o código, erro tratado de forma genérica, duplicação do que já existe), gambiarras (teste pulado, lint desativado, tipo frouxo), API obsoleta para a versão instalada.
>
> Responda em dois blocos separados:
> 1. **Decidido x feito:** cada critério e decisão da tabela, marcado **atendido**, **parcial** ou **ausente**, citando a linha; e o que o diff faz sem ter sido pedido.
> 2. **Achados:** prefixados `bloqueante:`, `sugestão:` ou `dúvida:`, cada um com `arquivo:linha` ou link da documentação oficial; achado grave descreve o cenário concreto de falha. Procure no diff cada item de "Perguntar antes" do `AGENTS.md` (dependência, migração, contrato, configuração de verificação, convenção, interface nova, infraestrutura): ocorrência sem autorização registrada é `bloqueante:`.
>
> Não comente o que o lint ou o CI já pegam. Zero achados é um resultado válido. Termine com um veredito: **pronto**, **mudanças** (lista dos `bloqueante:`) ou **precisa de decisão** (cada decisão com a recomendação). Não edite arquivos.

## Depois da revisão
1. Confira cada achado no código antes de agir: o revisor também erra. Descartou um? Diga por quê no arquivo da tarefa.
2. Corrija os `bloqueante:` numa rodada só e rode a verificação de novo.
3. Re-revisão (se houve correção) reabre só o que divergiu. O que continuar falhando vai ao dev como "precisa de decisão".
4. Registre o veredito e os achados tratados no arquivo da tarefa; eles entram na descrição do PR.
5. Achado que se repete em demandas diferentes: proponha ao dev uma regra automática (lint ou arquitetura) em vez de confiar na próxima revisão.
