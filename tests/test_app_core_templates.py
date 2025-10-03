# tests/test_app_core_templates.py
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_inclusao_parcial_de_mensagens_na_pagina_inicial(client, settings):
    """
    Verifica se o partial de mensagens está sendo corretamente incluído na página inicial,
    conferindo se a classe de alert do Bootstrap aparece no HTML.
    """
    url = reverse("app_core:home")
    resposta = client.get(url)
    assert resposta.status_code == 200
    html = resposta.content.decode("utf-8")
    assert "messages" in html
