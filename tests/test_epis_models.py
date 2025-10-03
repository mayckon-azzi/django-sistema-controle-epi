# tests/test_epis_models.py
import pytest
from django.db import DataError, IntegrityError

from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db
def test_str_do_epi_retorna_nome_e_codigo():
    """
    Verifica se o método __str__ do modelo EPI retorna corretamente
    o nome do EPI seguido do código entre parênteses.
    """
    categoria = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="LUV-1", nome="Luva Nitrílica", categoria=categoria, estoque=0)
    assert str(epi) == "Luva Nitrílica (LUV-1)"


@pytest.mark.django_db
def test_constraints_de_valores_nao_negativos_do_epi():
    """
    Verifica se o modelo EPI impede a criação de registros
    com estoque ou estoque mínimo negativos, lançando exceções apropriadas.
    """
    categoria = CategoriaEPI.objects.create(nome="Capacete")

    # Estoque negativo
    with pytest.raises((IntegrityError, DataError, ValueError)):
        EPI.objects.create(codigo="X-1", nome="X", categoria=categoria, estoque=-1)

    # Estoque mínimo negativo
    with pytest.raises((IntegrityError, DataError, ValueError)):
        EPI.objects.create(
            codigo="X-2", nome="X", categoria=categoria, estoque=0, estoque_minimo=-1
        )
