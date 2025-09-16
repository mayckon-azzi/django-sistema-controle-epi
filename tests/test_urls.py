from django.urls import reverse


def test_urls():
    assert reverse("app_core:home")
    assert reverse("app_colaboradores:lista")  # ajuste para um name real seu
