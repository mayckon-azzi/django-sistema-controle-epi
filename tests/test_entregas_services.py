# tests/test_entregas_services.py
import pytest
from django.core.exceptions import ValidationError

from app_entregas.models import Entrega
from app_entregas.services import movimenta_por_entrega, movimenta_por_exclusao
from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db
def test_movimenta_epi_por_entrega_create_update_e_delete():
    """
    Testa se a função movimenta_por_entrega ajusta corretamente o estoque
    ao criar, atualizar e excluir uma entrega.
    """
    categoria = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(
        codigo="L1", nome="Luva", categoria=categoria, estoque=10, estoque_minimo=0
    )

    # Criar entrega EMPRESTADO
    entrega = Entrega(epi=epi, quantidade=3, status=Entrega.Status.EMPRESTADO)
    movimenta_por_entrega(entrega, antiga=None)
    epi.refresh_from_db()
    assert epi.estoque == 7

    # Atualizar entrega para DEVOLVIDO
    antiga = Entrega(epi=epi, quantidade=3, status=Entrega.Status.EMPRESTADO)
    entrega2 = Entrega(epi=epi, quantidade=3, status=Entrega.Status.DEVOLVIDO)
    movimenta_por_entrega(entrega2, antiga=antiga)
    epi.refresh_from_db()
    assert epi.estoque == 10

    # Criar entrega PERDIDO
    entrega3 = Entrega(epi=epi, quantidade=2, status=Entrega.Status.PERDIDO)
    movimenta_por_entrega(entrega3, antiga=None)
    epi.refresh_from_db()
    assert epi.estoque == 8

    # Exclusão da entrega
    movimenta_por_exclusao(entrega3)
    epi.refresh_from_db()
    assert epi.estoque == 10


@pytest.mark.django_db
def test_movimenta_epi_gera_erro_quando_estoque_insuficiente():
    """
    Testa se movimenta_por_entrega lança ValidationError
    quando a quantidade solicitada excede o estoque disponível.
    """
    categoria = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(
        codigo="C1", nome="Capacete", categoria=categoria, estoque=2, estoque_minimo=0
    )

    entrega = Entrega(epi=epi, quantidade=5, status=Entrega.Status.EMPRESTADO)
    with pytest.raises(ValidationError):
        movimenta_por_entrega(entrega, antiga=None)
