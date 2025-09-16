import pytest
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from app_colaboradores.models import Colaborador

@pytest.mark.django_db
def test_busca_por_nome_filtra_resultados(client):
    # user com permissão
    u = User.objects.create_user("viewer", password="x")
    u.user_permissions.add(Permission.objects.get(codename="view_colaborador"))
    client.force_login(u)

    Colaborador.objects.create(nome="Ana Clara", email="ana@x.com", matricula="A1")
    Colaborador.objects.create(nome="Bruno", email="bruno@x.com", matricula="B1")

    url = reverse("app_colaboradores:lista")
    resp = client.get(url, {"q": "ana"})
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Ana Clara" in html
    assert "Bruno" not in html
