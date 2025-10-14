# Guia Didático — Selenium WebDriver no Sistema de Controle de EPI

**Última atualização:** 2025-10-14
**Escopo:** Introdução didática e prática da ferramenta **Selenium WebDriver**, com foco na automação de testes funcionais no Sistema de Controle de EPI (Django + Pytest).
**Objetivo:** Ensinar passo a passo como instalar, configurar e aplicar o Selenium em fluxos reais do sistema (login, CRUDs, relatórios, etc.).

---

## Índice

1. [O que é o Selenium WebDriver](#1-o-que-é-o-selenium-webdriver)
2. [Como o Selenium funciona](#2-como-o-selenium-funciona)
3. [Instalação e primeiro teste](#3-instalação-e-primeiro-teste)
4. [Boas práticas para iniciantes](#4-boas-práticas-para-iniciantes)
5. [Page Objects (estrutura recomendada)](#5-page-objects-estrutura-recomendada)
6. [Rodando no CI (GitHub Actions)](#6-rodando-no-ci-github-actions)
7. [Aplicando no Sistema de Controle de EPI](#7-aplicando-no-sistema-de-controle-de-epi)
8. [Mapa dos 20 testes e equivalentes em Selenium](#8-mapa-dos-20-testes-e-equivalentes-em-selenium)
9. [Suite de exemplo pronta (tests_selenium)](#9-suite-de-exemplo-pronta-tests_selenium)
10. [Conclusão](#10-conclusão)

---

## 1. O que é o Selenium WebDriver

O **Selenium WebDriver** é uma ferramenta usada para automatizar navegadores.
Com ele, é possível simular as ações de um usuário real, como acessar páginas, clicar em botões, preencher formulários e validar mensagens.

💡 **Principais usos**:

* **Testes funcionais** — valida se as funcionalidades da aplicação funcionam corretamente.
* **Testes de regressão** — assegura que novas alterações não quebraram fluxos anteriores.
* **Validação de interface** — garante que o usuário consegue navegar e interagir sem erros.

**Exemplo:** testar o fluxo completo de login e acesso ao módulo de “Colaboradores”.

🔝 [Voltar ao Índice](#índice)

---

## 2. Como o Selenium funciona

O Selenium é composto por três camadas principais:

| **Componente** | **Função**                                                                |
| -------------- | ------------------------------------------------------------------------- |
| WebDriver      | Interface que envia comandos ao navegador (abrir URL, clicar, etc.)       |
| Browser Driver | Faz a ponte entre Selenium e o navegador (ex.: ChromeDriver, GeckoDriver) |
| Test Runner    | Framework que executa os testes (no seu caso, **Pytest**)                 |

**Exemplo de arquitetura:**
`Test → Selenium WebDriver → ChromeDriver → Google Chrome`

👉 No **Selenium 4**, o *Selenium Manager* já baixa o driver automaticamente — não é mais necessário baixar manualmente o `chromedriver.exe`.

🔝 [Voltar ao Índice](#índice)

---

## 3. Instalação e primeiro teste

### Pré-requisitos

* Python **3.10+**
* Navegador instalado (Google Chrome recomendado)
* Ambiente virtual configurado (`venv`)
* Django + Pytest já funcionando no projeto

### Passo a passo

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac

# 2. Instale as dependências
pip install selenium pytest pytest-django webdriver-manager
```

> **webdriver-manager** evita problemas de versão, baixando automaticamente o driver correto do navegador.

---

### Crie um teste simples

**Arquivo:** `tests_selenium/test_smoke.py`

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_abrir_home():
    driver = webdriver.Chrome()
    driver.get("http://localhost:8000/")
    assert "Sistema" in driver.title or "EPI" in driver.page_source
    driver.quit()
```

**Executar o teste:**

```bash
pytest -q tests_selenium

pytest --maxfail=1 --tb=short --capture=tee-sys -v tests_selenium   <-- Este é usado para printar em caso de erro.
```

🔝 [Voltar ao Índice](#índice)

---

## 4. Boas práticas para iniciantes

* ✅ Evite `time.sleep()` — use **esperas explícitas** (`WebDriverWait`).
* ✅ Organize localizadores (IDs, classes, XPaths) em um único lugar.
* ✅ Use o modo **headless** no CI.
* ✅ Capture evidências com `driver.save_screenshot("falha.png")`.
* ✅ Mantenha testes **curtos e independentes**.
* ✅ Use **IDs fixos ou atributos `data-testid`** nos elementos HTML.

🔝 [Voltar ao Índice](#índice)

---

## 5. Page Objects (estrutura recomendada)

O padrão **Page Object** separa a lógica de navegação dos testes.
Cada página é representada por uma classe, contendo os elementos e ações.

**Exemplo:** `pages/login_page.py`

```python
from selenium.webdriver.common.by import By

class LoginPage:
    URL = "http://localhost:8000/accounts/login/"
    USER = (By.ID, "id_username")
    PASS = (By.ID, "id_password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    def login(self, username, password):
        self.driver.find_element(*self.USER).send_keys(username)
        self.driver.find_element(*self.PASS).send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()
```

🔝 [Voltar ao Índice](#índice)

---

## 7. Aplicando no Sistema de Controle de EPI

| **Módulo**          | **URL base**      | **Função**                         |
| ------------------- | ----------------- | ---------------------------------- |
| `app_core`          | `/`               | Home e mensagens de sucesso        |
| `app_colaboradores` | `/colaboradores/` | Login e CRUD de colaboradores      |
| `app_epis`          | `/epis/`          | Listagem e edição de EPIs          |
| `app_entregas`      | `/entregas/`      | Criação e controle de entregas     |
| `app_relatorios`    | `/relatorios/`    | Geração e exportação de relatórios |

### Exemplos práticos

```python
def test_home_responde_200(driver):
    driver.get("http://localhost:8000/")
    assert "Sistema" in driver.title
```

```python
from pages.login_page import LoginPage

def test_login_e_lista_colaboradores(driver):
    page = LoginPage(driver)
    page.open()
    page.login("admin", "admin123")
    driver.get("http://localhost:8000/colaboradores/")
    assert "Colaboradores" in driver.page_source
```

🔝 [Voltar ao Índice](#índice)

---

## 8. Mapa dos 20 testes e equivalentes em Selenium

| **Grupo**     | **Teste (pytest)**          | **Objetivo**                   | **Equivalente Selenium**               |
| ------------- | --------------------------- | ------------------------------ | -------------------------------------- |
| Core          | home responde 200           | Verifica disponibilidade       | Acessar `/` e validar título           |
| Core          | teste_mensagens redireciona | Confirma exibição de mensagens | Acessar `/teste-mensagens/` e checar   |
| Colaboradores | lista exige login           | Proteção de rota               | Verificar redirecionamento ao login    |
| Colaboradores | lista com permissão         | Acesso liberado                | Login → acessar `/colaboradores/`      |
| EPIs          | lista responde 200          | Carregamento da tabela         | Acessar `/epis/`                       |
| Entregas      | criar exige login           | Bloqueio sem autenticação      | Acessar `/entregas/novo/` sem login    |
| Relatórios    | index/exportar exige login  | Proteção de rota               | Acessar `/relatorios/` sem login       |
| Forms         | validações                  | Regras de negócio              | Submeter formulário inválido e validar |

🔝 [Voltar ao Índice](#índice)

---

## 9. Suite de exemplo pronta (tests_selenium)

**Estrutura sugerida:**

```
tests_selenium/
├── conftest.py
├── pages/
│   ├── login_page.py
│   ├── colaboradores_page.py
│   ├── epis_page.py
│   ├── entregas_page.py
│   └── relatorios_page.py
├── test_app_core.py
├── test_colaboradores.py
├── test_epis.py
├── test_entregas.py
└── test_relatorios.py
```

---

### conftest.py

```python
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

@pytest.fixture
def driver():
    opts = Options()
    if os.getenv("HEADLESS", "1") == "1":
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1366, 900)
    yield driver
    driver.quit()
```

---

### Exemplo — test_core.py

```python
def test_home(driver):
    driver.get("http://localhost:8000/")
    assert "Sistema" in driver.title

def test_teste_mensagens(driver):
    driver.get("http://localhost:8000/teste-mensagens/")
    assert "Sucesso" in driver.page_source
```

🔝 [Voltar ao Índice](#índice)

---

## 10. Conclusão

O **Selenium WebDriver** é uma ferramenta poderosa para **testes funcionais**, permitindo validar a experiência do usuário de ponta a ponta.
No **Sistema de Controle de EPI**, ele complementa os **testes unitários** e **de integração** já existentes com **Pytest**, garantindo confiabilidade tanto na camada de **back-end** quanto na **interface**.

🔝 [Voltar ao Índice](#índice)


