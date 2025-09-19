# tests/test_models_epi.py
import pytest
from django.db import DataError, IntegrityError 
from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db
def test_epi_str():
    cat = CategoriaEPI.objects.create(nome="Proteção Cabeça")
    epi = EPI.objects.create(codigo="CAP-001", nome="Capacete", categoria=cat, estoque=10)
    s = str(epi)
    assert "Capacete" in s
    assert "CAP-001" in s


@pytest.mark.django_db
def test_epi_estoque_nao_negativo_constraint():
    cat = CategoriaEPI.objects.create(nome="Mãos")
    with pytest.raises((IntegrityError, DataError)):
        EPI.objects.create(
            codigo="LUV-001",
            nome="Luva Nitrílica",
            categoria=cat,
            estoque=-1, 
        )
