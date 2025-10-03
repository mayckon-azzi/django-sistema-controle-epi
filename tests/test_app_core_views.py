# tests/test_app_core_views.py
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_pagina_inicial_carrega_corretamente_com_contexto(client):
    """
    Verifica se a página inicial carrega corretamente, incluindo o template correto
    e todas as variáveis de contexto esperadas.
    """
    url = reverse("app_core:home")
    resposta = client.get(url)
    assert resposta.status_code == 200
    assert "app_core/pages/home.html" in [t.name for t in resposta.templates]

    chaves_esperadas = [
        "total_colaboradores",
        "total_epis",
        "estoque_total",
        "entregas_ativas",
        "devolvidos_mes",
        "solicitacoes_pendentes",
    ]
    for chave in chaves_esperadas:
        assert chave in resposta.context


def test_redirecionamento_teste_mensagens_exibe_alertas(client):
    """
    Verifica se a view de teste de mensagens redireciona corretamente
    e se pelo menos uma mensagem de alerta é adicionada no contexto.
    """
    url = reverse("app_core:teste_mensagens")
    resposta = client.get(url, follow=True)
    assert resposta.redirect_chain
    mensagens = list(resposta.context["messages"])
    assert len(mensagens) >= 1
