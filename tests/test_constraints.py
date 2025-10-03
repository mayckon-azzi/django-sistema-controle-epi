# tests/test_constraints.py
import pytest
from django.db import IntegrityError

from app_epis.models import EPI


@pytest.mark.django_db
def test_estoque_epi_nao_pode_ser_negativo():
    """
    Verifica se o modelo EPI impede que o estoque seja negativo,
    lançando IntegrityError caso seja tentada a criação com valor inválido.
    """
    with pytest.raises(IntegrityError):
        EPI.objects.create(nome="Luva", estoque=-1)
