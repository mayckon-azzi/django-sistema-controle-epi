import pytest
from django.contrib.auth.models import User, Group
from django.db import OperationalError
from django.urls import reverse

from app_colaboradores.models import Colaborador

@pytest.mark.django_db
def test_registrar_success_creates_user_and_colab(client):
    Group.objects.get_or_create(name="Colaborador")  # grupo padrão usado no form
    url = reverse("app_colaboradores:registrar")
    resp = client.post(
        url,
        data={
            "username": "novo",
            "email": "novo@empresa.com",
            "password1": "Senha12345!",
            "password2": "Senha12345!",
            "nome": "Novo Usuário",
            "matricula": "Z9",
        },
        follow=True,
    )
    assert resp.status_code == 200
    assert User.objects.filter(username="novo").exists()
    assert Colaborador.objects.filter(email="novo@empresa.com").exists()

@pytest.mark.django_db
def test_registrar_handles_db_error_gracefully(client, monkeypatch):
    url = reverse("app_colaboradores:registrar")

    # Monkeypatch: força erro ao salvar
    from app_colaboradores import views as colab_views

    def boom(*a, **k):
        raise OperationalError("db down")

    monkeypatch.setattr(colab_views.RegisterForm, "save", boom)

    resp = client.post(
        url,
        data={
            "username": "x",
            "email": "x@empresa.com",
            "password1": "Senha12345!",
            "password2": "Senha12345!",
            "nome": "X",
            "matricula": "X1",
        },
        follow=True,
    )
    assert resp.status_code == 200
    assert "Banco de dados não inicializado".lower() in resp.content.decode().lower()
