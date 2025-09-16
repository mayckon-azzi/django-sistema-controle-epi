import pytest
from django.contrib.auth.models import User, Permission
from django.urls import reverse

@pytest.mark.django_db
def test_lista_requires_login(client):
    url = reverse("app_colaboradores:lista")
    resp = client.get(url)
    assert resp.status_code == 302
    assert reverse("app_colaboradores:entrar") in resp.url

@pytest.mark.django_db
def test_lista_requires_permission_403(client):
    u = User.objects.create_user("sem_permissao", password="x")
    client.force_login(u)
    url = reverse("app_colaboradores:lista")
    resp = client.get(url)
    assert resp.status_code == 403  # PermissionRequiredMixin + raise_exception=True

@pytest.mark.django_db
def test_lista_with_permission_ok(client):
    u = User.objects.create_user("com_permissao", password="x")
    perm = Permission.objects.get(codename="view_colaborador")
    u.user_permissions.add(perm)
    client.force_login(u)
    url = reverse("app_colaboradores:lista")
    resp = client.get(url)
    assert resp.status_code == 200
