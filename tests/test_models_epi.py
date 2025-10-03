# tests/test_models_epi.py
import pytest
from django.db import DataError, IntegrityError

from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db
def test_str_do_epi_retorna_nome_e_codigo():
    """
    Verifica se o método __str__ do modelo EPI retorna corretamente
    o nome do EPI seguido do código entre parênteses.
    """
    categoria = CategoriaEPI.objects.create(nome="Proteção Cabeça")
    epi = EPI.objects.create(codigo="CAP-001", nome="Capacete", categoria=categoria, estoque=10)
    s = str(epi)
    assert "Capacete" in s
    assert "CAP-001" in s


@pytest.mark.django_db
def test_constraint_estoque_epi_nao_negativo():
    """
    Verifica se o modelo EPI impede a criação de registros
    com estoque negativo, lançando exceções apropriadas.
    """
    categoria = CategoriaEPI.objects.create(nome="Mãos")
    with pytest.raises((IntegrityError, DataError, ValueError)):
        EPI.objects.create(codigo="LUV-001", nome="Luva Nitrílica", categoria=categoria, estoque=-1)
