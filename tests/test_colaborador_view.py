# tests/test_colaborador_view.py
import pytest
from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse

from app_colaboradores.models import Colaborador


def make_user_with_perms(*codenames):
    user = User.objects.create_user("admin_test", password="x")
    perms = Permission.objects.filter(
        codename__in=codenames, content_type__app_label="app_colaboradores"
    )
    user.user_permissions.add(*perms)
    user.is_staff = True
    user.is_superuser = False
    user.save()
    return user


@pytest.mark.django_db
def test_lista_requires_perm_and_filters(client):
    user = make_user_with_perms("view_colaborador")
    client.force_login(user)

    Colaborador.objects.create(nome="Alice", matricula="A1", email="a@x.com")
    Colaborador.objects.create(nome="Bob", matricula="B1", email="b@x.com")

    url = reverse("app_colaboradores:lista")
    resp = client.get(url, {"q": "ali"})
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Alice" in html and "Bob" not in html


@pytest.mark.django_db
def test_criar_stays_on_page_and_may_create_user_and_groups(client):
    user = make_user_with_perms("add_colaborador", "view_colaborador")
    client.force_login(user)

    g = Group.objects.create(name="almoxarife")

    url = reverse("app_colaboradores:criar")
    resp = client.post(
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
            "groups": [g.id],
        },
        follow=True,
    )
    assert resp.status_code == 200
    colab = Colaborador.objects.get(matricula="C123")
    assert colab.user is not None
    assert g in colab.user.groups.all()
    assert "cadastrado com sucesso" in resp.content.decode().lower()


@pytest.mark.django_db
def test_editar_updates_user_email_and_active_and_groups(client):
    user = make_user_with_perms("change_colaborador", "view_colaborador")
    client.force_login(user)
    g1 = Group.objects.create(name="colaborador")
    g2 = Group.objects.create(name="almoxarife")
    c = Colaborador.objects.create(nome="Maria", matricula="M1", email="maria@x.com", ativo=True)
    u = User.objects.create_user("maria", email="maria@x.com", password="x", is_active=True)
    c.user = u
    c.save()

    url = reverse("app_colaboradores:editar", kwargs={"pk": c.pk})
    resp = client.post(
        url,
        data={
            "nome": "Maria",
            "email": "novo@empresa.com",
            "matricula": "M1",
            "funcao": "",
            "setor": "",
            "telefone": "",
            "ativo": "",
            "groups": [g2.id],
        },
        follow=True,
    )
    assert resp.status_code == 200
    c.refresh_from_db()
    u.refresh_from_db()
    assert u.email == "novo@empresa.com"
    assert u.is_active is False
    assert g2 in u.groups.all() and g1 not in u.groups.all()


@pytest.mark.django_db
def test_delete_redirects_and_removes(client):
    user = make_user_with_perms("delete_colaborador", "view_colaborador")
    client.force_login(user)
    c = Colaborador.objects.create(nome="X", matricula="Z9")
    url = reverse("app_colaboradores:excluir", kwargs={"pk": c.pk})
    resp = client.post(url, follow=True)
    assert resp.status_code == 200
    assert not Colaborador.objects.filter(pk=c.pk).exists()
