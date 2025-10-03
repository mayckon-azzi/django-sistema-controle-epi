# tests/test_colaboradores_perfil_autolink.py
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from app_colaboradores.models import Colaborador


@pytest.mark.django_db
def test_perfil_colaborador_vincula_usuario_por_email_automaticamente(client):
    """
    Testa se o perfil do colaborador é vinculado automaticamente
    ao usuário quando o email do usuário corresponde ao email do colaborador.
    """
    # Criação do colaborador sem usuário associado
    colaborador = Colaborador.objects.create(
        nome="Ana", email="ana@empresa.com", matricula="A1", user=None
    )

    # Criação do usuário correspondente
    usuario = User.objects.create_user("ana", email="ana@empresa.com", password="x")
    client.force_login(usuario)

    # Acessa a página de perfil
    url = reverse("app_colaboradores:perfil")
    resposta = client.get(url)
    assert resposta.status_code == 200

    # Verifica se o usuário foi vinculado automaticamente ao colaborador
    colaborador.refresh_from_db()
    assert colaborador.user == usuario
