# Entregar uma demanda

Objetivo: a demanda do dev pronta com qualidade e com evidência. Cada passo termina em algo verificável, e o estado fica num arquivo para qualquer sessão continuar.

As regras do projeto estão no `AGENTS.md` dele e nos documentos que ele aponta. Este roteiro diz **quando** usar cada uma; não as repita nem as substitua. Se o projeto não foi preparado, siga o mesmo roteiro com o que existir (README, scripts do manifesto, testes vizinhos) e diga no relato o que faltou.

## Sumário
- [0. Começar](#0-começar)
- [1. Entender](#1-entender)
- [2. Planejar](#2-planejar)
- [3. Teste primeiro](#3-teste-primeiro)
- [4. Implementar](#4-implementar)
- [5. Verificar](#5-verificar)
- [6. Revisar](#6-revisar)
- [7. Fechar](#7-fechar)
- [Arquivo da tarefa](#arquivo-da-tarefa)
- [Retomar](#retomar)

## 0. Começar
1. Leia o `AGENTS.md` do projeto inteiro (é curto de propósito).
2. Se há alterações não commitadas que não são desta demanda, pergunte antes de seguir.
3. Crie a branch no formato do `CONTRIBUTING.md` do projeto (no kit: `<tipo>/<issue>-<descricao-curta>`) a partir da branch principal atualizada.
4. Crie o [arquivo da tarefa](#arquivo-da-tarefa) com a demanda **literal**, como o dev escreveu.
5. Rode a verificação do projeto (`CMD_CHECK`, ou os testes) antes de mudar qualquer coisa: é a linha de base. Se não roda, anote o motivo; ele limita o que você vai poder provar.

## 1. Entender
- Releia o pedido frase a frase: cada frase vira um **critério de aceitação** no arquivo da tarefa. A frase que não cai em lugar nenhum é requisito que some.
- Leia o código do módulo afetado e os testes existentes (e o `CODEBASE_MAP.md`, se o projeto tiver).
- **Procure antes de presumir:** busque por nome e por conceito ("disponível", "bloqueado") antes de concluir que algo não existe ou de criar uma regra nova.
- Ache o **exemplo de referência** do tipo de operação (no `CODEBASE_MAP.md`, se houver; senão, o vizinho mais parecido no código) e um segundo vizinho do mesmo tipo. O código novo segue esse padrão, e os princípios do projeto valem dentro dele. Se o padrão contraria um princípio no trecho que você vai mexer, não corrija por conta própria: siga o padrão e registre a divergência como pergunta no plano.

## 2. Planejar
1. **Dimensione** a demanda. O processo cresce com ela:

   | Tamanho | Sinal | Plano | Revisão independente |
   |---|---|---|---|
   | pequena | até ~3 arquivos, um comportamento, padrão vizinho claro | critérios + checklist só dos itens que se aplicam, em poucas linhas | só se houver risco (passo 6) |
   | média | vários comportamentos ou camadas | checklist + plano "passo → como verificar", cada passo uma fatia completa | sim |
   | grande | decisão de arquitetura, várias semanas, contrato novo | design doc em `docs/design-docs/` com 2 ou 3 alternativas e uma recomendação | sim |
2. **Responda o checklist de design** do projeto (`docs/CHECKLIST_DESIGN.md`, se existir; senão, confira o plano contra `docs/PRINCIPIOS.md`), no arquivo da tarefa:
   - **fato** (quem chama, onde está o teste, qual transição existe): você responde, com `arquivo:linha`;
   - **decisão** (regra de negócio com mais de uma resposta defensável, contrato, dependência nova, item de "Perguntar antes"): vira pergunta.
3. **Pergunte em rodadas** (como no `CODING_GUIDELINES.md` §8 do projeto): numeradas, só as que não dependem de outra ainda aberta, cada uma com um cenário de borda concreto e redigida para que "sim" aceite a recomendação. Mostre o plano junto.
4. **Pare e espere** quando houver pergunta. Siga com o que não depende dela (ler, preparar o teste) e termine a resposta com "aguardando decisão", listando o que ficou parado. Urgência não transforma decisão em suposição.
5. Cada resposta do dev vai para o arquivo da tarefa no turno em que chega, com as palavras dele.

Demanda pequena e sem decisão: mostre o checklist e o plano em poucas linhas e siga sem esperar.

## 3. Teste primeiro
- Todo comportamento novo começa por um teste que **falha pelo motivo certo**: unitário no domínio e integração no caso de uso, conforme o `TESTING.md` do projeto.
- **Bug:** o teste reproduz o sintoma exato relatado; hipóteses ordenadas antes de instrumentar; depois procure a mesma causa nos outros pontos que usam o conceito (`TESTING.md` §9 do projeto). Não reproduziu? Isso é o achado: relate e pergunte o dado que falta.
- Guarde a saída do teste falhando (RED) no arquivo da tarefa. Se a infraestrutura de teste ainda não existe, o RED é o primeiro teste que roda: diga isso.

## 4. Implementar
- O mínimo para o teste passar, imitando o exemplo de referência; depois refatore com os testes verdes.
- Um passo do plano por vez. Ao concluir um passo, marque-o no arquivo da tarefa com o comando que o verificou. Sugira um commit por passo verificado (Conventional Commits, escopo = módulo); commite só se o dev pedir.
- Ação de "Perguntar antes" que surgir no meio: pare, pergunte, siga com o resto.

## 5. Verificar
Do mais rápido ao completo: o teste do arquivo → o teste de integração da fatia → o comando de verificação completa do projeto (`CMD_CHECK` no `AGENTS.md`) → **rodar o sistema como o usuário usa**, pela linha da funcionalidade em `docs/VERIFICACAO.md` (sem a linha, crie-a), quando a mudança é visível ao usuário.
- Falhou? Corrija o código, nunca a verificação: não pule teste, não afrouxe asserção, lint, tipos ou baseline.
- Registre o que foi **observado** (saída, resposta da API), não só "passou", e o que não pôde ser rodado e por quê.

## 6. Revisar
**Revisão independente** ([revisar.md](revisar.md)): um subagente sem o histórico da conversa confere o diff contra os critérios e as regras do projeto. Uma rodada de correção; o que continuar divergindo vai ao dev como decisão. Faça quando:
- a demanda é média ou grande;
- ou o diff toca algo de "Perguntar antes" (dependência, dados ou migração, contrato público, configuração de verificação, segredos), autorização ou segurança;
- ou a verificação não pôde rodar.

Fora disso (pequena, sem risco e verificada), faça a **autorrevisão:** releia o diff contra cada critério e contra o exemplo de referência, e registre o resultado no arquivo da tarefa.

## 7. Fechar
1. **Documentação:** atualize só os documentos que o projeto tem e que a mudança invalidou. Percorra a lista "Mantendo a documentação" do `AGENTS.md`, se houver (termo novo no `docs/DOMAIN.md`, evento no `docs/EVENTS.md`, comando no `AGENTS.md`...). Atualize a linha da funcionalidade em `docs/VERIFICACAO.md`. Se a revisão apontou algo que uma ferramenta pegaria (lint, tipos, teste de arquitetura), proponha a regra automática no `docs/IA_FIRST.md` (ou na tabela "regra → garantida por" do `ARCHITECTURE.md` §9, se existir). Se a mudança trouxe algo que o projeto não tinha (primeiro evento, primeira tela, primeira API), acrescente o documento do módulo com `copiar-kit.sh <projeto> <as mesmas flags de .dev-ai-first/kit.lst> --modulos <novo> --arquivos <arquivo do módulo>`. Rode `verificar-links.sh <projeto> --alterados <branch principal>` e `verificar-citacoes.sh <projeto> --alterados <branch principal>`.
2. **Definição de pronto:** confira cada item da seção do `AGENTS.md` do projeto, com evidência.
3. **Descrição do PR:** siga [pr.md](pr.md).
4. **Relato final ao dev**, nesta ordem: resultado em uma frase → critérios (atendido, parcial, ausente) → como foi verificado → o que não foi verificado → ações de "Perguntar antes" executadas, cada uma com a autorização citada → próximos passos ou "aguardando decisão".

## Arquivo da tarefa

Guarda o estado da demanda para que outra sessão continue lendo só arquivos.

- **Onde:** `.dev-ai-first/<branch>.md` na raiz do projeto, com `/` da branch trocada por `-` (sem git: o nome da demanda). Não grave dentro de `.git/`: os agentes costumam bloquear escrita ali. A pasta não é versionada: se `.dev-ai-first/` não está no `.gitignore`, nunca use `git add -A` ou `git add .` (adicione arquivo por arquivo) e proponha ao dev incluir a linha no `.gitignore`. Demanda grande usa o design doc versionado em `docs/design-docs/`, e o arquivo da tarefa só aponta para ele.
- **Formato:**

```markdown
# <demanda em uma linha>
Branch: <branch> · Tamanho: pequena | média | grande · Status: planejando | aguardando decisão | implementando | revisando | pronta

## Demanda (literal)
## Critérios de aceitação
| # | Critério (frase da demanda) | Teste que prova | Status |
## Checklist de design
## Decisões (pergunta → resposta do dev, com as palavras dele, e data)
## Plano
- [ ] passo → como verificar
## Evidências (RED, verificação, revisão)
## Não verificado
```

## Retomar
`/dev-ai-first retomar` (ou sessão nova, ou contexto resumido):
1. Ache o arquivo da tarefa da branch atual (`git branch --show-current`); se houver mais de um candidato, pergunte.
2. Releia do disco o arquivo da tarefa, o design doc se houver, e os arquivos que vai editar. Nunca edite a partir de trecho lembrado.
3. Confira o estado real com `git log` e `git diff` contra a branch principal: commit é fato; o arquivo da tarefa é intenção. Divergiu? Vale o código; atualize o arquivo e diga o que divergiu.
4. Rode o teste do último passo marcado para confirmar que ele ainda passa.
5. Diga ao dev em duas linhas onde a demanda está e qual o próximo passo; siga.
