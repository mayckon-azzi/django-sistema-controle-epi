# tests/test_colaboradores_delete.py
import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from app_colaboradores.models import Colaborador


def criar_usuario_com_permissao(*codenames):
    """
    Cria um usuário de teste com permissões específicas.
    """
    usuario = User.objects.create_user("adm_test", password="x")
    permissoes = Permission.objects.filter(
        codename__in=codenames, content_type__app_label="app_colaboradores"
    )
    usuario.user_permissions.add(*permissoes)
    usuario.is_staff = True
    usuario.is_superuser = False
    usuario.save()
    return usuario


@pytest.mark.django_db
def test_excluir_colaborador_exibe_mensagem_e_desativa_soft(client):
    """
    Testa a exclusão de um colaborador, verificando se ele é desativado (soft delete)
    e se a mensagem de confirmação aparece corretamente no HTML.
    """
    usuario = criar_usuario_com_permissao("view_colaborador", "delete_colaborador")
    client.force_login(usuario)

    colaborador = Colaborador.objects.create(nome="Apagar", email="a@x.com", matricula="D1")
    url = reverse("app_colaboradores:excluir", kwargs={"pk": colaborador.pk})

    resposta = client.post(url, follow=True)

    assert resposta.status_code == 200
    assert Colaborador.objects.filter(pk=colaborador.pk).exists()
    colaborador.refresh_from_db()
    assert colaborador.ativo is False
    assert "desativado" in resposta.content.decode().lower()
