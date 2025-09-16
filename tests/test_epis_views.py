import pytest
from django.contrib.auth.models import Permission, User
from django.db.models.deletion import ProtectedError
from django.urls import reverse

from app_epis.models import CategoriaEPI, EPI


def _login_with_perms(client, *codenames):
    u = User.objects.create_user("user", password="x")
    for code in codenames:
        u.user_permissions.add(Permission.objects.get(codename=code))
    client.force_login(u)
    return u


@pytest.mark.django_db
def test_lista_filters_and_flags(client):
    cat1 = CategoriaEPI.objects.create(nome="Luvas")
    cat2 = CategoriaEPI.objects.create(nome="Capacete")
    EPI.objects.create(codigo="L1", nome="Luva A", categoria=cat1, estoque=2, estoque_minimo=5)  # abaixo
    EPI.objects.create(codigo="L2", nome="Luva B", categoria=cat1, estoque=10, estoque_minimo=5) # ok
    EPI.objects.create(codigo="C1", nome="Capacete", categoria=cat2, estoque=0, estoque_minimo=0, ativo=False)

    url = reverse("app_epis:lista")

    # sem filtros
    resp = client.get(url)
    assert resp.status_code == 200
    html = resp.content.decode().lower()
    assert "luva a" in html and "luva b" in html and "capacete" in html

    # filtro por q
    resp = client.get(url + "?q=luva")
    html = resp.content.decode().lower()
    assert "luva a" in html and "luva b" in html and "capacete" not in html

    # filtro categoria
    resp = client.get(url + f"?categoria={cat2.id}")
    html = resp.content.decode().lower()
    assert "capacete" in html and "luva a" not in html

    # somente ativos
    resp = client.get(url + "?ativos=1")
    html = resp.content.decode().lower()
    assert "capacete" not in html  # estava inativo

    # abaixo do mínimo
    resp = client.get(url + "?abaixo=1")
    html = resp.content.decode().lower()
    assert "luva a" in html and "luva b" not in html


@pytest.mark.django_db
def test_criar_requires_login_and_perm(client):
    url = reverse("app_epis:criar")
    # não logado -> redirect
    resp = client.get(url)
    assert resp.status_code in (302, 303)

    # logado sem perm -> 403
    u = User.objects.create_user("u1", password="x")
    client.force_login(u)
    assert client.get(url).status_code == 403


@pytest.mark.django_db
def test_criar_success_shows_message_and_stays_on_page(client):
    _login_with_perms(client, "add_epi")
    cat = CategoriaEPI.objects.create(nome="Luvas")
    url = reverse("app_epis:criar")
    resp = client.post(
        url,
        data={
            "nome": "Luva Neo",
            "codigo": "LUV-9",
            "categoria": cat.id,
            "tamanho": "",
            "ativo": "on",
            "estoque": 5,
            "estoque_minimo": 2,
        },
        follow=True,
    )
    assert resp.status_code == 200
    assert EPI.objects.filter(codigo="LUV-9").exists()
    assert "criado com sucesso" in resp.content.decode().lower()


@pytest.mark.django_db
def test_editar_success_message_and_redirects_to_same_page(client):
    _login_with_perms(client, "change_epi")
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=1)
    url = reverse("app_epis:editar", kwargs={"pk": epi.pk})
    resp = client.post(
        url,
        data={
            "nome": "Luva Editada",
            "codigo": "L1",
            "categoria": cat.id,
            "tamanho": "",
            "ativo": "on",
            "estoque": 3,
            "estoque_minimo": 1,
        },
        follow=True,
    )
    assert resp.status_code == 200
    epi.refresh_from_db()
    assert epi.nome == "Luva Editada"
    # nossa view mostra mensagem e permanece na tela de edição
    assert "atualizado com sucesso" in resp.content.decode().lower()


@pytest.mark.django_db
def test_excluir_success_message(client):
    _login_with_perms(client, "delete_epi")
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=1)
    url = reverse("app_epis:excluir", kwargs={"pk": epi.pk})
    resp = client.post(url, follow=True)
    assert resp.status_code == 200
    assert not EPI.objects.filter(pk=epi.pk).exists()
    assert "excluído com sucesso" in resp.content.decode().lower()


@pytest.mark.django_db
def test_excluir_protected_error_shows_error_message(monkeypatch, client):
    _login_with_perms(client, "delete_epi")
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=1)

    # força erro de proteção de FK (simula entregas associadas)
    def boom(*a, **k):
        raise ProtectedError("tem fk", [])

    monkeypatch.setattr(EPI, "delete", boom)

    url = reverse("app_epis:excluir", kwargs={"pk": epi.pk})
    resp = client.post(url, follow=True)
    assert resp.status_code == 200
    assert EPI.objects.filter(pk=epi.pk).exists()
    assert "não é possível excluir" in resp.content.decode().lower()
