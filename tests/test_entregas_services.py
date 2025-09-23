# tests/test_entregas_services.py
import pytest
from django.core.exceptions import ValidationError

from app_entregas.models import Entrega
from app_entregas.services import movimenta_por_entrega, movimenta_por_exclusao
from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db
def test_movimenta_por_entrega_create_and_update_and_delete():
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=10, estoque_minimo=0)

    e = Entrega(epi=epi, quantidade=3, status=Entrega.Status.EMPRESTADO)
    movimenta_por_entrega(e, antiga=None)
    epi.refresh_from_db()
    assert epi.estoque == 7

    antiga = Entrega(epi=epi, quantidade=3, status=Entrega.Status.EMPRESTADO)
    e2 = Entrega(epi=epi, quantidade=3, status=Entrega.Status.DEVOLVIDO)
    movimenta_por_entrega(e2, antiga=antiga)
    epi.refresh_from_db()
    assert epi.estoque == 10

    e3 = Entrega(epi=epi, quantidade=2, status=Entrega.Status.PERDIDO)
    movimenta_por_entrega(e3, antiga=None)
    epi.refresh_from_db()
    assert epi.estoque == 8
    movimenta_por_exclusao(e3)
    epi.refresh_from_db()
    assert epi.estoque == 10


@pytest.mark.django_db
def test_movimenta_por_entrega_insuficiente():
    cat = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(
        codigo="C1", nome="Capacete", categoria=cat, estoque=2, estoque_minimo=0
    )
    e = Entrega(epi=epi, quantidade=5, status=Entrega.Status.EMPRESTADO)
    with pytest.raises(ValidationError):
        movimenta_por_entrega(e, antiga=None)
