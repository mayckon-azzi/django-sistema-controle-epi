# tests/test_colaboradores_views_extra.py
from itertools import count

import pytest
from django.contrib.auth.models import Permission, User
from django.db import IntegrityError
from django.urls import reverse

from app_colaboradores.models import Colaborador

_seq = count(1)


def make_user_with_perms(*codenames, app_label="app_colaboradores"):
    suffix = next(_seq)
    base = "_".join(codenames) if codenames else "noperm"
    u = User.objects.create_user(f"u_{base}_{suffix}", password="x")
    if codenames:
        perms = Permission.objects.filter(codename__in=codenames, content_type__app_label=app_label)
        u.user_permissions.add(*perms)
    return u


# ----------------------- LoginView -----------------------


@pytest.mark.django_db
def test_login_respects_next_and_redirects_by_perms(client):
    u = make_user_with_perms()
    client.force_login(u)
    url = reverse("app_colaboradores:entrar") + "?next=" + reverse("app_relatorios:index")
    r = client.get(url, follow=False)
    assert r.status_code in (302, 303)
    assert r.headers["Location"].endswith(reverse("app_relatorios:index"))

    u = make_user_with_perms("view_colaborador")
    client.force_login(u)
    r = client.get(reverse("app_colaboradores:entrar"), follow=False)
    assert r.status_code in (302, 303)
    assert r.headers["Location"].endswith(reverse("app_colaboradores:lista"))

    u = make_user_with_perms("view_solicitacao", app_label="app_entregas")
    client.force_login(u)
    r = client.get(reverse("app_colaboradores:entrar"), follow=False)
    assert r.status_code in (302, 303)
    assert r.headers["Location"].endswith(reverse("app_entregas:lista"))

    u = make_user_with_perms()
    client.force_login(u)
    r = client.get(reverse("app_colaboradores:entrar"), follow=False)
    assert r.status_code in (302, 303)
    assert r.headers["Location"].endswith(reverse("app_core:home"))


# ----------------------- ListaColaboradoresView -----------------------


@pytest.mark.django_db
def test_lista_anonymous_redirects_to_login(client):
    r = client.get(reverse("app_colaboradores:lista"), follow=False)
    assert r.status_code in (302, 303)


@pytest.mark.django_db
def test_lista_no_perm_returns_403(client):
    u = make_user_with_perms()
    client.force_login(u)
    r = client.get(reverse("app_colaboradores:lista"))
    assert r.status_code == 403


@pytest.mark.django_db
def test_lista_deleted_message_and_base_query(client):
    u = make_user_with_perms("view_colaborador")
    client.force_login(u)

    for i in range(11):
        Colaborador.objects.create(nome=f"Bob #{i}", matricula=f"B{i}", email=f"b{i}@x.com")

    r = client.get(reverse("app_colaboradores:lista"), {"q": "Bob", "page": 2, "deleted": "1"})
    assert r.status_code == 200
    html = r.content.decode().lower()
    assert "colaborador" in html and ("desativado" in html or "excluído" in html)

    ctx = r.context[-1]
    assert "base_query" in ctx
    assert "page=" not in ctx["base_query"]
    assert "q=Bob".lower() in ctx["base_query"].lower()
    assert "deleted=1" in ctx["base_query"]


# ----------------------- Criar / Atualizar -----------------------


@pytest.mark.django_db
def test_criar_integrity_error_shows_message(monkeypatch, client):
    u = make_user_with_perms("add_colaborador", "view_colaborador")
    client.force_login(u)
    from app_colaboradores import views as v

    def boom_save(self, *a, **k):
        raise IntegrityError("dup")

    monkeypatch.setattr(v.ColaboradorAdminForm, "save", boom_save)

    r = client.post(
        reverse("app_colaboradores:criar"),
        data={"nome": "X", "email": "x@x.com", "matricula": "Z1"},
        follow=True,
    )
    assert r.status_code == 200
    assert "não foi possível criar" in r.content.decode().lower()


@pytest.mark.django_db
def test_atualizar_integrity_error_shows_message(monkeypatch, client):
    u = make_user_with_perms("change_colaborador", "view_colaborador")
    client.force_login(u)
    c = Colaborador.objects.create(nome="Y", email="y@x.com", matricula="Y1")
    from app_colaboradores import views as v

    def boom_save(self, *a, **k):
        raise IntegrityError("conflict")

    monkeypatch.setattr(v.ColaboradorAdminForm, "save", boom_save)

    r = client.post(
        reverse("app_colaboradores:editar", kwargs={"pk": c.pk}),
        data={"nome": "Y", "email": "y@x.com", "matricula": "Y1"},
        follow=True,
    )
    assert r.status_code == 200
    assert "não foi possível atualizar" in r.content.decode().lower()


# ----------------------- Excluir -----------------------


@pytest.mark.django_db
def test_excluir_appends_deleted_queryparam_and_list_shows_message(client):
    u = make_user_with_perms("delete_colaborador", "view_colaborador")
    client.force_login(u)
    c = Colaborador.objects.create(nome="Del", matricula="D1", email="d@x.com")
    r = client.post(reverse("app_colaboradores:excluir", kwargs={"pk": c.pk}), follow=True)
    assert r.redirect_chain
    final_url, _ = r.redirect_chain[-1]
    assert "deleted=1" in final_url
    assert "desativado" in r.content.decode().lower()
    assert Colaborador.objects.filter(pk=c.pk).exists()
    c.refresh_from_db()
    assert c.ativo is False


