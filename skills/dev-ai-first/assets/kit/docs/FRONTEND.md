# Frontend

> Como o frontend é organizado, nomeado e testado. Leia antes de criar ou alterar telas. Framework: {{AGENTE: FRAMEWORK_FRONTEND}} (ex.: React ou Vue). Estado de servidor: {{AGENTE: BIBLIOTECA_DE_ESTADO_DE_SERVIDOR}}. Validação de formulário: {{AGENTE: BIBLIOTECA_DE_SCHEMA}}. Testes de componente: {{AGENTE: FERRAMENTA_DE_TESTE_DE_COMPONENTE}}. E2E: {{AGENTE: FERRAMENTA_E2E}}.

## 1. Princípios

- **O frontend espelha o backend.** Os módulos e as fatias têm os mesmos nomes dos dois lados: `modules/vendas/features/criar-venda/` existe no backend e no frontend. Quem acha uma fatia num lado acha a outra sem procurar.
- **Uma tarefa corresponde a uma fatia nos dois lados.** Adicionar "cancelar venda" cria `features/cancelar-venda/` no backend e no frontend, e nada fora delas além do necessário.
- **O backend é dono da regra de negócio.** O frontend valida formato para dar resposta rápida ao usuário (campo obrigatório, e-mail válido), mas a decisão final é do backend. Regra duplicada no frontend vira divergência. Filtrar, buscar, ordenar, paginar e contar com regra de negócio (ex.: "pedidos atrasados", "total em aberto") é do backend; o componente só apresenta o resultado.
- **Contrato gerado, não escrito à mão.** Tipos da API vêm do contrato do backend ([seção 6](#6-contrato-com-o-backend)).
- **Páginas compõem; fatias fazem.** Uma página junta fatias e componentes, sem lógica própria.
- **Framework first.** Use o que {{AGENTE: FRAMEWORK_FRONTEND}} e as bibliotecas adotadas oferecem (roteamento, estado de servidor, formulários, cliente HTTP, streaming), do jeito que a documentação mostra. Wrapper ou utilitário próprio só quando não houver recurso, com justificativa ([ADR-0005](adr/0005-framework-first.md)).
- **Funções onde o framework de UI exige.** Componentes e hooks/composables são funções quando o framework de UI os define assim: é a borda do framework ([CODING_GUIDELINES.md](../CODING_GUIDELINES.md#orientação-a-objetos)). Lógica que não depende do framework (o `<caso>.model`, formatação) fica em classes, como no backend.
- **Responsabilidades separadas também no frontend.** Componente apresenta; hook/composable gerencia estado e chama `api/`; só `api/` faz chamadas de rede; página compõe.
- **Os mesmos verbos do backend.** A função de `api/`, o hook e o botão usam o verbo do caso de uso (`cancelar`, `useCancelarVenda`), não `store`/`changeStatus`: quem lê um chamado acha o código dos dois lados.
- **Botões a partir das ações permitidas.** O que o usuário pode fazer num registro vem das ações permitidas devolvidas pelo backend, com o motivo quando bloqueada ([API_GUIDELINES.md](API_GUIDELINES.md#princípios)). A tela nunca recria a máquina de estados.
- **Lógica de tela com fluxo próprio pode ficar num módulo simples.** O padrão é o hook/composable. Telas com fluxo próprio (assistente em etapas, progresso, mensagens por etapa) podem pôr essas regras num módulo simples (`<caso>.model`), testado sem renderizar, e o hook só o conecta ao framework.

## 2. Estrutura

Os caminhos abaixo são relativos à raiz do frontend, `{{AGENTE: RAIZ_DO_FRONTEND}}` (ex.: `frontend/src/` num monorepo, `src/` num repositório só de frontend, `resources/js/` com Inertia). Os testes e2e ficam em `tests/e2e/` na raiz do repositório. Extensões como marcador: `{{AGENTE: ext}}` para componentes (ex.: `.tsx`, `.vue`) e `{{AGENTE: ext-script}}` para módulos de código (ex.: `.ts`). Abaixo, sem extensão.

```
{{AGENTE: RAIZ_DO_FRONTEND}}/
├── app/                                  # inicialização: rotas, providers, layout raiz
│   ├── router
│   ├── providers
│   └── app-layout                            → AppLayout
├── modules/
│   └── vendas/                           # mesmo nome do módulo do backend
│       ├── features/                     # mesmas fatias do backend
│       │   ├── criar-venda/
│       │   │   ├── criar-venda-form          → CriarVendaForm
│       │   │   ├── criar-venda-form.test
│       │   │   ├── use-criar-venda           → useCriarVenda (envio + estados)
│       │   │   └── criar-venda.schema        → criarVendaSchema
│       │   ├── cancelar-venda/
│       │   │   ├── cancelar-venda-dialog     → CancelarVendaDialog
│       │   │   └── use-cancelar-venda        → useCancelarVenda
│       │   └── listar-vendas/
│       │       ├── vendas-table              → VendasTable
│       │       ├── filtro-vendas-bar         → FiltroVendasBar
│       │       └── use-listar-vendas         → useListarVendas
│       ├── components/                   # usados por 2+ fatias do módulo
│       │   ├── venda-card                    → VendaCard
│       │   └── venda-status-badge            → VendaStatusBadge
│       ├── pages/                        # compõem fatias; sem lógica
│       │   ├── vendas-page                   → VendasPage
│       │   └── venda-detalhe-page            → VendaDetalhePage
│       ├── api/
│       │   └── vendas.api                    → vendasApi (chamadas HTTP do módulo)
│       ├── model/
│       │   ├── venda.types                   → Venda
│       │   └── venda-status.enum             → VendaStatusEnum
│       ├── vendas.routes                 # rotas do módulo (se o roteamento for do frontend)
│       └── index                         # API pública do módulo
├── shared/
│   ├── ui/                               # design system: button, modal, data-table
│   ├── api/
│   │   ├── http-client                   # configuração da biblioteca HTTP adotada; trata Problem Details (RFC 9457)
│   │   └── generated/                    # tipos gerados do contrato do backend: NÃO EDITAR
│   ├── hooks/                            # hooks/composables genéricos, sem regra de módulo
│   └── lib/                              # datas, moeda, formatação
tests/
└── e2e/
    └── vendas/
        └── criar-venda.spec              # cenário de ponta a ponta ({{AGENTE: FERRAMENTA_E2E}})
```

| Pasta | Contém | Não pode |
|---|---|---|
| `app/` | rotas, providers (cliente de estado de servidor, tema, i18n), layout raiz | regra de módulo |
| `modules/<m>/features/<caso>/` | componentes, hook/composable e schema de um caso de uso | importar outra fatia |
| `modules/<m>/components/` | componentes usados por 2+ fatias do módulo | chamar a API diretamente |
| `modules/<m>/pages/` | composição de fatias e componentes para uma rota | lógica, chamadas de API, estado próprio além do da rota |
| `modules/<m>/api/` | funções que chamam o backend, tipadas com os tipos gerados | estado de UI |
| `modules/<m>/model/` | tipos e enums do módulo usados por várias fatias | regra de negócio |
| `modules/<m>/index` | o que outros módulos podem usar | expor o interior do módulo |
| `shared/` | design system, cliente HTTP, utilitários | importar `modules/` |

Se a renderização é do servidor (ex.: Inertia, Livewire ou templates), os dados da página chegam como props do controller da fatia. Nesse caso `api/` só existe para chamadas fora do ciclo da página (busca, autocomplete) e `vendas.routes` não existe, porque as rotas são do backend.

Crie uma pasta só quando houver o primeiro arquivo dela.

## 3. Convenção de nomes

Nomes em português do Brasil com o tipo em inglês no fim. Componentes levam o tipo após hífen; módulos utilitários, após ponto. Estilo do arquivo: kebab-case.

| Tipo | Arquivo | Nome no código |
|---|---|---|
| Página | `vendas-page.{{AGENTE: ext}}` | `VendasPage` |
| Layout | `app-layout.{{AGENTE: ext}}` | `AppLayout` |
| Formulário | `criar-venda-form.{{AGENTE: ext}}` | `CriarVendaForm` |
| Diálogo | `cancelar-venda-dialog.{{AGENTE: ext}}` | `CancelarVendaDialog` |
| Tabela / lista | `vendas-table.{{AGENTE: ext}}` | `VendasTable` |
| Card / badge / bar | `venda-card.{{AGENTE: ext}}`, `venda-status-badge.{{AGENTE: ext}}`, `filtro-vendas-bar.{{AGENTE: ext}}` | `VendaCard`, `VendaStatusBadge`, `FiltroVendasBar` |
| Hook / composable | `use-criar-venda.{{AGENTE: ext-script}}` | `useCriarVenda` |
| Schema | `criar-venda.schema.{{AGENTE: ext-script}}` | `criarVendaSchema` |
| API | `vendas.api.{{AGENTE: ext-script}}` | `vendasApi` |
| Tipos / enum | `venda.types.{{AGENTE: ext-script}}`, `venda-status.enum.{{AGENTE: ext-script}}` | `Venda`, `VendaStatusEnum` |
| Store (se houver) | `vendas.store.{{AGENTE: ext-script}}` | `useVendasStore` |
| Teste unitário / de componente | `criar-venda-form.test.{{AGENTE: ext}}` | — |
| E2E | `criar-venda.spec.{{AGENTE: ext-script}}` | — |

PascalCase para componentes, `useX` para hooks/composables, camelCase para o resto. O lint verifica o kebab-case dos arquivos ({{AGENTE: REGRA_DE_LINT_DE_NOME_DE_ARQUIVO}}, ex.: `unicorn/filename-case` no ESLint).

## 4. Regras de dependência

1. Uma fatia não importa outra fatia. O que duas fatias usam sobe para `components/` ou `model/` do módulo.
2. `pages/` compõem fatias e componentes, sem lógica.
3. Um módulo só importa outro pelo `index`.
4. `shared/` não importa `modules/`.
5. Só `api/` (ou o cliente HTTP) faz chamadas de rede; componentes usam hooks/composables.
6. Tipos da API são gerados do contrato do backend; nunca escritos à mão quando houver geração.
7. Regra de negócio é do backend; o frontend valida formato para UX.

Verificação: `{{AGENTE: CMD_ARCH_CHECK_FRONTEND}}` no CI, com {{AGENTE: FERRAMENTA_DE_FRONTEIRAS}} (ex.: dependency-cruiser ou eslint-plugin-boundaries no ecossistema JavaScript). As regras, em forma de pseudoconfiguração:

```
proibido  modules/(*)/features/(*)/  →  modules/$1/features/(outra que não $2)/
proibido  modules/(*)/               →  modules/(outro que não $1)/ exceto index
proibido  shared/                    →  modules/
proibido  modules/*/(features|components|pages)/  →  biblioteca HTTP (só api/ e shared/api/)
proibido  arquivo editado à mão em shared/api/generated/ (checado por diff após regenerar)
```

## 5. Dados e estado

| Tipo de estado | Onde fica | Ferramenta |
|---|---|---|
| Estado de servidor (dados do backend) | hooks da fatia, sobre `api/` | {{AGENTE: BIBLIOTECA_DE_ESTADO_DE_SERVIDOR}} (ex.: TanStack Query) ou props da página quando o backend renderiza |
| Estado de formulário | dentro da fatia | {{AGENTE: BIBLIOTECA_DE_FORMULARIO}} + `*.schema` |
| Estado de UI local (aberto/fechado, aba ativa) | no componente | estado do próprio framework |
| Fluxo de tela com várias etapas | `<caso>.model` (módulo simples) conectado por um hook/composable | linguagem pura; testado sem renderizar |
| Estado global de cliente | `*.store`, só quando 2+ módulos precisam e não é dado do servidor | {{AGENTE: BIBLIOTECA_DE_ESTADO_GLOBAL}} |
| Estado na URL (filtros, página, ordenação) | parâmetros da rota | roteador |

- Não copie dado do servidor para estado global; o cache do estado de servidor é a fonte.
- Chaves de cache por módulo e por fatia: `['vendas', 'lista', filtros]`, `['vendas', 'detalhe', id]`. Uma mutação invalida só as chaves do próprio módulo.
- Filtros e paginação ficam na URL, para que a tela possa ser recarregada e compartilhada.

Exemplo (pseudocódigo; no React com TanStack Query, `useMutation`; em Vue com Inertia, `useForm`):

```
// features/criar-venda/use-criar-venda
function useCriarVenda():
  mutation = useMutation(
    enviar: dados => vendasApi.criar(dados),
    aoTerSucesso: () => invalidar(['vendas', 'lista']),
  )
  return { criar: mutation.enviar, enviando: mutation.pendente, erro: mutation.erro }

// features/criar-venda/criar-venda-form
component CriarVendaForm:
  form = useForm(schema: criarVendaSchema)
  { criar, enviando, erro } = useCriarVenda()
  render:
    <form aoEnviar={form.validarEntao(criar)}>
      <label for="cliente">Cliente</label> <input id="cliente" {...form.campo('clienteId')} />
      <MensagemErro campo="clienteId" erros={form.erros ∪ errosCampo(erro)} />
      <button type="submit" disabled={enviando}>Criar venda</button>
    </form>
```

## 6. Contrato com o backend

- **Tipos gerados.** Os tipos de request e response vêm do contrato publicado pelo backend ({{AGENTE: FORMATO_DO_CONTRATO}}, ex.: OpenAPI) com `{{AGENTE: CMD_GERAR_TIPOS}}`, e ficam em `shared/api/generated/`. Ninguém edita essa pasta. Mudou o contrato? Regenere no mesmo PR. Quando o backend renderiza as páginas e não há geração, escreva os tipos em `model/*.types` e cubra com teste de contrato.
- **Erros.** O backend responde erros no formato Problem Details (RFC 9457), conforme [API_GUIDELINES.md](API_GUIDELINES.md#erros). O `http-client` converte a resposta em um erro tipado:

| Resposta | No frontend |
|---|---|
| 400 com `errors` (validação de entrada) | mensagem junto do campo correspondente no formulário |
| 422 com `violacoes` (regras de negócio) | lista de todas as violações no topo do formulário (ou junto do campo, quando a violação tiver `campo`) |
| 409 (estado não permite) | mensagem com o `detail` do backend e atualização das `acoesPermitidas` do registro |
| 401 | redirecionar para login |
| 403 | mensagem de acesso negado; não esconder o erro |
| 5xx / rede | toast genérico com opção de tentar de novo; detalhe só no log |

## 7. Testes

| Nível | O que cobre | Ferramenta | Onde |
|---|---|---|---|
| Componente | comportamento visível ao usuário: o que aparece, o que acontece ao clicar e digitar | {{AGENTE: FERRAMENTA_DE_TESTE_DE_COMPONENTE}} (ex.: Testing Library) | junto da fatia (`*.test`) |
| Hook / composable | estados de carregamento, erro e sucesso | mesma ferramenta | junto da fatia |
| E2E | cenários BDD de ponta a ponta, com backend real | {{AGENTE: FERRAMENTA_E2E}} (ex.: Playwright) | `tests/e2e/<modulo>/` |

- Busque elementos como o usuário os percebe: por papel e nome acessível (`botão "Criar venda"`), não por classe CSS ou id de teste. Isso também testa acessibilidade.
- Mock de rede no nível HTTP, não do módulo `api/` ({{AGENTE: FERRAMENTA_DE_MOCK_DE_REDE}}, ex.: MSW), para que o teste exercite o cliente real e o mapeamento de erros.
- Cada cenário `.feature` de [TESTING.md](../TESTING.md#3-bdd) que tem tela vira um teste e2e.

Exemplo de teste de componente (pseudocódigo):

```
teste "mostra o erro do backend junto do campo cliente":
  rede.responder(POST /vendas, 422, problemDetails(violacoes: [{ regra: "clienteSemBloqueio", campo: "clienteId", mensagem: "cliente bloqueado" }]))
  renderizar(<CriarVendaForm />)
  digitar(campo com rótulo "Cliente", "42")
  clicar(botão "Criar venda")
  esperar(texto "cliente bloqueado" visível)
```

Exemplo de e2e (pseudocódigo):

```
// tests/e2e/vendas/criar-venda.spec
teste "analista cria uma venda":
  entrarComo(analista)
  abrir("/vendas")
  clicar(botão "Nova venda")
  preencher(rótulo "Cliente", "ACME")
  clicar(botão "Criar venda")
  esperar(linha da tabela com "ACME" e status "Pendente")
  verificarAcessibilidade(página)        // ex.: axe
```

## 8. Acessibilidade e textos

- HTML semântico: `button` para ações, `a` para navegação, `label` ligado a cada campo, títulos em ordem.
- Toda funcionalidade funciona só com teclado; o foco é visível e vai para o lugar certo ao abrir e fechar diálogos.
- Contraste mínimo WCAG AA; informação nunca só por cor (o `VendaStatusBadge` tem texto, não só cor).
- Erros de formulário anunciados a leitores de tela e ligados ao campo.
- Checagem automática com {{AGENTE: FERRAMENTA_DE_ACESSIBILIDADE}} (ex.: axe) nos testes e2e; falha de acessibilidade quebra o CI.
- Textos em pt-BR. Se houver i18n ({{AGENTE: BIBLIOTECA_DE_I18N}}), os textos ficam centralizados por módulo e nenhum texto visível fica fixo no componente. Datas, moeda e números formatados por `shared/lib` com a localidade.

## 9. Receitas

### Adicionar uma fatia de frontend
1. Confirme que a fatia existe (ou vai existir) no backend com o mesmo nome em `features/`.
2. Regenere os tipos da API (`{{AGENTE: CMD_GERAR_TIPOS}}`) se o contrato mudou.
3. Crie `modules/<m>/features/<caso>/` com o componente (`<caso>-form`, `-dialog`, `-table`...), o hook `use-<caso>` e, se houver formulário, `<caso>.schema`.
4. Adicione a função de chamada em `api/<m>.api`, se ainda não houver.
5. Escreva o teste de componente antes ou junto do componente.
6. Use a fatia em uma página de `pages/`.

### Adicionar uma página
1. Crie `modules/<m>/pages/<nome>-page` compondo fatias e componentes, sem lógica.
2. Registre a rota em `<m>.routes` (ou, com renderização no servidor, no controller da fatia do backend).
3. Se a página corresponde a um cenário BDD, crie o e2e em `tests/e2e/<m>/`.

### Adicionar um componente compartilhado
1. Usado por 2+ fatias do mesmo módulo → `modules/<m>/components/`.
2. Sem conhecimento de negócio e útil em vários módulos → `shared/ui/` (design system).
3. Usado por outro módulo e com conhecimento de negócio → exporte pelo `index` do módulo dono.
