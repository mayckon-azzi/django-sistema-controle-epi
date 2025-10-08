# tests/test_colaboradores_excluir_fluxos_completos.py
import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from app_colaboradores.models import Colaborador


def _user_with(*perms):
    u = User.objects.create_user("adm", password="x")
    for cod in perms:
        u.user_permissions.add(Permission.objects.get(codename=cod))
    return u


@pytest.mark.django_db
def test_excluir_colaborador_get_renderiza_confirmacao(client):
    """
    Acessa o GET de exclusão e garante render do template de confirmação com o objeto no contexto.
    """
    u = _user_with("delete_colaborador", "view_colaborador")
    client.force_login(u)
    c = Colaborador.objects.create(nome="Z", matricula="Z1", email="z@x.com", ativo=True)
    r = client.get(reverse("app_colaboradores:excluir", kwargs={"pk": c.pk}))
    assert r.status_code == 200
    assert r.context["object"].pk == c.pk


@pytest.mark.django_db
def test_excluir_colaborador_ja_inativo_mostra_mensagem_info(client):
    """
    Ao tentar desativar quem já está inativo, deve apenas informar e redirecionar sem alterações.
    """
    u = _user_with("delete_colaborador", "view_colaborador")
    client.force_login(u)
    c = Colaborador.objects.create(nome="Y", matricula="Y1", email="y@x.com", ativo=False)

    r = client.post(reverse("app_colaboradores:excluir", kwargs={"pk": c.pk}), follow=True)
    assert r.status_code == 200
    c.refresh_from_db()
    assert c.ativo is False
    msgs = [m.message.lower() for m in list(r.context["messages"])]
    assert any("já está desativado" in m for m in msgs)
