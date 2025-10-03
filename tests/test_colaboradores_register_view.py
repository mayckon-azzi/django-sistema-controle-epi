# tests/test_colaboradores_register_view.py
import pytest
from django.contrib.auth.models import Group, User
from django.db import OperationalError
from django.urls import reverse

from app_colaboradores.models import Colaborador


@pytest.mark.django_db
def test_registro_colaborador_cria_usuario_e_colaborador(client):
    """
    Verifica se o registro de um novo colaborador cria corretamente
    o usuário e o colaborador no sistema.
    """
    Group.objects.get_or_create(name="Colaborador")  # grupo padrão usado no form
    url = reverse("app_colaboradores:registrar")
    resposta = client.post(
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
    assert resposta.status_code == 200
    assert User.objects.filter(username="novo").exists()
    assert Colaborador.objects.filter(email="novo@empresa.com").exists()


@pytest.mark.django_db
def test_registro_trata_erro_banco_de_dados(client, monkeypatch):
    """
    Testa se o formulário de registro trata erros de banco de dados
    de forma graciosa, exibindo mensagem adequada sem quebrar a página.
    """
    url = reverse("app_colaboradores:registrar")
    from app_colaboradores import views as colab_views

    def falha(*args, **kwargs):
        raise OperationalError("db down")

    monkeypatch.setattr(colab_views.RegisterForm, "save", falha)
    resposta = client.post(
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
    assert resposta.status_code == 200
    assert "Banco de dados não inicializado".lower() in resposta.content.decode().lower()
