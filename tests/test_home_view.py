import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_ok(client):
    resp = client.get(reverse("app_core:home"))
    assert resp.status_code == 200
    assert b"<html" in resp.content.lower()
