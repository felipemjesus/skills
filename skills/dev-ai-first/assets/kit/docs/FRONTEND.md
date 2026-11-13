# Frontend

> Leia antes de criar ou alterar telas.

| Item | No projeto |
|---|---|
| Framework | {{AGENTE: FRAMEWORK_FRONTEND}} |
| Raiz | `{{AGENTE: RAIZ_DO_FRONTEND}}` |
<!-- se: frontend-spa -->
| Estado de servidor | {{AGENTE: BIBLIOTECA_DE_ESTADO_DE_SERVIDOR}} |
| Tipos da API | `{{AGENTE: CMD_GERAR_TIPOS}}`, a partir de {{AGENTE: FORMATO_DO_CONTRATO}} |
<!-- fim: frontend-spa -->
<!-- se: frontend-servidor -->
| Templates | {{AGENTE: MOTOR_DE_TEMPLATES ou ponte (Inertia, Livewire)}} |
| JavaScript e assets | {{AGENTE: BIBLIOTECA_JS_PROGRESSIVA}}; build: {{AGENTE: FERRAMENTA_DE_ASSETS}} |
<!-- fim: frontend-servidor -->
| Formulário e schema | {{AGENTE: BIBLIOTECA_DE_FORMULARIO}} + {{AGENTE: BIBLIOTECA_DE_SCHEMA}} |
| Testes | componente: {{AGENTE: FERRAMENTA_DE_TESTE_DE_COMPONENTE}}; e2e: {{AGENTE: FERRAMENTA_E2E}}; acessibilidade: {{AGENTE: FERRAMENTA_DE_ACESSIBILIDADE}} |
| Fronteiras | `{{AGENTE: CMD_ARCH_CHECK_FRONTEND ou "ainda não existe"}}` |

## Princípios

Valem com qualquer estrutura de pastas.

