# Plano de Testes — Sistema de Controle de EPI

**Versão:** 1.0  
**Autores:** Jonathan Eichenberger e Felipe fernandes Ribeiro
**Data:** 2025-10-06  
**Cobertura mínima esperada:** **90%**

---

## Índice

1. [Identificação do Projeto](#1-identificação-do-projeto)  
2. [Objetivo do Plano de Testes](#2-objetivo-do-plano-de-testes)  
3. [Escopo dos Testes](#3-escopo-dos-testes)  
4. [Tipos de Testes](#4-tipos-de-testes)  
5. [Estratégia de Testes](#5-estratégia-de-testes)  
6. [Critérios de Entrada e Saída](#6-critérios-de-entrada-e-saída)  
7. [Ambiente de Teste](#7-ambiente-de-teste)  
8. [Casos de Teste (Resumo)](#8-casos-de-teste-resumo)  
9. [Métricas de Qualidade](#9-métricas-de-qualidade)  
10. [Riscos e Mitigações](#10-riscos-e-mitigações)  
11. [Papéis e Responsabilidades](#11-papéis-e-responsabilidades)  
12. [Critérios de Aceitação](#12-critérios-de-aceitação)  
13. [Execução e Relatórios](#13-execução-e-relatórios)  
14. [Conclusão](#14-conclusão)  
15. [Anexos Sugeridos](#15-anexos-sugeridos)

---

## 1. Identificação do Projeto

**Nome:** Sistema de Controle de EPI  
**Descrição:** Sistema web em Django para gestão de Equipamentos de Proteção Individual (EPIs), controlando entregas, devoluções e solicitações por colaborador.  

**Tecnologias Utilizadas:**  
- Backend: Python 3.12 + Django  
- Banco de Dados: MySQL (via Docker)  
- Testes: Pytest + Django Test Client  
- CI/CD: GitHub Actions + Codecov  
- Frontend: Bootstrap 5 + CSS 

[🔝 Voltar ao Índice](#índice)

---

## 2. Objetivo do Plano de Testes

Garantir a **qualidade funcional, estrutural e regressiva** do Sistema de Controle de EPI, assegurando que:

- As funcionalidades principais funcionem conforme os requisitos (RF e RN).  
- As permissões e fluxos de autenticação estejam corretos.  
- A integração entre módulos (`colaboradores`, `epis`, `entregas`, `relatorios`) opere sem falhas.  
- As alterações de código não reduzam a cobertura mínima de **90%**.  
- As respostas e templates retornem conforme esperado.

[🔝 Voltar ao Índice](#índice)

---

## 3. Escopo dos Testes

### ✅ Serão testados
- **Modelos:** regras de negócio e constraints de dados.  
- **Formulários:** validações e campos obrigatórios.  
- **Views e URLs:** redirecionamentos, permissões, status codes e mensagens.  
- **Templates:** renderização e elementos visuais principais.  
- **Serviços:** movimentação de estoque e lógica de domínio.  
- **Integração entre apps:** `app_entregas`, `app_colaboradores`, `app_epis`, `app_relatorios`.

### 🚫 Fora de escopo
- Testes de performance e carga.  
- Testes de usabilidade e acessibilidade.  
- Testes de compatibilidade cross-browser.

[🔝 Voltar ao Índice](#índice)

---

## 4. Tipos de Testes

| Tipo | Objetivo | Ferramenta / Técnica |
|------|-----------|----------------------|
| **Unitário** | Validar métodos e funções isoladas (models, forms, utils). | Pytest |
| **Integração** | Validar comunicação entre views, URLs, templates e DB. | Django Test Client |
| **Funcional (Sistema)** | Validar fluxos completos (CRUDs, login, entregas). | Selenium IDE + Pytest + Client|
| **Regressão** | Reexecutar suíte completa após cada PR/Merge. | GitHub Actions |
| **Cobertura de Código** | Monitorar percentual mínimo de 90%. | Coverage.py + Codecov |

[🔝 Voltar ao Índice](#índice)

---

## 5. Estratégia de Testes

- Todos os testes serão escritos com **Pytest** e organizados na pasta `/tests`.  
- Cada app (`app_colaboradores`, `app_epis`, etc.) mantém seus próprios arquivos de teste.  
- Convenções:
  - Nomes iniciam com `test_`.
  - Decorador `@pytest.mark.django_db` quando houver interação com o banco.
  - Nenhum teste deve depender de outro (independência total).  
- O ambiente de teste usará **SQLite** (modo in-memory) para desempenho.  
- Execução automatizada via **GitHub Actions** em cada *push* na `main`.

[🔝 Voltar ao Índice](#índice)

---

## 6. Critérios de Entrada e Saída

### Entrada
- Migrações aplicadas sem erros.  
- Ambiente `.env.test` ou variáveis Docker configuradas.  
- Suíte executável via `pytest`.

### Saída
- Todos os testes passam (`exit code 0`).  
- Cobertura ≥ **90%**.  
- Sem falhas críticas ou regressões em funcionalidades principais.

[🔝 Voltar ao Índice](#índice)

---

## 7. Ambiente de Teste

| Item | Configuração |
|------|---------------|
| **Sistema Operacional** | Ubuntu 22.04 (Docker container) |
| **Banco de Dados** | SQLite para testes, MySQL em produção |
| **Ferramentas** | Pytest, Coverage.py, Codecov |
| **Execução local** | `pytest --cov=. --cov-report=term-missing --cov-report=html` |
| **CI/CD** | GitHub Actions (`.github/workflows/tests.yml`) |

[🔝 Voltar ao Índice](#índice)

---

## 8. Casos de Teste (Resumo)

| ID | Caso de Teste | Tipo | App | Resultado Esperado |
|----|----------------|------|-----|--------------------|
| **CT01** | Listagem e filtros de colaboradores | Integração | app_colaboradores | Retorna lista filtrada corretamente conforme parâmetros e permissões |
| **CT02** | Criação, edição e exclusão (soft delete) de colaborador | Integração | app_colaboradores | Cria, atualiza e desativa colaborador com feedback de mensagens |
| **CT03** | Registro de novo colaborador via formulário público | Integração | app_colaboradores | Cria `User` e `Colaborador`, trata erros de banco e exibe mensagens adequadas |
| **CT04** | Permissões e autenticação em views de colaboradores | Integração | app_colaboradores | Bloqueia acesso sem login e sem permissões, permitindo acesso autorizado |
| **CT05** | Criação e edição de EPIs | Integração | app_epis | Cadastra e atualiza EPI, exibindo mensagens de sucesso |
| **CT06** | Exclusão de EPI protegido por chave estrangeira | Integração | app_epis | Exibe mensagem de erro e mantém o registro protegido |
| **CT07** | Validação de formulário de EPI | Unitário | app_epis | Cria categorias padrão e valida campos negativos com erros corretos |
| **CT08** | Movimentação de estoque por entrega | Integração | app_entregas | Ajusta estoque ao criar, editar e excluir entregas |
| **CT09** | Erro de estoque insuficiente em movimentação | Unitário / Integração leve | app_entregas | Lança `ValidationError` quando a quantidade excede o estoque |
| **CT10** | Formulário de entrega (datas e status) | Unitário | app_entregas | Exige datas válidas conforme status (emprestado, devolvido) |
| **CT11** | Fluxo completo de solicitações (criar → aprovar → atender → devolver → reprovar) | Integração | app_entregas | Mantém estados e estoques corretos com mensagens esperadas |
| **CT12** | Permissões e redirecionamentos em entregas | Integração | app_entregas | Exige login e permissões corretas nas views |
| **CT13** | Geração e filtragem de relatórios | Integração | app_relatorios | Agrega entregas, filtra por data e retorna contexto correto |
| **CT14** | Exportação de relatório em CSV | Integração | app_relatorios | Gera arquivo CSV formatado com dados filtrados e cabeçalho correto |
| **CT15** | Validação de período no formulário de relatórios | Unitário | app_relatorios | Impede seleção de data final anterior à inicial |
| **CT16** | Testes de rotas principais (URLs e redirects) | Unitário / Integração leve | config / app_core | URLs resolvem corretamente e redirects funcionam conforme esperado |
| **CT17** | Página inicial (home) disponível e renderizada | Integração | app_core | Retorna status 200 e renderiza cards e blocos principais do dashboard |
| **CT18** | Validação de constraints de modelo EPI | Unitário | app_epis | Impede criação de EPI com estoque ou estoque mínimo negativo |
| **CT19** | Testes de modelos (str e criação de usuário) | Unitário | models gerais | Retorna representação textual correta e cria usuário com PK válida |
| **CT20** | URLs gerais do sistema | Unitário | config / app_core | Confirma reverses válidos e resolução de rotas principais |
| **CT21** | Marcar entrega como **perdida** via POST mantém efeito no estoque | Integração | app_entregas | Atualiza status para **PERDIDO**, define `data_devolucao`, mantém o estoque do EPI inalterado e exibe mensagem de sucesso |
| **CT22** | Impedir “marcar perdido” para status inválidos | Integração | app_entregas | Para entregas em **FORNECIDO**/**DEVOLVIDO**, não altera o status e exibe **mensagem de aviso** |
| **CT23** | Rejeitar GET em “marcar perdido” | Integração | app_entregas | Apenas **POST** é aceito: requisições **GET** redirecionam sem efeitos colaterais no registro |
| **CT24** | Listagem filtra corretamente apenas colaboradores **ativos** (`ativo=1`) | Integração | app_colaboradores | Retorna status 200, exibe apenas registros com `ativo=True` e exclui os inativos da página |
| **CT25** | Listagem filtra corretamente apenas colaboradores **inativos** (`ativo=0`) | Integração | app_colaboradores | Retorna status 200, exibe somente colaboradores com `ativo=False` e oculta os ativos |
| **CT26** | Contexto da listagem contém parâmetros de busca e filtro (`q` e `ativo`) | Integração | app_colaboradores | Inclui no contexto os valores informados na querystring para manter filtros ativos na navegação |
| **CT27** | Página de exclusão (GET) renderiza corretamente o **template de confirmação** | Integração | app_colaboradores | Retorna status 200, renderiza o template de confirmação e inclui o objeto colaborador no contexto |
| **CT28** | Tentar excluir colaborador já **inativo** apenas informa sem alterar dados | Integração | app_colaboradores | Exibe mensagem informativa “já está desativado” e mantém o registro sem alterações no banco |
| **CT29** | Página de **registro** (GET) é exibida com formulário válido | Integração | app_colaboradores | Retorna status 200 e inclui `form` no contexto pronto para preenchimento |
| **CT30** | Envio de **registro inválido** permanece na página exibindo erros | Integração | app_colaboradores | Retorna status 200, mantém o contexto com `form` e mensagens de erro de validação |
| **CT31** | Usuário sem perfil mas com permissão de criar é redirecionado para **criação** | Integração | app_colaboradores | Redireciona para rota de criação (`app_colaboradores:criar`) e exibe mensagem informativa para criação do perfil |
| **CT32** | Usuário sem perfil e **sem permissão** é redirecionado à **home** com erro | Integração | app_colaboradores | Direciona para `app_core:home` e exibe mensagem de erro informando ausência de perfil de colaborador |
| **CT33** | Acesso ao perfil de **outro colaborador sem permissão** retorna **403** | Integração | app_colaboradores | Bloqueia acesso via `PermissionDenied`, retornando HTTP 403 Forbidden |
| **CT34** | Contexto do perfil contém dados do **colaborador logado** e form de foto | Integração | app_colaboradores | Renderiza página com chaves `colaborador` e `foto_form` no contexto |
| **CT35** | Ação **“remover foto”** sem imagem associada exibe mensagem informativa | Integração | app_colaboradores | Exibe mensagem “colaborador não possui foto” e não realiza alterações no modelo |
| **CT36** | Ação **“remover foto”** com imagem salva remove arquivo e confirma sucesso | Integração | app_colaboradores | Remove o arquivo da instância e exibe mensagem de sucesso “foto removida com sucesso” |
| **CT37** | POST inválido de upload de foto re-renderiza página mantendo contexto | Integração | app_colaboradores | Retorna status 200, renderiza `perfil.html` novamente e mantém `colaborador` e `foto_form` no contexto |
| **CT38** | Validação de formulário de entrega com campos obrigatórios | Unitário | app_entregas | Garante que o form exibe erros apropriados quando campos obrigatórios não são preenchidos |
| **CT39** | Validação de quantidade negativa em formulário de entrega | Unitário | app_entregas | Impede o envio de quantidade menor ou igual a zero e retorna erro de validação |
| **CT40** | Criação de entrega reduz o estoque do EPI conforme quantidade e status | Integração | app_entregas | Ao criar uma entrega com status **EMPRESTADO**, o estoque do EPI é reduzido corretamente |
| **CT41** | Atualização de entrega com mesmo EPI e status ajusta estoque conforme diferença de quantidade | Integração | app_entregas | Atualiza o estoque apenas pelo delta entre a quantidade antiga e a nova, mantendo a consistência |
| **CT42** | Atualização de entrega com troca de EPI reverte estoque do antigo e aplica no novo | Unitário | app_entregas | Reverte o delta no EPI antigo e aplica o novo delta no EPI novo, garantindo consistência entre EPIs |
| **CT43** | Exclusão de entrega bem-sucedida remove o registro e atualiza estoque | Integração | app_entregas | Após exclusão via POST, o registro é removido e o estoque do EPI é restaurado corretamente |
| **CT44** | Exclusão de entrega com falha no service redireciona e preserva estoque | Integração | app_entregas | Quando `movimenta_por_exclusao` lança exceção, a view redireciona à lista e o estoque permanece inalterado |
| **CT45** | Listagem de entregas filtra por nome, colaborador, EPI e status | Integração | app_entregas | Aplica filtros conforme querystring (`q`, `colaborador`, `epi`, `status`) e monta `base_query` sem `page` |
| **CT46** | Contexto da listagem contém parâmetros e resultados filtrados corretamente | Integração | app_entregas | Inclui `q`, `colaborador_id`, `epi_id` e `status` no contexto, exibindo apenas registros compatíveis |
| **CT47** | Marcar entrega como **perdida** via POST mantém efeito no estoque | Integração | app_entregas | Atualiza status para **PERDIDO**, define `data_devolucao`, mantém o estoque do EPI inalterado e exibe mensagem de sucesso |
| **CT48** | Impedir “marcar perdido” para status inválidos | Integração | app_entregas | Para entregas em **FORNECIDO**/**DEVOLVIDO**, não altera o status e exibe mensagem de aviso |
| **CT49** | Rejeitar GET em “marcar perdido” | Integração | app_entregas | Apenas **POST** é aceito: requisições **GET** redirecionam sem efeitos colaterais no registro |
| **CT50** | Atender solicitação GET renderiza página de confirmação | Integração | app_entregas | GET de solicitação **pendente** retorna status 200 e renderiza `solicitacao_atender_confirm.html` |
| **CT51** | POST em solicitação com status inválido (REPROVADA) exibe aviso e redireciona | Integração | app_entregas | Exibe mensagem “apenas solicitações pendentes/aprovadas podem ser atendidas” e redireciona para `solicitacoes_gerenciar` |



[🔝 Voltar ao Índice](#índice)

---

## 9. Métricas de Qualidade

| Métrica | Valor Esperado |
|----------|----------------|
| Cobertura total | **≥ 90%** |
| Cobertura de linhas críticas (views, services) | ≥ 85% |
| Testes falhos permitidos | 0 |
| Tempo médio de execução | ≤ 15s |
| Execução automatizada | Em cada push/PR na branch `main` |

[🔝 Voltar ao Índice](#índice)

---

## 10. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|--------|----------|-----------|
| Alterações no schema do banco invalidam fixtures | Alto | Atualizar fixtures e rodar `makemigrations` antes dos testes |
| Dependência de permissões nos testes | Médio | Criar função `criar_usuario_com_permissao()` reutilizável |
| Redução de cobertura após merge | Alto | Bloquear merge se cobertura < 90% no Codecov |
| Lentidão nos testes de integração | Baixo | Usar SQLite in-memory nos testes |

[🔝 Voltar ao Índice](#índice)

---

## 11. Papéis e Responsabilidades

| Papel | Responsável | Atividade |
|--------|--------------|-----------|
| **Desenvolvedor** | Felipe Fernandes Ribeiro | Implementar testes unitários |
| **Desenvolvedor** | Jonathan Eichenberger | Implementar testes de integração |
| **Desenvolvedor** | Jonathan Eichenberger e Felipe Fernandes Ribeiro | Implementar testes de funcionais automatizados com Selenium IDE (Teste de sistemas End-to-End) |
| **Revisor Técnico** | Jonathan Eichenberger | Revisão de PRs e verificação de cobertura |
| **DevOps/CI** | GitHub Actions | Execução automática da suíte e envio ao Codecov |

[🔝 Voltar ao Índice](#índice)

---

## 12. Critérios de Aceitação

- Funcionalidades críticas testadas (CRUDs, login, permissões, relatórios).  
- Nenhum teste falho.  
- Cobertura **≥ 90%**.  
- Relatórios disponíveis na pipeline CI.  
- Commit na branch `main` exibe selo verde no Codecov.

[🔝 Voltar ao Índice](#índice)

---

## 13. Execução e Relatórios

**Comandos principais:**
```bash
# Executar todos os testes com relatório de cobertura no terminal
pytest --cov=. --cov-report=term-missing

# Gerar relatório de cobertura em HTML
pytest --cov=. --cov-report=html

# Enviar cobertura para o Codecov
bash <(curl -s https://codecov.io/bash)
```

[🔝 Voltar ao Índice](#índice)

---

## 🗂️ Relatórios de Cobertura

Os relatórios de cobertura serão **gerados automaticamente** após a execução dos testes:

📄 **Local (HTML):**  
`/htmlcov/index.html`

☁️ **Publicação automática:**  
Os relatórios são enviados e publicados no **Codecov** após a execução do pipeline no **GitHub Actions**.

[🔝 Voltar ao Índice](#índice)

---

## 📊 14. Conclusão

Este plano garante um **processo sistemático e automatizado de verificação da qualidade** do Sistema de Controle de EPI, cobrindo todos os módulos críticos e assegurando **alta confiabilidade com cobertura mínima de 90%**.

A **manutenção contínua deste plano**, com revisões a cada nova funcionalidade ou requisito, garantirá a **evolução estável e segura** do sistema.

[🔝 Voltar ao Índice](#índice)


