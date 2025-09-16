import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from app_colaboradores.models import Colaborador


@pytest.mark.django_db
def test_delete_colaborador_shows_message_and_removes(client):
    u = User.objects.create_user("adm", password="x")
    u.user_permissions.add(
        Permission.objects.get(codename="view_colaborador"),
        Permission.objects.get(codename="delete_colaborador"),
    )
    client.force_login(u)

    c = Colaborador.objects.create(nome="Apagar", email="a@x.com", matricula="D1")
    url = reverse("app_colaboradores:excluir", kwargs={"pk": c.pk})
    resp = client.post(url, follow=True)
    assert resp.status_code == 200
    assert not Colaborador.objects.filter(pk=c.pk).exists()
    assert "excluído" in resp.content.decode().lower()
