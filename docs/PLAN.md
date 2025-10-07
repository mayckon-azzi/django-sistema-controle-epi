# 🧪 Plano de Testes — Sistema de Controle de EPI

**Versão:** 1.0  
**Autor:** Jonathan Eichenberger  
**Data:** 2025-10-06  
**Cobertura mínima esperada:** **93%**

---

##  Índice

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
- As alterações de código não reduzam a cobertura mínima de **93%**.  
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
- **Integração entre apps:** `app_entregas`, `app_colaboradores`, `app_epis`.

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
| **Funcional (Sistema)** | Validar fluxos completos (CRUDs, login, entregas). | Pytest + Client |
| **Regressão** | Reexecutar suíte completa após cada PR/Merge. | GitHub Actions |
| **Cobertura de Código** | Monitorar percentual mínimo de 93%. | Coverage.py + Codecov |

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
- Cobertura ≥ **93%**.  
- Sem falhas críticas ou regressões em funcionalidades principais.

[🔝 Voltar ao Índice](#índice)

---

## 7. Ambiente de Teste

| Item | Configuração |
|------|---------------|
| **Sistema Operacional** | Ubuntu 22.04 (Docker container) |
| **Banco de Dados** | SQLite para testes, MySQL em produção |
| **Ferramentas** | Pytest, Coverage.py, Codecov |
| **Execução local** | `pytest --cov=.` |
| **CI/CD** | GitHub Actions (`.github/workflows/tests.yml`) |

[🔝 Voltar ao Índice](#índice)

---

## 🧩 8. Casos de Teste (Resumo)

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


[🔝 Voltar ao Índice](#índice)

---

## 9. Métricas de Qualidade

| Métrica | Valor Esperado |
|----------|----------------|
| Cobertura total | **≥ 93%** |
| Cobertura de linhas críticas (views, services) | ≥ 90% |
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
| Redução de cobertura após merge | Alto | Bloquear merge se cobertura < 93% no Codecov |
| Lentidão nos testes de integração | Baixo | Usar SQLite in-memory nos testes |

[🔝 Voltar ao Índice](#índice)

---

## 11. Papéis e Responsabilidades

| Papel | Responsável | Atividade |
|--------|--------------|-----------|
| **Desenvolvedor** | Jonathan Eichenberger | Implementar testes unitários e integração |
| **Revisor Técnico** | Jonathan Eichenberger | Revisão de PRs e verificação de cobertura |
| **DevOps/CI** | GitHub Actions | Execução automática da suíte e envio ao Codecov |

[🔝 Voltar ao Índice](#índice)

---

## 12. Critérios de Aceitação

- Funcionalidades críticas testadas (CRUDs, login, permissões, relatórios).  
- Nenhum teste falho.  
- Cobertura **≥ 93%**.  
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

Este plano garante um **processo sistemático e automatizado de verificação da qualidade** do Sistema de Controle de EPI, cobrindo todos os módulos críticos e assegurando **alta confiabilidade com cobertura mínima de 93%**.

A **manutenção contínua deste plano**, com revisões a cada nova funcionalidade ou requisito, garantirá a **evolução estável e segura** do sistema.

[🔝 Voltar ao Índice](#índice)