# ----------------------- registrar -----------------------


@pytest.mark.django_db
def test_registrar_success_creates_user_and_colab(client):
    r = client.post(
        reverse("app_colaboradores:registrar"),
        data={
            "username": "novo",
            "email": "novo@empresa.com",
            "password1": "Senha12345!",
            "password2": "Senha12345!",
            "nome": "Novo Usuário",
            "matricula": "N1",
        },
        follow=True,
    )
    assert r.status_code == 200
    assert "cadastro realizado com sucesso" in r.content.decode().lower()
    u = User.objects.get(username="novo")
    col = Colaborador.objects.get(email="novo@empresa.com")
    assert col.user == u


# ----------------------- PerfilView -----------------------


@pytest.mark.django_db
def test_perfil_autolinks_by_email_and_shows_info_message(client):
    u = User.objects.create_user("z", password="x", email="z@empresa.com")
    c = Colaborador.objects.create(nome="Z", email="z@empresa.com", matricula="Z1")
    assert c.user is None
    client.force_login(u)
    r = client.get(reverse("app_colaboradores:perfil"), follow=True)
    assert r.status_code == 200
    assert "vinculado automaticamente" in r.content.decode().lower()
    c.refresh_from_db()
    assert c.user == u


@pytest.mark.django_db
def test_perfil_missing_redirects_to_create_when_user_can_add(client):
    u = make_user_with_perms("add_colaborador")
    u.email = ""
    u.save(update_fields=["email"])
    client.force_login(u)

    r = client.get(reverse("app_colaboradores:perfil"), follow=True)
    assert r.redirect_chain
    final_url, _ = r.redirect_chain[-1]
    assert final_url.endswith(reverse("app_colaboradores:criar"))
    assert "crie seu perfil" in r.content.decode().lower()


@pytest.mark.django_db
def test_perfil_missing_redirects_home_when_no_perm(client):
    u = make_user_with_perms()
    u.email = ""
    u.save(update_fields=["email"])
    client.force_login(u)

    r = client.get(reverse("app_colaboradores:perfil"), follow=True)
    assert r.redirect_chain
    final_url, _ = r.redirect_chain[-1]
    assert final_url.endswith(reverse("app_core:home"))
    assert "não possui um perfil de colaborador" in r.content.decode().lower()


@pytest.mark.django_db
def test_perfil_pk_requires_view_perm_when_not_own(client):
    other = Colaborador.objects.create(nome="Outro", email="o@x.com", matricula="O1")
    u = make_user_with_perms()
    client.force_login(u)
    r = client.get(reverse("app_colaboradores:perfil_pk", kwargs={"pk": other.pk}))
    assert r.status_code == 403


@pytest.mark.django_db
def test_perfil_pk_allows_own_without_perm(client):
    u = make_user_with_perms()
    c = Colaborador.objects.create(nome="Self", email="s@x.com", matricula="S1", user=u)
    client.force_login(u)
    r = client.get(reverse("app_colaboradores:perfil_pk", kwargs={"pk": c.pk}))
    assert r.status_code == 200
    assert any("foto_form" in ctx for ctx in r.context)


@pytest.mark.django_db
def test_perfil_post_remove_photo_messages(client):
    u = make_user_with_perms()
    c = Colaborador.objects.create(nome="Pic", email="pic@x.com", matricula="P1", user=u)
    c.foto.name = "dummy.jpg"
    c.save(update_fields=["foto"])

    client.force_login(u)
    r = client.post(reverse("app_colaboradores:perfil"), data={"remover": "1"}, follow=True)
    assert r.status_code == 200
    c.refresh_from_db()
    assert not c.foto
    assert "foto removida com sucesso" in r.content.decode().lower()


@pytest.mark.django_db
def test_perfil_post_remove_photo_when_none_shows_info(client):
    u = make_user_with_perms()
    Colaborador.objects.create(nome="NoPic", email="n@x.com", matricula="N1", user=u)
    client.force_login(u)
    r = client.post(reverse("app_colaboradores:perfil"), data={"remover": "1"}, follow=True)
    assert "não possui foto" in r.content.decode().lower()


@pytest.mark.django_db
def test_perfil_post_update_foto_success_with_fake_form(monkeypatch, client):
    """
    Evita dependência de Pillow simulando um form válido.
    """
    u = make_user_with_perms()
    Colaborador.objects.create(nome="Pic2", email="p2@x.com", matricula="P2", user=u)
    client.force_login(u)

    class FakeFotoForm:
        def __init__(self, *a, **k):
            pass

        def is_valid(self):
            return True

        def save(self):
            return None

    from app_colaboradores import views as v

    monkeypatch.setattr(v, "ColaboradorFotoForm", FakeFotoForm)

    r = client.post(reverse("app_colaboradores:perfil"), data={}, follow=True)
    assert r.status_code == 200
    assert "foto atualizada com sucesso" in r.content.decode().lower()
