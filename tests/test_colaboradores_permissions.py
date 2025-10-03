# tests/test_colaboradores_permissions.py
import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse


@pytest.mark.django_db
def test_lista_colaboradores_requer_login_redireciona_para_entrar(client):
    """
    Verifica se a página de listagem de colaboradores exige login.
    Usuário não autenticado deve ser redirecionado para a página de login.
    """
    url = reverse("app_colaboradores:lista")
    resposta = client.get(url)
    assert resposta.status_code == 302
    assert reverse("app_colaboradores:entrar") in resposta.url


@pytest.mark.django_db
def test_lista_colaboradores_sem_permissao_retorna_403(client):
    """
    Verifica se usuário autenticado sem a permissão 'view_colaborador'
    recebe erro 403 ao acessar a listagem.
    """
    usuario = User.objects.create_user("sem_permissao", password="x")
    client.force_login(usuario)

    url = reverse("app_colaboradores:lista")
    resposta = client.get(url)
    assert resposta.status_code == 403


@pytest.mark.django_db
def test_lista_colaboradores_com_permissao_exibe_pagina(client):
    """
    Verifica se usuário autenticado com a permissão 'view_colaborador'
    consegue acessar a página de listagem corretamente (status 200).
    """
    usuario = User.objects.create_user("com_permissao", password="x")
    permissao = Permission.objects.get(codename="view_colaborador")
    usuario.user_permissions.add(permissao)
    client.force_login(usuario)

    url = reverse("app_colaboradores:lista")
    resposta = client.get(url)
    assert resposta.status_code == 200
