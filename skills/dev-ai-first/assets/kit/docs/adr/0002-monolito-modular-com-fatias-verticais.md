# 0002. Monolito modular com fatias verticais e domínio rico

- **Status:** Proposta
- **Data:** {{USUARIO: AAAA-MM-DD}}

## Contexto

Precisamos de uma organização para o código novo em que mudanças fiquem locais (pessoas e agentes trabalham melhor com contexto delimitado), a operação seja simples e um caso de uso fique em poucos arquivos próximos, sem perder um modelo de domínio que concentre as regras. O critério de escolha é o custo de achar e ler um caso de uso.

## Opções consideradas

1. **Microsserviços.** Isolamento forte, mas custo operacional alto e fronteiras erradas caras de corrigir enquanto o domínio muda.
2. **Monolito em camadas.** Simples, mas sem fronteira de negócio.
3. **Módulos hexagonais em camadas** (`domain`, `application/...`, `infrastructure`). Até 5 níveis de pasta; um caso de uso espalhado por 4 ou 5 diretórios.
4. **Fatias verticais puras, sem domínio compartilhado.** A regra se espalha e se duplica entre fatias.
5. **Por conceito** (pasta do agregado com os casos de uso dentro). Tende a juntar tudo num `*Service` que cresce até misturar os casos de uso, o maior custo de leitura observado. Rejeitada.
6. **Pastas por tipo do framework com subcaminho `Conceito/Verbo` espelhado.** Idiomático, mas um caso de uso fica em 3 a 5 árvores e o espelhamento quebra fácil (singular × plural).
7. **Fatias verticais com domínio rico:** uma pasta por caso de uso em `features/`, uma pasta plana por tipo de arquivo no módulo, papel no sufixo do nome.

## Decisão

Opção 7 como padrão; opção 6 como variante aceita em bases que já seguem as pastas do framework, com o mesmo subcaminho e número gramatical em todas as árvores e o espelhamento verificado no CI. Um deploy; módulos em `src/modules/<contexto>/`; outro módulo só pela `<Modulo>Api`. Pastas, regras de dependência e matriz: [ARCHITECTURE.md §4.2](../../ARCHITECTURE.md#42-pastas) e [§4.1](../../ARCHITECTURE.md#41-responsabilidades). É a estrutura proposta para código novo; os princípios da [§4](../../ARCHITECTURE.md#4-estilo-arquitetural) valem em qualquer estrutura.

## Consequências

- **Positivas:** operação simples; transações locais; uma tarefa é uma pasta, o que reduz o contexto do agente; o service do agregado não tem onde crescer; CQRS natural.
- **Custos aceitos:** o ciclo de vida do agregado fica espalhado em N fatias (a [tabela de transições](../../ARCHITECTURE.md#54-estados-e-transições) o reúne); risco de domínio anêmico e de duplicação entre fatias, mitigado pela verificação de dependências no CI e pela revisão; escala é do sistema inteiro.
- **Quando revisitar:** um módulo precisa de escala, deploy ou isolamento próprio de forma recorrente (extração por *strangler fig*); ou uma pasta por tipo cresce a ponto de pedir subpastas por agregado.
