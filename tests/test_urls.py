# tests/test_urls.py
from django.urls import reverse


def test_urls():
    assert reverse("app_core:home")
    assert reverse("app_colaboradores:lista")
