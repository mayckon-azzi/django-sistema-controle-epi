import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_home_ok(client):
    url = reverse("home")  # 👉 troque para o nome real da sua rota (ex.: "dashboard")
    resp = client.get(url)
    assert resp.status_code == 200
