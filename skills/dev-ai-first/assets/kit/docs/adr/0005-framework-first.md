# 0005. Framework first

- **Status:** Proposta
- **Data:** {{USUARIO: AAAA-MM-DD}}

## Contexto

Peças próprias para o que o framework já oferece (relógio e gerador de ID injetáveis, `Result` próprio, publicador de eventos com relay, interfaces de autorização e flags, entidade e mapper separados quando o model do ORM já é a entidade idiomática, builders de teste à mão) são razoáveis uma a uma, mas o conjunto afasta a aplicação do que a documentação mostra. Pessoas não reconhecem o projeto, e agentes, que conhecem bem o idioma do framework, erram quando o projeto foge dele.

## Opções consideradas

1. **Independente de framework.** Domínio puro, toda dependência atrás de interface; portável, mas com muita cerimônia e longe do idioma.
2. **Framework first.** Usar os recursos que o framework e as bibliotecas adotadas documentam, como a documentação mostra; solução própria só quando não oferecem.
3. **Livre por caso.** Rápido no início, inconsistente com o tempo.

## Decisão

Opção 2. Antes de criar abstração, utilitário ou infraestrutura, procure o recurso na documentação oficial da versão instalada; solução própria só com justificativa no PR ou em ADR. Recursos do framework não ganham interface ([ADR-0004](0004-interfaces-so-em-fronteiras.md)). Versão estável mais recente e sintaxe atual: [CODING_GUIDELINES.md](../../CODING_GUIDELINES.md#versões-e-sintaxe-atual). Framework first não relaxa a separação de responsabilidades: o recurso é usado no artefato responsável por ele ([ARCHITECTURE.md §4.1](../../ARCHITECTURE.md#41-responsabilidades)).

## Consequências

- **Positivas:** menos código próprio; o projeto parece um projeto típico do framework; pessoas e agentes aplicam o que já sabem; testes usam os helpers oficiais.
- **Custos aceitos:** código de negócio acoplado ao framework (trocar de framework fica caro); atualizações de versão afetam mais código. Mitigação: regra concentrada no domínio, fronteiras externas atrás de `Port`, dependências verificadas no CI.
- **Quando revisitar:** o framework deixar de ser mantido, ou um recurso dele se mostrar insuficiente de forma recorrente.
