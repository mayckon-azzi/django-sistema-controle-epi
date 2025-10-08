# tests/test_entregas_services.py
from datetime import timezone

import pytest
from django.core.exceptions import ValidationError

from app_colaboradores.models import Colaborador
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

    entrega = Entrega(epi=epi, quantidade=3, status=Entrega.Status.EMPRESTADO)
    movimenta_por_entrega(entrega, antiga=None)
    epi.refresh_from_db()
    assert epi.estoque == 7

    antiga = Entrega(epi=epi, quantidade=3, status=Entrega.Status.EMPRESTADO)
    entrega2 = Entrega(epi=epi, quantidade=3, status=Entrega.Status.DEVOLVIDO)
    movimenta_por_entrega(entrega2, antiga=antiga)
    epi.refresh_from_db()
    assert epi.estoque == 10

    entrega3 = Entrega(epi=epi, quantidade=2, status=Entrega.Status.PERDIDO)
    movimenta_por_entrega(entrega3, antiga=None)
    epi.refresh_from_db()
    assert epi.estoque == 8

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


@pytest.mark.django_db
def test_movimenta_por_entrega_troca_de_epi_reverte_delta_no_antigo_e_aplica_no_novo():
    """
    Garante que, ao atualizar uma Entrega trocando o EPI (antiga.epi_id != nova.epi_id),
    o serviço:
      - reverte o delta antigo no EPI antigo (devolve o estoque consumido antes), e
      - aplica o delta novo no EPI novo (consome do novo EPI).

    Cenário:
      1) Criação de entrega EMPRESTADO (q=2) para EPI_A  -> estoque A diminui 2.
      2) Atualização para EMPRESTADO (q=2) em EPI_B  -> estoque A devolve 2; estoque B diminui 2.
    """

    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi_a = EPI.objects.create(codigo="L1", nome="Luva Nitrílica", categoria=cat, estoque=10)
    epi_b = EPI.objects.create(codigo="L2", nome="Luva Térmica", categoria=cat, estoque=20)
    col = Colaborador.objects.create(nome="Ana", email="ana@x.com", matricula="A1", ativo=True)

    antiga = Entrega.objects.create(
        colaborador=col,
        epi=epi_a,
        quantidade=2,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=timezone.now(),
    )

    movimenta_por_entrega(nova=antiga, antiga=None)
    epi_a.refresh_from_db()
    assert epi_a.estoque == 10 - 2

    nova = Entrega.objects.create(
        colaborador=col,
        epi=epi_b,
        quantidade=2,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=antiga.data_entrega,
    )

    movimenta_por_entrega(nova=nova, antiga=antiga)
    epi_a.refresh_from_db()
    epi_b.refresh_from_db()
    assert epi_a.estoque == 10
    assert epi_b.estoque == 20 - 2
