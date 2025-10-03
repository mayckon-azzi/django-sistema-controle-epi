# tests/test_views.py
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_pagina_home_disponivel(client):
    """
    Verifica se a página inicial (home) está disponível
    e retorna status HTTP 200.
    """
    url = reverse("app_core:home")
    resposta = client.get(url)
    assert resposta.status_code == 200
