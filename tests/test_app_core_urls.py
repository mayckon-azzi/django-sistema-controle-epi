# tests/test_app_core_urls.py
import pytest
from django.urls import resolve, reverse

pytestmark = pytest.mark.django_db


def test_url_pagina_inicial_corresponde_a_view():
    """
    Verifica se a URL da página inicial (home) está corretamente ligada à view app_core:home
    """
    url = reverse("app_core:home")
    correspondencia = resolve(url)
    assert correspondencia.view_name == "app_core:home"


def test_url_teste_mensagens_corresponde_a_view():
    """
    Verifica se a URL de teste de mensagens está corretamente ligada à view app_core:teste_mensagens
    """
    url = reverse("app_core:teste_mensagens")
    correspondencia = resolve(url)
    assert correspondencia.view_name == "app_core:teste_mensagens"
