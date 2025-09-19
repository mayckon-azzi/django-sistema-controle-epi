# tests/test_config_urls.py
import importlib
import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import Resolver404, clear_url_caches, resolve, reverse


def _reload_urls():
    """Recarrega o módulo de urls principal e limpa o cache do resolver."""
    import config.urls as urls_module

    importlib.reload(urls_module)
    clear_url_caches()
    return urls_module


@pytest.mark.django_db
def test_accounts_login_redirects_to_colaboradores_login(client):
    resp = client.get("/accounts/login/", follow=False)
    assert resp.status_code in (302, 303)
    assert resp.headers["Location"].endswith(reverse("app_colaboradores:entrar"))


def test_included_url_prefixes():
    assert reverse("app_colaboradores:lista").startswith("/colaboradores/")
    assert reverse("app_epis:lista").startswith("/epis/")
    assert reverse("app_entregas:lista").startswith("/entregas/")
    assert reverse("app_relatorios:index").startswith("/relatorios/")


def test_admin_login_page_accessible(client):
    resp = client.get("/admin/login/")
    assert resp.status_code == 200
    html = resp.content.decode().lower()
    assert "username" in html and "password" in html


def test_static_urlpatterns_toggle_with_debug():
    original_debug = settings.DEBUG

    with override_settings(DEBUG=True):
        _reload_urls() 
        path = f"{settings.MEDIA_URL.rstrip('/')}/test.txt"
        match = resolve(path)
        assert match is not None

    with override_settings(DEBUG=False):
        _reload_urls()  
        path = f"{settings.MEDIA_URL.rstrip('/')}/test.txt"
        with pytest.raises(Resolver404):
            resolve(path)

    with override_settings(DEBUG=original_debug):
        _reload_urls()
