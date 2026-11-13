# Preparar um projeto existente

Objetivo: o agente entregar bem neste projeto e **provar** que terminou. Medimos que documentos longos gerados por agente não melhoram o código que ele escreve e encarecem cada demanda: o agente imita o código vizinho de qualquer jeito. O que ajuda é o que o código não mostra (comandos, regras que ninguém deve quebrar, armadilhas, como verificar) e um projeto que dê para verificar por máquina.

Resultado, em poucos arquivos curtos:

| Arquivo | O que é | Tamanho |
|---|---|---|
| `AGENTS.md` | comandos, ordem de verdade, regras inegociáveis, armadilhas, perguntar antes, pronto | ≤ 3 KB preenchido (o modelo tem ~1,5 KB fixo) |
| `docs/PRINCIPIOS.md` | princípios de arquitetura e de código, **copiados sem edição** | fixo |
| `docs/VERIFICACAO.md` | como subir o sistema e provar cada funcionalidade principal rodando-o | ≤ 3 KB |
| `docs/IA_FIRST.md` | diagnóstico e plano para o projeto ficar agent-friendly | ≤ 4 KB |

Documentos longos (ARCHITECTURE, CODEBASE_MAP, CODING_GUIDELINES, TESTING...) só se o dev pedir: siga [preparar-completo.md](preparar-completo.md) para o documento pedido.

## Regras

1. **Só o que o código não mostra.** Não descreva árvore de pastas, camadas nem fluxo que o agente lê sozinho.
2. **Sem evidência, não escreva.** Cada regra e cada comando tem `arquivo:linha` ou saída de comando. Fato que você não alcança vira VERIFICAR (`{{VERIFICAR: o que falta confirmar}}`); decisão do dev vira USUARIO.
3. **`PRINCIPIOS.md` não se edita.** Onde o projeto diverge de um princípio, registre em `IA_FIRST.md`, nunca no princípio.
4. **Nunca sobrescreva arquivo do projeto.** Já existe `AGENTS.md` ou `CLAUDE.md`? Proponha só o trecho que falta; o limite do projeto vale.
5. **Gerado é rascunho.** Diga ao dev que os documentos são para ele revisar e podar.
6. **Codificação:** se o detector avisar arquivos fora de UTF-8, use `grep -a` e preserve a codificação ao editar código.

## Passo a passo

1. **Detecte** (feito pelo `SKILL.md`).
2. **Uma rodada de perguntas, antes de copiar:**
   - o perfil (`perfil_sugerido`), e a variante do frontend se houver;
   - se usa Claude Code, para copiar o `CLAUDE.md` (se o projeto já tem `CLAUDE.md` ou `.claude/`, não pergunte);
   - se o dev quer algum documento longo.
   
   Dev indisponível: siga as recomendações e registre as suposições em `IA_FIRST.md`.
3. **Copie:** `bash <pasta da skill>/scripts/copiar-kit.sh <projeto> --minimo --perfil <perfil> [--frontend spa|servidor] [--modulos claude]`. No modo mínimo, não passe `github` nem `gitlab`: os modelos de PR/MR fazem parte do kit completo. Projeto governado: veja [abaixo](#projeto-já-governado).
4. **Rode o que existir,** se o dev permitir. O que rodou é o melhor fato que você tem; o que falhou ou não existe vai para o diagnóstico.
   - **Prefira o comando único de verificação** (ou typecheck, lint e um teste de um arquivo) à suíte inteira. Teto de ~10 minutos por comando: passou disso, interrompa e registre o tempo como achado.
   - **Rode sem modo de correção** (`--fix`, `--write`): o preparar não altera código.
   - **Não dá para instalar** (runtime ausente, dependência privada, credencial que você não deve usar): rode o que der sem instalar (checagem de sintaxe, inclusive em contêiner se houver Docker; build do que estiver instalado) e registre o que ficou de fora.
5. **Preencha o `AGENTS.md`:**
   - comandos que rodaram ou que existem no manifesto e no CI;
   - até 5 regras inegociáveis do padrão dominante, cada uma confirmada em pelo menos 2 arquivos além do citado;
   - armadilhas reais (ambiente, codificação, dado compartilhado, geração de código).
   
   Seção sem conteúdo real sai.
6. **Preencha o `docs/VERIFICACAO.md`** com de 5 a 10 funcionalidades principais: como chegar e o que observar. O que você rodou fica "verificado"; o resto, "não verificado".
7. **Segunda rodada de perguntas, se a leitura levantou decisões:** qual de duas formas convivendo imitar, o que fazer com um segredo encontrado, o que é dado de outro sistema. Mesma regra: numeradas, com recomendação; dev indisponível, siga a recomendação e registre.
8. **Preencha o `docs/IA_FIRST.md`.** É o produto principal do preparar:
   - a verificação executável: o que existe e o que falta;
   - onde o atalho não é o caminho certo (duas formas convivendo, dado com vários escritores, tipo de operação sem exemplo bom, regra que só a revisão garante);
   - segredos versionados: arquivo e linha, nunca o valor;
   - as próximas demandas em ordem de prioridade.
9. **Verifique:**

   ```bash
   bash <pasta da skill>/scripts/listar-marcadores.sh <projeto> --resumo
   bash <pasta da skill>/scripts/verificar-links.sh <projeto> --alterados
   bash <pasta da skill>/scripts/verificar-citacoes.sh <projeto> --alterados --mostrar
   ```

   Corrija toda citação errada. Com `--mostrar`, confira se a linha citada diz o que você afirma. `listar-marcadores` só reprova com marcador AGENTE; USUARIO e VERIFICAR que sobram são as decisões pendentes do relatório. Confira os tamanhos com `wc -c` contra a tabela do topo.
10. **Proponha** `.dev-ai-first/` no `.gitignore` (é o estado do modo entregar).
11. **Relatório na conversa:**
    - o que foi gerado;
    - as 3 primeiras demandas do `IA_FIRST.md`;
    - as decisões pendentes;
    - o que não foi verificado.
    
    Não commite.

## Projeto já governado

`situacao: governado`: o projeto já tem instruções para agentes (`AGENTS.md`/`CLAUDE.md` próprios, `.claude/`, `.cursor/rules`, skills locais). Elas mandam.

1. **Não toque no `AGENTS.md` nem no `CLAUDE.md` do projeto.** Copie só o resto: `copiar-kit.sh <projeto> --minimo --perfil <perfil> --arquivos docs/PRINCIPIOS.md,docs/VERIFICACAO.md,docs/IA_FIRST.md`. Se o projeto já tem algo equivalente a um deles, não copie esse.
2. **Leia as instruções existentes** e registre no `IA_FIRST.md` o que falta nelas: comandos, como provar, regras que ninguém deveria quebrar. Se o `AGENTS.md` passa muito do limite de uma leitura rápida, proponha a poda como item do plano, sem editar.
3. **Proponha ao dev uma linha** no `AGENTS.md` dele apontando para os documentos novos. Ele decide.
4. Siga os passos 4, 6, 7, 8, 9 e 11.

## Diagnóstico de prontidão

Projeto já preparado e o dev pede preparar de novo, ou "o que falta?": refaça o passo 7 contra o estado atual e mostre o que mudou desde o último `IA_FIRST.md`.
