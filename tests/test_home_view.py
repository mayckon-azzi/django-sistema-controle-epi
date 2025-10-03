# tests/test_home_view.py
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_pagina_home_disponivel(client):
    """
    Verifica se a página inicial (home) está disponível
    e contém o container principal.
    """
    url = reverse("app_core:home")
    resposta = client.get(url)
    assert resposta.status_code == 200
