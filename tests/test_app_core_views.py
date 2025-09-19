# tests/test_app_core_views.py
import pytest
from django.urls import reverse
pytestmark = pytest.mark.django_db


def test_home_ok(client):
    url = reverse("app_core:home")
    resp = client.get(url)
    assert resp.status_code == 200
    assert "app_core/pages/home.html" in [t.name for t in resp.templates]

    for key in [
        "total_colaboradores",
        "total_epis",
        "estoque_total",
        "entregas_ativas",
        "devolvidos_mes",
        "solicitacoes_pendentes",
    ]:
        assert key in resp.context


def test_teste_mensagens_redirect_and_messages(client):
    url = reverse("app_core:teste_mensagens")
    resp = client.get(url, follow=True)
    assert resp.redirect_chain
    msgs = list(resp.context["messages"])
    assert len(msgs) >= 1
