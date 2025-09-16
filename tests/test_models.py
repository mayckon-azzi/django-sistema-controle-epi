import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_user_creation():
    User = get_user_model()
    u = User.objects.create_user(username="jo", password="x")
    assert u.pk is not None
