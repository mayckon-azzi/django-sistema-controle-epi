# tests/test_urls.py
from django.urls import reverse


def test_resolucao_urls_basicas():
    """
    Testa se as URLs principais do sistema estão corretamente resolvidas.
    """
    assert reverse("app_core:home")
    assert reverse("app_colaboradores:lista")
    assert reverse("app_epis:lista")
    assert reverse("app_entregas:lista")
    assert reverse("app_relatorios:index")
