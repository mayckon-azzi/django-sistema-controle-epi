import pytest
from django.db import DataError, IntegrityError

from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db
def test_epi_str():
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="LUV-1", nome="Luva Nitrílica", categoria=cat, estoque=0)
    assert str(epi) == "Luva Nitrílica (LUV-1)"


@pytest.mark.django_db
def test_non_negative_constraints():
    cat = CategoriaEPI.objects.create(nome="Capacete")

    # Estoque negativo deve falhar (DataError em MySQL, IntegrityError em SQLite, etc.)
    with pytest.raises((IntegrityError, DataError, ValueError)):
        EPI.objects.create(codigo="X-1", nome="X", categoria=cat, estoque=-1)

    # Estoque mínimo negativo também deve falhar (pela nova constraint)
    with pytest.raises((IntegrityError, DataError, ValueError)):
        EPI.objects.create(codigo="X-2", nome="X", categoria=cat, estoque=0, estoque_minimo=-1)
