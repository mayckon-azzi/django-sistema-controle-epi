# tests/test_colaborador_view.py
import pytest
from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse

from app_colaboradores.models import Colaborador


def criar_usuario_com_permissao(*codenames):
    """
    Cria um usuário de teste com permissões específicas.
    """
    usuario = User.objects.create_user("admin_test", password="x")
    permissoes = Permission.objects.filter(
        codename__in=codenames, content_type__app_label="app_colaboradores"
    )
    usuario.user_permissions.add(*permissoes)
    usuario.is_staff = True
    usuario.is_superuser = False
    usuario.save()
    return usuario


@pytest.mark.django_db
def test_lista_colaboradores_requer_permissao_e_aplica_filtros(client):
    """
    Testa se a listagem de colaboradores requer permissão específica
    e se os filtros de pesquisa funcionam corretamente.
    """
    usuario = criar_usuario_com_permissao("view_colaborador")
    client.force_login(usuario)

    Colaborador.objects.create(nome="Alice", matricula="A1", email="a@x.com")
    Colaborador.objects.create(nome="Bob", matricula="B1", email="b@x.com")

    url = reverse("app_colaboradores:lista")
    resposta = client.get(url, {"q": "ali"})
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Alice" in html and "Bob" not in html


@pytest.mark.django_db
def test_criar_colaborador_permanece_na_pagina_e_cria_usuario_e_grupos(client):
    """
    Testa a criação de um colaborador, verificando se o usuário e os grupos
    associados são criados corretamente, permanecendo na página de criação.
    """
    usuario = criar_usuario_com_permissao("add_colaborador", "view_colaborador")
    client.force_login(usuario)

    grupo = Group.objects.create(name="almoxarife")

    url = reverse("app_colaboradores:criar")
    resposta = client.post(
        url,
        data={
            "nome": "João da Silva",
            "email": "joao@empresa.com",
            "matricula": "C123",
            "funcao": "Operador",
            "setor": "Chão de Fábrica",
            "telefone": "9999-0000",
            "ativo": "on",
            "criar_usuario": "on",
            "groups": [grupo.id],
        },
        follow=True,
    )

    assert resposta.status_code == 200
    colaborador = Colaborador.objects.get(matricula="C123")
    assert colaborador.user is not None
    assert grupo in colaborador.user.groups.all()
    assert "cadastrado com sucesso" in resposta.content.decode().lower()


@pytest.mark.django_db
def test_editar_colaborador_atualiza_email_status_e_grupos(client):
    """
    Testa a edição de um colaborador, verificando se o email do usuário,
    status ativo e grupos são atualizados corretamente.
    """
    usuario = criar_usuario_com_permissao("change_colaborador", "view_colaborador")
    client.force_login(usuario)

    grupo1 = Group.objects.create(name="colaborador")
    grupo2 = Group.objects.create(name="almoxarife")

    colaborador = Colaborador.objects.create(
        nome="Maria", matricula="M1", email="maria@x.com", ativo=True
    )
    usuario_maria = User.objects.create_user(
        "maria", email="maria@x.com", password="x", is_active=True
    )
    colaborador.user = usuario_maria
    colaborador.save()

    url = reverse("app_colaboradores:editar", kwargs={"pk": colaborador.pk})
    resposta = client.post(
        url,
        data={
            "nome": "Maria",
            "email": "novo@empresa.com",
            "matricula": "M1",
            "funcao": "",
            "setor": "",
            "telefone": "",
            "ativo": "",
            "groups": [grupo2.id],
        },
        follow=True,
    )

    assert resposta.status_code == 200
    colaborador.refresh_from_db()
    usuario_maria.refresh_from_db()
    assert usuario_maria.email == "novo@empresa.com"
    assert usuario_maria.is_active is False
    assert grupo2 in usuario_maria.groups.all() and grupo1 not in usuario_maria.groups.all()


@pytest.mark.django_db
def test_excluir_colaborador_redireciona_e_desativa_soft(client):
    """
    Testa a exclusão de um colaborador, verificando se ele é
    desativado (soft delete) e a operação redireciona corretamente.
    """
    usuario = criar_usuario_com_permissao("delete_colaborador", "view_colaborador")
    client.force_login(usuario)

    colaborador = Colaborador.objects.create(nome="X", matricula="Z9")
    url = reverse("app_colaboradores:excluir", kwargs={"pk": colaborador.pk})
    resposta = client.post(url, follow=True)

    assert resposta.status_code == 200
    assert Colaborador.objects.filter(pk=colaborador.pk).exists()
    colaborador.refresh_from_db()
    assert colaborador.ativo is False
