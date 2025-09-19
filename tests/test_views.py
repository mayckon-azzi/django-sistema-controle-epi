# tests/test_views.py
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_ok(client):
    url = reverse("app_core:home")
    resp = client.get(url)
    assert resp.status_code == 200
