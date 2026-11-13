# Princípios de arquitetura e de código

> Valem em qualquer organização do código: em camadas, hexagonal ou por fatias. Os nomes de papel abaixo descrevem a função, não um tipo ou uma pasta.

## Precedência

- O código novo segue o padrão do projeto: imite o exemplo de referência vizinho, do mesmo tipo. Não misture duas formas no mesmo módulo.
- Dentro do padrão, estes princípios valem.
- Onde o padrão contraria um princípio, não corrija por conta própria: siga o padrão, registre a divergência e pergunte se o dev quer migrar.
- Exceção a uma regra se explica no PR.

## Disciplina de implementação

1. Precisa existir? Se o pedido não exige, não faça.
2. Já existe? Procure o conceito, o método e o recurso do framework antes de criar.
3. Faça o mínimo, no padrão do projeto.
- Antes de criar, ache dois vizinhos do mesmo tipo e imite.
- Procure antes de presumir: nome de API, campo, comando e regra se confirmam no código ou na documentação.
- Não corrija vizinho fora do pedido; aponte e pergunte.
- Pronto é evidência: teste que falhou e passou, verificação rodada, sistema usado como o usuário usa.

## Responsabilidades por papel

Cada papel tem um motivo para mudar, qualquer que seja o nome que o projeto lhe dá.
- **Entrada** (o ponto que recebe a requisição ou o comando): só recebe, delega e formata a saída.
- **Validação de forma** (presença, tipo, tamanho): fica na borda. Regra de negócio não.
- **Caso de uso**: orquestra a operação. Carrega, autoriza, chama o domínio, grava. Não tem `if` de negócio próprio.
- **Domínio** (entidade, value object, agregado): guarda a regra de negócio em métodos com nome de intenção e predicados com nome do negócio. Domínio rico, não anêmico.
- **Integração externa** (terceiro, LLM, SDK): fica atrás de uma fronteira que traduz nomes e erros para o domínio.
<!-- se: backend -->
- **Persistência**: fica num lugar só. ORM e SQL não vazam para entrada, caso de uso nem domínio. A persistência não abre nem confirma transação e não decide regra.
- **Transação**: abre e fecha no caso de uso, uma por operação, sem aninhar.
<!-- fim: backend -->
<!-- se: frontend -->
- **Tela**: apresenta e coleta. O backend é o dono da regra; a tela mostra as ações e os erros que ele devolve.
- A tela não duplica validação de negócio. Validação de forma na tela é conforto do usuário, nunca a garantia.
<!-- fim: frontend -->

Sinais de violação: regra de negócio na entrada, na tela ou numa reação a evento; condição de negócio montada fora do domínio; erro engolido; escrever antes de validar.

## Framework first

Antes de criar abstração, utilitário, wrapper ou infraestrutura, procure o recurso na documentação oficial do framework e das bibliotecas adotadas e use-o como ela mostra. Relógio, gerador de ID, autorização, feature flags, filas, cliente HTTP e cache vêm do framework. Solução própria só quando ele não oferece, com justificativa.

## Versões e sintaxe atual

A versão em uso está no lockfile. Consulte a documentação dessa versão antes de escrever: agentes tendem a repetir a sintaxe do treinamento. Código novo usa a forma recomendada para a versão instalada, sem API obsoleta. Dependência nova entra na versão estável mais recente compatível, depois de perguntar.

## Interfaces só quando há motivo

Use interface só para fronteira externa (lenta, instável ou cara em teste), mais de uma implementação real ou teste sem outro jeito de trocar a dependência. Caso de uso, serviço de domínio e porta pública com uma implementação são classes concretas.
- Teste da remoção: se apagar a interface e a complexidade sumir junto, era só passagem.
- "Não precisa de interface" não autoriza chamar sistema externo direto do caso de uso.

## Um conceito, uma definição

- Cada conceito de negócio tem uma definição, com nome, no domínio. O predicado em memória e o critério de consulta leem do mesmo lugar.
- Busque o conceito antes de escrever uma condição de negócio.
- Uma implementação viva por conceito: a nova substitui a antiga no mesmo ciclo.
- Regra de três: abstraia na terceira repetição. Código parecido por coincidência não é duplicação; conhecimento duplicado é bug.

