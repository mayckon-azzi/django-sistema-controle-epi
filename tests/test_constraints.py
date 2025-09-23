import pytest
from django.db import IntegrityError

from app_epis.models import EPI


@pytest.mark.django_db
def test_epi_estoque_nao_negativo():
    with pytest.raises(IntegrityError):
        EPI.objects.create(nome="Luva", estoque=-1)
