# Como avaliar a skill dev-ai-first

Uma mudança na skill só entra se uma avaliação mostrar **custo menor ou igual e acerto igual ou maior** que a versão anterior. Este é o roteiro usado nas rodadas de melhoria.

## Preparar o ambiente

1. **Projetos reais,** copiados para uma pasta de teste com nomes neutros (`a-1`, `b-7`). Os originais não são tocados. Os `.env*` ficam de fora. Cada cópia ganha `git init` e um commit inicial.
2. **Sigilo:** relatórios e mudanças na skill falam só da skill. Nada de nome, domínio, caminho ou trecho de código dos projetos; achados por projeto são agregados em contagens.
3. **Amostra:** de 3 a 6 projetos que cubram os casos:
   - backend, frontend e fullstack;
   - SPA e telas renderizadas no servidor;
   - projeto com e sem manifesto;
   - projeto já governado por instruções para agentes;
   - legado fora de UTF-8.

## Duas camadas

| Camada | O que roda | Custo |
|---|---|---|
| 1. Scripts | `detectar-projeto.sh`, `verificar-links.sh`, `verificar-citacoes.sh` e `listar-marcadores.sh` em todos os projetos, comparados com uma contagem independente (ex.: manifestos e instruções para agentes encontrados por `find`) | baixo |
| 2. Agente | o modo inteiro, num **subagente novo** por projeto, que lê a skill pelo caminho do repositório, com o dev indisponível (segue as recomendações e registra cada pergunta) e sem acesso externo | alto |

## O que medir

| Tipo | Métricas |
|---|---|
| Custo | tokens, tempo, chamadas de ferramenta; parte do esforço gasta com o kit × com o projeto (estimativa do agente) |
| Custo recorrente | bytes do `AGENTS.md` (toda sessão) e dos documentos lidos por demanda |
| Acerto | citações `arquivo:linha` erradas, exemplos do kit que sobraram, caminhos inexistentes (`verificar-citacoes.sh`); links quebrados; pendências USUARIO e VERIFICAR |
| Fidelidade | prescrição do kit num projeto com estrutura própria (meta: 0); princípios presentes nos documentos gerados |
| Regras | não sobrescreveu, não commitou, não inventou decisão |

## Rodada

1. **Linha de base:** a versão atual da skill em todos os projetos da amostra. Guarde o resultado numa branch da cópia (`baseline-vN`).
2. **Achados:** junte os atritos que os agentes relatam com as métricas. Uma falha que se repete vira uma mudança proposta. Cada proposta diz o ganho esperado.
3. **Aprovação** do dono da skill.
4. **Aplicar** e rodar `make verify`. Cada script novo ou alterado ganha teste, inclusive o teste que copia o kit em todas as combinações de estrutura, perfil e módulo.
5. **Repetir** nos mesmos projetos, a partir do commit inicial, com o mesmo roteiro.
6. **Comparar** e aplicar o critério de aceite. O que piorar volta.

## Cuidados

- **Quem constrói não escreve as instruções de quem avalia:** o roteiro do subagente é o mesmo em todas as rodadas.
- **Uma rodada mede uma coisa:** não mude o roteiro e a skill ao mesmo tempo.
- **Número sem amostra é anedota:** com 3 projetos, diferenças pequenas (menos de 10%) não contam.
