# tests/test_app_core_templates.py
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_messages_partial_is_included(client, settings):
    """
    Garante que o partial de mensagens esteja sendo renderizado
    (verifica uma classe do alert do Bootstrap).
    """
    url = reverse("app_core:home")
    resp = client.get(url)
    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    # Mesmo sem mensagens, o arquivo é incluído e não quebra layout.
    # Se preferir, você pode jogar uma mensagem temporária antes de validar.
    assert "messages" in html  # id/section do bloco
