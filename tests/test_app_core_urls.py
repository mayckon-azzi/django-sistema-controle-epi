# tests/test_app_core_urls.py
import pytest
from django.urls import resolve, reverse

pytestmark = pytest.mark.django_db


def test_app_core_home_url_resolves():
    url = reverse("app_core:home")
    match = resolve(url)
    assert match.view_name == "app_core:home"


def test_app_core_teste_mensagens_url_resolves():
    url = reverse("app_core:teste_mensagens")
    match = resolve(url)
    assert match.view_name == "app_core:teste_mensagens"
