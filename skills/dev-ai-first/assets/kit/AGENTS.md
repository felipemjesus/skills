# AGENTS.md

> Leia inteiro antes de alterar algo.

## Sobre o projeto

**{{AGENTE: NOME_DO_PROJETO}}**: {{USUARIO: DESCRICAO_EM_UMA_FRASE}}. Stack: {{AGENTE: LINGUAGEM · FRAMEWORK · BANCO}}.
<!-- se: estrutura-kit -->
Estrutura: fatias por caso de uso em `features/`.
<!-- fim: estrutura-kit -->
<!-- se: estrutura-projeto -->
Estrutura: {{AGENTE: organização real em 1 linha}}.
<!-- fim: estrutura-projeto -->

## Comandos

- Instalar `{{AGENTE: CMD_INSTALL}}` · subir `{{AGENTE: CMD_DEV}}` · lint `{{AGENTE: CMD_LINT}}` · testes `{{AGENTE: CMD_TEST_UNIT}}` · um arquivo `{{AGENTE: CMD_TEST_FILE}}`
<!-- se: backend -->
- Integração `{{AGENTE: CMD_TEST_INTEGRATION}}`
<!-- fim: backend -->
<!-- se: frontend -->
- Frontend `{{AGENTE: CMD_FRONTEND_DEV}}` · e2e `{{AGENTE: CMD_FRONTEND_E2E}}`
<!-- fim: frontend -->
<!-- se: verificacao-arquitetura -->
- Arquitetura `{{AGENTE: CMD_ARCH_CHECK}}`
<!-- fim: verificacao-arquitetura -->
<!-- se: bdd -->
- Aceitação `{{AGENTE: CMD_TEST_ACCEPTANCE}}`
<!-- fim: bdd -->
- **Verificação completa** `{{AGENTE: CMD_CHECK}}`

## Mapa de documentos

- [CODEBASE_MAP](CODEBASE_MAP.md) · [DOMAIN](docs/DOMAIN.md) · [ARCHITECTURE](ARCHITECTURE.md) · [CODING_GUIDELINES](CODING_GUIDELINES.md) · [TESTING](TESTING.md) · [VERIFICACAO](docs/VERIFICACAO.md) · [SECURITY](SECURITY.md) · [CONTRIBUTING](CONTRIBUTING.md) · [ADRs](docs/adr/)
<!-- se: frontend -->
- [FRONTEND](docs/FRONTEND.md)
<!-- fim: frontend -->
<!-- se: api -->
- [API_GUIDELINES](docs/API_GUIDELINES.md)
<!-- fim: api -->
<!-- se: eventos -->
- [EVENTS](docs/EVENTS.md)
<!-- fim: eventos -->
<!-- se: observabilidade -->
- [OBSERVABILITY](docs/OBSERVABILITY.md)
<!-- fim: observabilidade -->

## Fluxo de trabalho

Entender → planejar (cada frase do pedido vira critério) → teste falhando → mínimo → verificar → documentar.

## Checklist de design

Mudança de comportamento responde [docs/CHECKLIST_DESIGN.md](docs/CHECKLIST_DESIGN.md) no plano.

## Ordem de verdade

Em conflito: (1) configuração e verificações; (2) ADR aceita; (3) documentos, o mais específico antes. O de baixo é o defeito: corrija e relate. Nunca mude a configuração para seguir um documento.

**Princípio × padrão:** código novo segue o padrão do projeto, sem misturar formas no módulo; dentro dele valem os princípios. Se o padrão contraria um princípio, siga-o, registre em [ARCHITECTURE §11](ARCHITECTURE.md#11-riscos-e-débitos-conhecidos) e pergunte se migra.

## Limites

### Sempre
- Recurso do framework na versão instalada, nunca API obsoleta.
- Regra de negócio no domínio; cada papel no seu [lugar](ARCHITECTURE.md#41-responsabilidades).
<!-- se: backend -->
- ORM só na persistência; transação no caso de uso.
<!-- fim: backend -->
- Decisão do dev vai ao PR na hora.

### Perguntar antes
Perguntar é não fazer: dê opções e recomendação e siga o resto. A demanda autoriza o que exige. Salvo [Decisões registradas](#decisões-registradas):
- dependência nova ou atualizada, infraestrutura, CI, deploy;
- migração destrutiva, contrato incompatível, o que a demanda não exige;
- mudar convenção documentada; solução própria ou interface sem motivo.

### Nunca
- Commitar segredos ou dados reais; comando destrutivo sem pedido.
- Enfraquecer testes, lint, tipos ou arquitetura, nem regravar baseline.
- Acessar o interior de outro módulo; inventar API; editar código gerado à mão.

## Definição de pronto

Verificação completa verde; teste que falhou citado no PR; verificado rodando o sistema como o usuário usa, conforme [docs/VERIFICACAO.md](docs/VERIFICACAO.md), quando aplicável. Diff conferido com o plano; documentação atualizada; cada "perguntar antes" cita a autorização literal.

## Decisões registradas

Fora daqui, cada demanda pergunta de novo.
- {{USUARIO: AAAA-MM-DD: decisão (alcance)}}

## Mantendo a documentação

Pasta → CODEBASE_MAP; fronteira → ARCHITECTURE + ADR; termo, regra → DOMAIN; convenção → CODING_GUIDELINES; funcionalidade → VERIFICACAO; o resto → o documento do tema.
