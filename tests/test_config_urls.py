# tests/test_config_urls.py
import importlib

import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import Resolver404, clear_url_caches, resolve, reverse


def recarregar_urls():
    """
    Recarrega o módulo de URLs principal e limpa o cache do resolver.
    """
    import config.urls as urls_module

    importlib.reload(urls_module)
    clear_url_caches()
    return urls_module


@pytest.mark.django_db
def test_redirect_login_accounts_para_login_colaboradores(client):
    """
    Verifica se o acesso à URL '/accounts/login/' redireciona
    corretamente para a página de login de colaboradores.
    """
    resposta = client.get("/accounts/login/", follow=False)
    assert resposta.status_code in (302, 303)
    assert resposta.headers["Location"].endswith(reverse("app_colaboradores:entrar"))


def test_prefixos_urls_incluidas_sao_corretos():
    """
    Verifica se os prefixos das URLs incluídas em cada app estão corretos.
    """
    assert reverse("app_colaboradores:lista").startswith("/colaboradores/")
    assert reverse("app_epis:lista").startswith("/epis/")
    assert reverse("app_entregas:lista").startswith("/entregas/")
    assert reverse("app_relatorios:index").startswith("/relatorios/")


def test_pagina_login_admin_disponivel(client):
    """
    Verifica se a página de login do admin está acessível
    e contém campos de username e password.
    """
    resposta = client.get("/admin/login/")
    assert resposta.status_code == 200
    html = resposta.content.decode().lower()
    assert "username" in html and "password" in html


def test_toggle_static_urlpatterns_com_debug():
    """
    Testa se os padrões de URL estáticos funcionam corretamente
    quando DEBUG=True e geram Resolver404 quando DEBUG=False.
    """
    debug_original = settings.DEBUG

    with override_settings(DEBUG=True):
        recarregar_urls()
        caminho = f"{settings.MEDIA_URL.rstrip('/')}/test.txt"
        match = resolve(caminho)
        assert match is not None

    with override_settings(DEBUG=False):
        recarregar_urls()
        caminho = f"{settings.MEDIA_URL.rstrip('/')}/test.txt"
        with pytest.raises(Resolver404):
            resolve(caminho)

    with override_settings(DEBUG=debug_original):
        recarregar_urls()
