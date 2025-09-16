# tests/test_app_core_views.py
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_home_ok(client):
    url = reverse("app_core:home")
    resp = client.get(url)
    assert resp.status_code == 200
    assert "app_core/pages/home.html" in [t.name for t in resp.templates]

    # Contexto essencial existe (pode ser zero em banco vazio)
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

    # Redireciona para home
    assert resp.redirect_chain
    # Ao menos uma mensagem foi adicionada
    msgs = list(resp.context["messages"])
    assert len(msgs) >= 1