- **O backend é dono da regra de negócio.** Filtrar, ordenar, paginar e contar com regra de negócio ("pedidos atrasados") é do backend; a tela apresenta.
- **A tela não duplica validação de negócio.** Ela valida só formato (obrigatório, tamanho, máscara) para dar retorno rápido; a regra é validada no backend e o erro dele aparece na tela.
- **Botões a partir das ações permitidas** que o backend devolve, com o motivo quando bloqueada. A tela nunca recria a máquina de estados.
<!-- se: api -->
  Formato: [API_GUIDELINES.md](API_GUIDELINES.md#princípios).
<!-- fim: api -->
- **Papéis separados:** um componente apresenta; um lugar só faz chamada de rede; a página compõe, sem regra. Lógica que não depende do framework de UI (fluxo de várias etapas, formatação) fica em classe testada sem renderizar ([orientação a objetos](../CODING_GUIDELINES.md#orientação-a-objetos)).
- **Framework first:** componente, formulário, rota e acessibilidade com o recurso do framework ou da biblioteca já adotada, nada artesanal.
- **Nomes:** pt-BR com o tipo técnico em inglês no fim (`CriarVendaForm`, `VendaStatusBadge`); o verbo é o do caso de uso do backend (`cancelar`, `useCancelarVenda`), não `store` nem `changeStatus`.
- **Erro do backend nunca é engolido:** aparece onde o usuário agiu (campo, formulário ou aviso geral) com a mensagem do backend.
- **Funcionalidade verificável:** cada tela nova ou alterada tem a linha dela em [VERIFICACAO.md](VERIFICACAO.md), com o caminho até ela e o seletor estável.

## Estrutura

<!-- se: estrutura-kit -->
Estrutura proposta: **o frontend espelha o backend.** Módulos e fatias têm o mesmo nome dos dois lados; "cancelar venda" cria `features/cancelar-venda/` nos dois, e nada fora delas além do necessário.

```
app/                          # rotas, providers, layout raiz
modules/vendas/               # mesmo nome do módulo do backend
  features/criar-venda/       # criar-venda-form, use-criar-venda, criar-venda.schema, *.test
  components/                 # usados por 2+ fatias do módulo
  pages/                      # compõem fatias; sem lógica
  api/vendas.api              # chamadas HTTP do módulo
  model/                      # venda.types, venda-status.enum, <caso>.model
  index                       # API pública do módulo
shared/ui/  shared/api/http-client  shared/api/generated/ (NÃO EDITAR)  shared/lib/
```

| Pasta | Não pode |
|---|---|
| `features/<caso>/` | importar outra fatia; o que duas usam sobe para `components/` ou `model/` |
| `components/` | chamar a API diretamente |
| `pages/` | lógica, chamada de API, estado além do da rota |
| `api/` | estado de UI |
| `model/` | regra de negócio |
| outro módulo | importar algo além do `index` |
| `shared/` | importar `modules/` |

Com telas renderizadas no servidor, a fatia do backend guarda o template e o JavaScript dela; `api/` só existe para chamadas fora do ciclo da página. Pasta só nasce com o primeiro arquivo. Arquivo em kebab-case: `criar-venda-form`, `use-criar-venda`, `criar-venda.schema`, `vendas.api`, `venda.types`, `criar-venda.spec` (e2e).
<!-- fim: estrutura-kit -->
<!-- se: estrutura-projeto -->
{{AGENTE: árvore real da raiz do frontend em até 12 linhas; 1 arquivo de exemplo por tipo (página ou template, componente, estado, chamada de rede, tipos); padrão de nome de arquivo; o que cada pasta não pode importar, se houver regra. Código novo imita o vizinho mais próximo}}
<!-- fim: estrutura-projeto -->

<!-- se: frontend-spa -->
## SPA

- **Componentes:** apresentam e emitem eventos; estado e chamadas ficam em hook/composable, que usa a camada de API.
- **Estado de servidor** na biblioteca de cache ({{AGENTE: BIBLIOTECA_DE_ESTADO_DE_SERVIDOR}}), nunca copiado para estado global. Chaves por módulo (`['vendas', 'lista', filtros]`); uma mutação invalida só as do próprio módulo.
- **Estado global de cliente** só se 2+ módulos precisam e não é dado do servidor. Estado de formulário fica no formulário; de UI (aberto, aba) no componente.
- **Camada de API:** só ela faz rede; o cliente HTTP converte a resposta de erro num erro tipado.
- **Tipos gerados** do contrato, nunca escritos à mão; contrato mudou, regenere no mesmo PR. Sem geração, tipos escritos com teste de contrato.
- **Roteamento no cliente:** filtros, página e ordenação na URL, para recarregar e compartilhar a tela; rota protegida redireciona, mas a barreira é o backend.
- **Testes:** mock de rede no nível HTTP, não da camada de API, para exercitar o cliente real e o mapeamento de erros.
<!-- fim: frontend-spa -->

<!-- se: frontend-servidor -->
## Telas renderizadas no servidor

- **Templates** recebem dados prontos do controller (ou props, com Inertia ou Livewire); sem consulta, regra nem cálculo de negócio no template.
- **JavaScript progressivo:** a página funciona sem ele no fluxo principal; o script só melhora (máscara, autocomplete, confirmação) e não guarda estado de negócio.
- **Formulários validados no servidor:** o erro volta com a página re-renderizada, a mensagem junto do campo e os valores digitados preservados; proteção CSRF do framework em todo formulário.
- **Rotas são do backend;** chamada assíncrona (autocomplete) usa um endpoint como qualquer outro, com autorização.
- **Assets** pelo pipeline do framework ({{AGENTE: FERRAMENTA_DE_ASSETS}}), com hash no nome; nada copiado à mão para a pasta pública.
<!-- fim: frontend-servidor -->

<!-- se: fullstack -->
## Contrato com o backend

Backend e frontend estão no mesmo repositório: uma mudança de contrato altera os dois lados no mesmo PR.

- **Dono da regra:** o backend. A tela mostra o que ele devolve (dados, ações permitidas, violações) e não recalcula.
- **Tipos e erros compartilhados:** gerados da especificação ou do código do backend ({{AGENTE: COMO_O_FRONTEND_OBTEM_OS_TIPOS}}), nunca duplicados à mão.
- **Erros** no formato de [CODING_GUIDELINES.md](../CODING_GUIDELINES.md#4-erros). Na tela:

| Resposta | Na tela |
|---|---|
| 400 com `errors` | mensagem junto do campo |
| 422 com `violacoes` | todas as violações no topo do formulário, ou junto do campo se a violação tiver `campo` |
| 409 | `detail` do backend e atualização das ações permitidas do registro |
| 401 / 403 | login / acesso negado, sem esconder o erro |
| 5xx / rede | aviso genérico com "tentar de novo" |

- **Teste do contrato:** um teste de tela com a resposta de erro real do backend (ex.: 422 com a regra `totalIgualSomaItens`) prova que a mensagem aparece junto do campo.
<!-- fim: fullstack -->

## Testes

- Busque por papel e nome acessível (`botão "Criar venda"`), não por classe CSS ou id de teste.
- Componente: o que o usuário vê e o efeito de clicar e digitar. E2E: cenário de ponta a ponta com backend real.
- {{AGENTE: FERRAMENTA_DE_ACESSIBILIDADE}} roda nos e2e; falha de acessibilidade quebra o CI.
- Textos em pt-BR; i18n: {{AGENTE: BIBLIOTECA_DE_I18N ou "não há"}} (com i18n, nenhum texto fixo no componente). Datas, moeda e números formatados com a localidade, num lugar só.
<!-- se: bdd -->
- Cada cenário `.feature` com tela ([TESTING.md](../TESTING.md#3-bdd)) vira um teste e2e.
<!-- fim: bdd -->
