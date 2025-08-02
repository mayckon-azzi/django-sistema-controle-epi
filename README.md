# 🐍🚀 Iniciando um Projeto Django + Python no Windows

## ✅ Pré-requisitos

- Python instalado (3.8+)
- pip funcionando
- Visual Studio Code
- Git Bash ou Prompt de Comando
- (opcional) Ambiente virtual

---

## 📁 1. Criar a pasta do projeto

```bash
mkdir meu_projeto
cd meu_projeto
```

---

## 🧪 2. Criar e ativar o ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 📦 3. Instalar o Django

```bash
pip install django
```

---

## 🚀 4. Criar o projeto Django

```bash
django-admin startproject config .
```

> O ponto no final (.) coloca os arquivos direto na raiz.

---

## 🧩 5. Criar um app principal chamado `core`

```bash
python manage.py startapp core
```

---

## 🧷 6. Registrar o app no projeto

No arquivo `config/settings.py`, adicione `'core',` na lista `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'core',
]
```

---

## 🗃️ 7. Criar estrutura de pastas para templates e static

```plaintext
core/
├── templates/
│   └── core/
│       ├── base.html
│       └── index.html
└── static/
    └── core/
        ├── css/
        │   └── custom.css
        └── img/
```

---

## 🧭 8. Configurar templates e arquivos estáticos

No `config/settings.py`, edite:

```python
import os

# Templates
TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'core', 'templates')]

# Arquivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'core', 'static')]
```

---

## 🛠️ 9. Criar URL principal e conectar com o app

### Em `config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # conecta com core
]
```

### Em `core/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
]
```

---

## 📄 10. Criar a view e os templates

### Em `core/views.py`:

```python
from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')
```

### Em `core/templates/core/index.html`:

```html
{% extends 'core/base.html' %}

{% block title %}Página Inicial{% endblock %}

{% block content %}
<h1>Bem-vindo ao projeto Django!</h1>
{% endblock %}
```

---

## 🎨 11. Criar `base.html` com Bootstrap e CSS

### Em `core/templates/core/base.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}Meu Projeto{% endblock %}</title>
  {% load static %}
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="{% static 'core/css/custom.css' %}" rel="stylesheet">
</head>
<body>
  <main class="container py-4">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

---

## 🏁 12. Rodar o servidor

```bash
python manage.py runserver
```

Abra no navegador: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🚨 13. Dica importante: estrutura geral

```plaintext
meu_projeto/
├── venv/
├── manage.py
├── config/
│   └── settings.py
├── core/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │   └── core/
│   │       ├── base.html
│   │       └── index.html
│   └── static/
│       └── core/
│           ├── css/
│           │   └── custom.css
│           └── img/
```

---

## ✅ Pronto!

Agora você tem:

- Django configurado
- Arquitetura organizada
- Templates funcionando
- Bootstrap ativado
- CSS customizado carregando

## 
