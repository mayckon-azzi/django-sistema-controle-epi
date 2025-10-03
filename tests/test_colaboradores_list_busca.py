# tests/test_colaboradores_list_busca.py
import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from app_colaboradores.models import Colaborador


@pytest.mark.django_db
def test_busca_colaborador_por_nome_filtra_resultados_corretamente(client):
    """
    Testa se a busca de colaboradores por nome filtra corretamente os resultados,
    mostrando apenas os colaboradores que correspondem ao critério pesquisado.
    """
    usuario = User.objects.create_user("viewer", password="x")
    usuario.user_permissions.add(Permission.objects.get(codename="view_colaborador"))
    client.force_login(usuario)

    Colaborador.objects.create(nome="Ana Clara", email="ana@x.com", matricula="A1")
    Colaborador.objects.create(nome="Bruno", email="bruno@x.com", matricula="B1")

    url = reverse("app_colaboradores:lista")
    resposta = client.get(url, {"q": "ana"})
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Ana Clara" in html
    assert "Bruno" not in html
