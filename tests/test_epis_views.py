# tests/test_epis_views.py
import pytest
from django.contrib.auth.models import Permission, User
from django.db.models.deletion import ProtectedError
from django.urls import reverse

from app_epis.models import EPI, CategoriaEPI


def login_com_permissoes(client, *codenames):
    """
    Cria um usuário com permissões específicas e realiza login.
    """
    usuario = User.objects.create_user("usuario_test", password="x")
    permissoes = Permission.objects.filter(codename__in=codenames)
    usuario.user_permissions.add(*permissoes)
    client.force_login(usuario)
    return usuario


@pytest.mark.django_db
def test_lista_epi_filtra_por_nome_categoria_ativos_e_estoque(client):
    """
    Testa a lista de EPIs filtrando por nome, categoria,
    ativos e quantidade abaixo do estoque mínimo.
    """
    cat1 = CategoriaEPI.objects.create(nome="Luvas")
    cat2 = CategoriaEPI.objects.create(nome="Capacete")
    EPI.objects.create(codigo="L1", nome="Luva A", categoria=cat1, estoque=2, estoque_minimo=5)
    EPI.objects.create(codigo="L2", nome="Luva B", categoria=cat1, estoque=10, estoque_minimo=5)
    EPI.objects.create(
        codigo="C1", nome="Capacete", categoria=cat2, estoque=0, estoque_minimo=0, ativo=False
    )

    url = reverse("app_epis:lista")

    resp = client.get(url)
    html = resp.content.decode().lower()
    assert "luva a" in html and "luva b" in html and "capacete" in html

    resp = client.get(url + "?q=luva")
    html = resp.content.decode().lower()
    assert "luva a" in html and "luva b" in html and "capacete" not in html

    resp = client.get(url + f"?categoria={cat2.id}")
    html = resp.content.decode().lower()
    assert "capacete" in html and "luva a" not in html

    resp = client.get(url + "?ativos=1")
    html = resp.content.decode().lower()
    assert "capacete" not in html

    resp = client.get(url + "?abaixo=1")
    html = resp.content.decode().lower()
    assert "luva a" in html and "luva b" not in html


@pytest.mark.django_db
def test_criar_epi_requer_login_e_permissao(client):
    """
    Verifica se a página de criação de EPI exige login e permissões,
    retornando 302 para anônimos e 403 para usuários sem permissão.
    """
    url = reverse("app_epis:criar")

    resp = client.get(url)
    assert resp.status_code in (302, 303)

    usuario = User.objects.create_user("u1", password="x")
    client.force_login(usuario)
    assert client.get(url).status_code == 403


@pytest.mark.django_db
def test_criar_epi_sucesso_exibe_mensagem(client):
    """
    Testa a criação de um EPI com sucesso e exibe mensagem de confirmação.
    """
    login_com_permissoes(client, "add_epi")
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
def test_editar_epi_sucesso_exibe_mensagem(client):
    """
    Testa a edição de um EPI e verifica se a mensagem de sucesso é exibida.
    """
    login_com_permissoes(client, "change_epi")
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
    assert "atualizado com sucesso" in resp.content.decode().lower()


@pytest.mark.django_db
def test_excluir_epi_sucesso_exibe_mensagem(client):
    """
    Testa a exclusão de um EPI e verifica se a mensagem de sucesso é exibida.
    """
    login_com_permissoes(client, "delete_epi")
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=1)

    url = reverse("app_epis:excluir", kwargs={"pk": epi.pk})
    resp = client.post(url, follow=True)
    assert resp.status_code == 200
    assert not EPI.objects.filter(pk=epi.pk).exists()
    assert "excluído com sucesso" in resp.content.decode().lower()


@pytest.mark.django_db
def test_excluir_epi_protected_error_exibe_mensagem_erro(monkeypatch, client):
    """
    Testa se ao tentar excluir um EPI protegido por FK é exibida a mensagem de erro
    e o objeto não é excluído.
    """
    login_com_permissoes(client, "delete_epi")
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=1)

    def boom(*a, **k):
        raise ProtectedError("tem fk", [])

    monkeypatch.setattr(EPI, "delete", boom)
    url = reverse("app_epis:excluir", kwargs={"pk": epi.pk})
    resp = client.post(url, follow=True)
    assert resp.status_code == 200
    assert EPI.objects.filter(pk=epi.pk).exists()
    assert "não é possível excluir" in resp.content.decode().lower()
