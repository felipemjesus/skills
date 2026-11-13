# Checklist de design

Responda no plano e no PR, uma linha por item ("n/a" com motivo). **Fato:** com `arquivo:linha`, nunca pelo nome da pasta. **Decisão** (regra de negócio, contrato, dependência): pergunta com recomendação e caso de borda ([como perguntar](../CODING_GUIDELINES.md#8-regras-para-código-escrito-por-agentes-de-ia)).

1. **Com quais termos?** Os da [linguagem ubíqua](DOMAIN.md#4-linguagem-ubíqua); termo novo entra lá antes.
2. **Qual módulo é o dono?** Outro módulo só pela porta pública ou por evento ([fronteiras](../ARCHITECTURE.md#6-comunicação-entre-módulos)).
3. **Segue o padrão do projeto?** Imite o [exemplo de referência](../CODEBASE_MAP.md#exemplos-de-referência), sem misturar formas. Onde o padrão contraria um princípio, registrou em [ARCHITECTURE §11](../ARCHITECTURE.md#11-riscos-e-débitos-conhecidos) e perguntou se migra?
4. **Quais arquivos, com que papel?** Pela [tabela de responsabilidades](../ARCHITECTURE.md#41-responsabilidades); escrita e leitura na forma de cada uma.
<!-- se: estrutura-kit -->
   Escrita na [forma fixa](../ARCHITECTURE.md#51-comando-escrita); leitura: método no repository, mesmo curto.
<!-- fim: estrutura-kit -->
5. **O conceito já tem definição?** Regra só no domínio, uma vez: busque-a antes de escrever a condição. Se o sentido muda, todo leitor (consulta, tela, evento) muda junto; manter um no sentido antigo é pergunta ([detalhe](../CODING_GUIDELINES.md#um-conceito-em-memória-e-na-consulta)).
6. **Que invariantes podem quebrar?** O domínio protege cada uma, testada ([invariantes](DOMAIN.md#5-agregados-e-invariantes)).
7. **O framework ou uma biblioteca adotada resolve?** Documentação da versão instalada; solução própria só justificada ([versões](../CODING_GUIDELINES.md#versões-e-sintaxe-atual)).
8. **Precisa de interface?** Só para fronteira externa, duas implementações reais ou teste que exija ([regra](../CODING_GUIDELINES.md#interfaces-só-quando-há-motivo)).
9. **Dependência, migração ou contrato público?** É [Perguntar antes](../AGENTS.md#perguntar-antes); contrato muda compatível.
10. **O que acontece junto e o que vem depois?** Efeito externo (evento, e-mail, terceiro) só depois de confirmada a mudança.
<!-- se: backend -->
    Uma transação por caso de uso, só do módulo; limite contado ou fato que outro caso de uso grava: que trava os dois usam e que teste de concorrência ([transação](../ARCHITECTURE.md#51-comando-escrita)).
<!-- fim: backend -->
<!-- se: estados -->
    Qual transição da [tabela](../ARCHITECTURE.md#54-estados-e-transições)?
<!-- fim: estados -->
<!-- se: eventos -->
    Consumidor idempotente; reação que grava estado tem [entrega garantida](EVENTS.md#reação-que-grava-estado--reação-que-só-avisa).
<!-- fim: eventos -->
11. **E quando falha?** Externo fora, entrada inválida, repetição: [categoria de erro](../CODING_GUIDELINES.md#4-erros); ausência pelos [verbos](../CODEBASE_MAP.md#verbos-com-contrato-de-retorno).
<!-- se: frontend -->
    Como o erro do backend aparece na tela ([FRONTEND](FRONTEND.md))?
<!-- fim: frontend -->
12. **Quem pode e que dados?** Autorização, tenant, dado pessoal ([SECURITY.md](../SECURITY.md)).
13. **Que teste prova, e como verificar rodando?** Unitário no domínio ([testes](../TESTING.md#4-escrevendo-bons-testes)); a linha da funcionalidade no [mapa de verificação](VERIFICACAO.md).
<!-- se: backend -->
    Caso de uso com banco real.
<!-- fim: backend -->
<!-- se: bdd -->
    Visível ao usuário: aceitação.
<!-- fim: bdd -->
14. **É o mais simples hoje?** Código repetido até a terceira vez ([passo comum](../CODING_GUIDELINES.md#passo-comum-a-vários-casos-de-uso)); conceito repetido, nunca.
15. **Alguma ADR trata disso?** Siga ou proponha trocá-la; ADR nova só para decisão difícil de reverter ([ADRs](adr/README.md)).
