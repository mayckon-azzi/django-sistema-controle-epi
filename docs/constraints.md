# 📘 Constraints de Dados — Sistema de Controle de EPI

**Última atualização:** 2025-10-07  
**Escopo:** *Constraints* (restrições) aplicadas nos modelos dos apps `app_colaboradores`, `app_epis`, `app_entregas` e `app_relatorios`, com referências a testes já existentes na pasta `tests/`.

---

## Índice

1. [Visão Geral](#1-visão-geral)  
2. [app_colaboradores](#2-app_colaboradores)  
   2.1 [Colaborador](#21-colaborador)  
3. [app_epis](#3-app_epis)  
   3.1 [CategoriaEPI](#31-categoriaepi)  
   3.2 [EPI](#32-epi)  
4. [app_entregas](#4-app_entregas)  
   4.1 [Entrega](#41-entrega)  
   4.2 [Solicitacao](#42-solicitacao)  
5. [Regras de Negócio x Constraints](#5-regras-de-negócio-x-constraints)  
6. [Exemplos de Testes (trechos reais)](#6-exemplos-de-testes-trechos-reais)  
7. [Checklist Rápido](#7-checklist-rápido)  
8. [Como rodar e inspecionar cobertura](#8-como-rodar-e-inspecionar-cobertura)

---

## 1. Visão Geral

**Constraints** (restrições) garantem a integridade dos dados no banco. Podem ser:
- **PRIMARY KEY**: identifica unicamente cada registro.
- **UNIQUE**: evita duplicidade (ex.: `codigo` de EPI).
- **NOT NULL**: campo obrigatório (não aceita `NULL`).
- **FOREIGN KEY**: referencia consistente entre tabelas.
- **CHECK**: regra lógica (ex.: `estoque >= 0`).
- **DEFAULT**: valor padrão (ex.: `ativo = True`).

> Em Django, muitas dessas regras são obtidas por tipo de campo (`PositiveIntegerField`, `ForeignKey`, `unique=True`) e por **validações de formulário/modelo** (camada de aplicação).

[🔝 Voltar ao Índice](#índice)

---

## 2. app_colaboradores

### 2.1 Colaborador

**Campos relevantes (derivados dos testes):**
- `nome` *(CharField, NOT NULL)*
- `email` *(EmailField, NOT NULL, pode ter UNIQUE dependendo da sua definição atual — nos testes usamos busca por email)*
- `matricula` *(CharField, recomendado **UNIQUE** — os testes assumem matrícula única em formulários)*
- `ativo` *(BooleanField, **DEFAULT=True**; usado para soft delete)*
- `user` *(FK → `auth.User`, **UNIQUE** opcional se 1–1 for exigido)*  
- `funcao`/`cargo`, `setor`, `telefone` *(opcionais)*

**Constraints sugeridas / observadas:**
- `UNIQUE(matricula)` — evita duplicidade de cadastro.
- `FK(user)` — mantém vínculo consistente com `User`.
- `CHECK` de domínio via app: **soft delete** altera `ativo=False` (não hard delete).

**Testes relacionados:**  
- `test_colaboradores_form.py` (matrícula única)  
- `test_colaborador_view.py`, `test_colaboradores_delete.py` (soft delete + mensagens)  
- `test_colaboradores_permissions.py` (acesso condicional por permissão)  
- `test_colaboradores_perfil_autolink.py` (vínculo por email User↔Colaborador)

[🔝 Voltar ao Índice](#índice)

---

## 3. app_epis

### 3.1 CategoriaEPI
- `nome` *(CharField, NOT NULL, **UNIQUE** recomendado)*

**Constraints sugeridas:**
- `UNIQUE(nome)` — categorias sem duplicidade.

### 3.2 EPI
- `codigo` *(CharField, **UNIQUE**, NOT NULL)*
- `nome` *(CharField, NOT NULL)*
- `categoria` *(FK → `CategoriaEPI`, NOT NULL)*
- `tamanho` *(CharField opcional)*
- `ativo` *(BooleanField, **DEFAULT=True**)  
- `estoque` *(**PositiveIntegerField**, **DEFAULT=0**)  
- `estoque_minimo` *(**PositiveIntegerField**, **DEFAULT=0**)*

**Constraints observadas (derivadas do tipo de campo e testes):**
- `UNIQUE(codigo)`
- `FK(categoria)`
- `CHECK(estoque >= 0)`
- `CHECK(estoque_minimo >= 0)`

**Testes relacionados:**  
- `test_epis_models.py`, `test_models_epi.py` (não permitir negativos; `__str__`)  
- `test_epis_forms.py` (validação de negativos no form; criação de categorias padrão)  
- `test_epis_views.py` (CRUD + ProtectedError ao excluir com dependências)

[🔝 Voltar ao Índice](#índice)

---

## 4. app_entregas

### 4.1 Entrega
- `colaborador` *(FK → `Colaborador`, NOT NULL)*
- `epi` *(FK → `EPI`, NOT NULL)*
- `quantidade` *(**PositiveIntegerField**, NOT NULL)*
- `status` *(Choices: **EMPRESTADO**, **FORNECIDO**, **DEVOLVIDO**, **PERDIDO**)*  
- `data_entrega` *(DateTimeField, NOT NULL — geralmente auto/preenchida)*  
- `data_prevista_devolucao` *(DateTimeField, **obrigatória se status=EMPRESTADO**)*  
- `data_devolucao` *(DateTimeField, **obrigatória se status=DEVOLVIDO**)*  
- `observacao` *(TextField opcional)*

**Constraints e regras:**
- `FK(colaborador)`, `FK(epi)`
- `CHECK(quantidade > 0)` (via PositiveIntegerField)
- **Regras condicionais (camada de aplicação / forms):**  
  - Se `status=EMPRESTADO` → exigir `data_prevista_devolucao` **futura**  
  - Se `status=DEVOLVIDO` → exigir `data_devolucao`
- **Serviço de domínio (services):** movimenta estoque na criação/edição/exclusão
  - Garante **não estourar estoque**; lança `ValidationError` se insuficiente.

**Testes relacionados:**  
- `test_entregas_form.py` (datas obrigatórias/futuras conforme status)  
- `test_entregas_services.py` (movimentação de estoque; erro por estoque insuficiente)  
- `test_entregas_views.py` (CRUD, mensagens, fluxo completo de solicitações)

### 4.2 Solicitacao
- `colaborador` *(FK → `Colaborador`, NOT NULL)*
- `epi` *(FK → `EPI`, NOT NULL)*
- `quantidade` *(**PositiveIntegerField**, NOT NULL)*
- `status` *(Choices: **PENDENTE**, **APROVADA**, **ATENDIDA**, **REPROVADA**)*

**Constraints e regras:**
- `FK(colaborador)`, `FK(epi)`
- `CHECK(quantidade > 0)`
- **Regra de negócio (camada de aplicação):** transições de status válidas; atendimento consome estoque.

**Testes relacionados:**  
- `test_entregas_views.py` (criar → aprovar → atender → devolver → reprovar)  
- `test_entregas_form.py` (quantidade > 0; EPI ativo para solicitar)

[🔝 Voltar ao Índice](#índice)

---

## 5. Regras de Negócio x Constraints

- **Constraints de banco** (ex.: `UNIQUE`, `CHECK`, `FK`) impedem persistência inválida **independente da aplicação**.
- **Validações de formulário/modelo/serviço** (ex.: “se `status=EMPRESTADO` exigir `data_prevista_devolucao` futura”) garantem **regras condicionais** que seriam difíceis de expressar apenas em SQL.

**Nos seus testes**:
- *Constraints de banco* são validadas quando esperamos `IntegrityError`/`DataError`.  
- *Regras de negócio* são validadas quando o `Form.is_valid()` falha com erro específico ou quando serviços lançam `ValidationError`.

[🔝 Voltar ao Índice](#índice)

---

## 6. Exemplos de Testes (trechos reais)

**EPI — impedir estoque negativo (constraint CHECK via campo positivo):**
```python
# tests/test_epis_models.py
@pytest.mark.django_db
def test_constraint_estoque_epi_nao_negativo():
    categoria = CategoriaEPI.objects.create(nome="Mãos")
    with pytest.raises((IntegrityError, DataError, ValueError)):
        EPI.objects.create(codigo="LUV-001", nome="Luva", categoria=categoria, estoque=-1)
```

**Entrega — regras condicionais de data conforme status (camada de formulário):**

```python
# tests/test_entregas_form.py
@pytest.mark.django_db
def test_formulario_entrega_requer_data_prevista_para_emprestado():
    # ... cria epi, colaborador
    form = EntregaForm(data={
        "colaborador": colaborador.pk,
        "epi": epi.pk,
        "quantidade": 1,
        "status": Entrega.Status.EMPRESTADO,
        # falta data_prevista_devolucao → inválido
    })
    assert not form.is_valid()
    assert "data_prevista_devolucao" in form.errors
```

**Services — movimentação de estoque e erro por insuficiência (regra de domínio):
```python
# tests/test_entregas_services.py
@pytest.mark.django_db
def test_movimenta_epi_gera_erro_quando_estoque_insuficiente():
    # ... cria epi com estoque=2
    entrega = Entrega(epi=epi, quantidade=5, status=Entrega.Status.EMPRESTADO)
    with pytest.raises(ValidationError):
        movimenta_por_entrega(entrega, antiga=None)
```

[🔝 Voltar ao Índice](#índice)

---

## 7. Checklist Rápido

- [ ] `EPI.codigo` é **UNIQUE**  
- [ ] `EPI.estoque` e `EPI.estoque_minimo` **não negativos**  
- [ ] `Entrega.quantidade > 0`  
- [ ] `Entrega.status=EMPRESTADO` → **exige** `data_prevista_devolucao` **futura**  
- [ ] `Entrega.status=DEVOLVIDO` → **exige** `data_devolucao`  
- [ ] **Movimentação de estoque** valida disponibilidade (serviço)  
- [ ] `Colaborador.matricula` é **UNIQUE** (recomendado e refletido nos testes de form)  
- [ ] **Soft delete** de `Colaborador` via `ativo=False`  
- [ ] **FKs consistentes** (`Entrega` → `EPI` / `Colaborador`; `EPI` → `CategoriaEPI`)

[🔝 Voltar ao Índice](#índice)

---

## 8. Como rodar e inspecionar cobertura

```bash
# Executar toda a suíte com cobertura
pytest --cov=. --cov-report=term-missing

# Gerar relatório de cobertura em HTML (abrir no navegador)
pytest --cov=. --cov-report=html
# → arquivo: htmlcov/index.html
```

**Integração com Codecov (via CI):**

```bash
bash <(curl -s https://codecov.io/bash)
```

[🔝 Voltar ao Índice](#índice)