exemplo: "estoque disponível" é um método de `Estoque`. Criar `Pedido` e confirmar `Pagamento` chamam esse método; nenhum dos dois reescreve `saldo - reservados`.

## Orientação a objetos

Lógica de aplicação e de domínio fica em classes: cada regra tem um dono com nome, e as dependências aparecem no construtor. Funções soltas só na borda do framework: inicialização, configuração, callbacks exigidos por biblioteca, fábricas de dados de teste. O que seria utilitário vira value object, método do agregado ou serviço injetado. Nada de classe só com métodos estáticos nem objeto literal como namespace.

## Nomes

- Tipos em português com sufixo técnico em inglês, sem preposição nem artigo.
- Use os termos da linguagem do negócio, iguais em toda a cadeia, da entrada ao evento.
- Variável e campo com o nome do conceito, sem abreviação, sinônimo ou genérico (`data`, `result`).

exemplo: `ItemPedido` e `PedidoId`, não `ItemDoPedido` nem `IdDoPedido`.

## API pública de módulo

Outro módulo fala com um módulo só pela porta pública dele, que delega e não tem regra. Nunca importe o interior de outro módulo nem escreva nos dados dele.

## Erros com categoria fechada

Toda exceção de domínio pertence a uma categoria fechada, e cada categoria tem um tratamento: não encontrado, sem permissão, entrada inválida, estado não permite (conflito), regra violada.
- A mensagem diz o que aconteceu, os valores e o que fazer. Nunca genérica, stack trace ou SQL.
- Desfecho que não é falha é resultado com nome, não exceção.
- Nunca engula erro nem o converta em vazio. A conversão erro → resposta fica num tratamento global.

## Testes primeiro

Escreva o teste antes do código e veja-o falhar pelo motivo certo. Um comportamento por teste. Não enfraqueça teste para passar.
<!-- se: backend -->
Os testes do caso de uso usam banco real, não mock do ORM.
<!-- fim: backend -->
<!-- se: frontend -->
Teste a tela pelo papel acessível e pelo texto visível, não por classe de estilo ou estrutura interna.
<!-- fim: frontend -->
<!-- se: backend -->

## Transação e concorrência

Falha de concorrência não avisa: cada transação sozinha parece correta.
- Valide e calcule antes da primeira escrita.
- Efeito externo (evento, HTTP, e-mail, fila) só depois do commit.
- Limite contado: contar e gravar na mesma transação, com trava da linha dona do limite ou restrição no banco.
- Write skew: quando um caso de uso grava um fato e outro o lê como regra, os dois serializam no mesmo ponto (mesma trava ou restrição).
- Cada caso tem um teste que dispara as operações em paralelo e falha sem a proteção.

exemplo: estornar `Pagamento` e faturar `Pedido` travam a mesma linha do `Pedido`; sem isso, um pedido estornado pode ser faturado.
<!-- fim: backend -->

## Tamanho por responsabilidade

Tamanho e complexidade se julgam pelo papel, não por número rígido. O número é gatilho para olhar. No caso de uso, muitas linhas indicam montagem repetida ou regra fora do domínio; no domínio, pesa a ramificação. O método principal é um índice: pré-condições primeiro, depois passos com nome de intenção. Extraia por intenção, nunca só para caber.

## Arquitetura amigável para agentes

- **O caminho convencional é o mais curto:** seguir o exemplo de referência custa menos que inventar.
- **Cada funcionalidade fica num lugar com dono:** uma busca pelo nome do negócio acha a cadeia inteira.
- **Um único escritor por valor durável:** cada dado gravado tem um só dono que escreve; os outros leem ou pedem a ele.
- **Trabalho novo adiciona arquivos** em vez de mais um ramo (`if`, `switch`, entrada num registro central) numa raiz compartilhada.
- **Dependência proibida falha por máquina:** lint, tipos ou teste, não só revisão. Comentário de revisão que se repete vira verificação.
- **Exceção é explícita:** declarada com motivo e revisada como mudança de arquitetura.
