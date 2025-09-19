# tests/test_colaboradores_perfil_autolink.py
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from app_colaboradores.models import Colaborador


@pytest.mark.django_db
def test_perfil_autolinka_por_email_quando_possivel(client):
    Colaborador.objects.create(nome="Ana", email="ana@empresa.com", matricula="A1", user=None)
    u = User.objects.create_user("ana", email="ana@empresa.com", password="x")
    client.force_login(u)

    url = reverse("app_colaboradores:perfil")
    resp = client.get(url)
    assert resp.status_code == 200

    c = Colaborador.objects.get(matricula="A1")
    c.refresh_from_db()
    assert c.user == u 
