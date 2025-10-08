# tests/test_colaboradores_lista_filtros_e_contexto.py
import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from app_colaboradores.models import Colaborador


@pytest.mark.django_db
def test_lista_colaboradores_filtro_ativo_1_apenas_ativos(client):
    """Garante que o filtro ativo=1 retorne somente colaboradores ativos."""
    u = User.objects.create_user("viewer", password="x")
    u.user_permissions.add(Permission.objects.get(codename="view_colaborador"))
    client.force_login(u)

    Colaborador.objects.create(nome="Ativo A", matricula="A1", email="a@x.com", ativo=True)
    Colaborador.objects.create(nome="Inativo B", matricula="B1", email="b@x.com", ativo=False)

    url = reverse("app_colaboradores:lista")
    r = client.get(url, {"ativo": "1"})
    assert r.status_code == 200
    html = r.content.decode()
    assert "Ativo A" in html
    assert "Inativo B" not in html


@pytest.mark.django_db
def test_lista_colaboradores_filtro_ativo_0_apenas_inativos(client):
    """Garante que o filtro ativo=0 retorne somente colaboradores inativos."""
    u = User.objects.create_user("viewer2", password="x")
    u.user_permissions.add(Permission.objects.get(codename="view_colaborador"))
    client.force_login(u)

    Colaborador.objects.create(nome="Ativo C", matricula="C1", email="c@x.com", ativo=True)
    Colaborador.objects.create(nome="Inativo D", matricula="D1", email="d@x.com", ativo=False)

    url = reverse("app_colaboradores:lista")
    r = client.get(url, {"ativo": "0"})
    assert r.status_code == 200
    html = r.content.decode()
    assert "Inativo D" in html
    assert "Ativo C" not in html


@pytest.mark.django_db
def test_lista_colaboradores_contexto_inclui_q_e_ativo(client):
    """Confere que o contexto da listagem inclui os campos 'q' e 'ativo' conforme querystring."""
    u = User.objects.create_user("viewer3", password="x")
    u.user_permissions.add(Permission.objects.get(codename="view_colaborador"))
    client.force_login(u)

    url = reverse("app_colaboradores:lista")
    r = client.get(url, {"q": "abc", "ativo": "1"})
    assert r.status_code == 200
    ctx = r.context[-1]
    assert ctx.get("q") == "abc"
    assert ctx.get("ativo") == "1"
