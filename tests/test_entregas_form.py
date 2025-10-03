# tests/test_entregas_form.py
from datetime import timedelta

import pytest
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.forms import EntregaForm, SolicitacaoForm
from app_entregas.models import Entrega
from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db
def test_formulario_entrega_requer_data_prevista_para_emprestado():
    """
    Testa se o formulário de Entrega exige a data prevista de devolução
    quando o status é EMPRESTADO e valida se a data é futura.
    """
    categoria = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=categoria, estoque=10)
    colaborador = Colaborador.objects.create(nome="A", email="a@x.com", matricula="A1", ativo=True)

    # Data prevista ausente
    form = EntregaForm(
        data={
            "colaborador": colaborador.pk,
            "epi": epi.pk,
            "quantidade": 1,
            "status": Entrega.Status.EMPRESTADO,
        }
    )
    assert not form.is_valid()
    assert "data_prevista_devolucao" in form.errors

    # Data prevista passada
    form = EntregaForm(
        data={
            "colaborador": colaborador.pk,
            "epi": epi.pk,
            "quantidade": 1,
            "status": Entrega.Status.EMPRESTADO,
            "data_prevista_devolucao": (timezone.now() - timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
        }
    )
    assert not form.is_valid()
    assert "data_prevista_devolucao" in form.errors

    # Data prevista futura
    form = EntregaForm(
        data={
            "colaborador": colaborador.pk,
            "epi": epi.pk,
            "quantidade": 1,
            "status": Entrega.Status.EMPRESTADO,
            "data_prevista_devolucao": (timezone.now() + timedelta(days=2)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
        }
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_formulario_entrega_requer_data_devolucao_para_status_final():
    """
    Testa se o formulário de Entrega exige a data de devolução
    quando o status é DEVOLVIDO.
    """
    categoria = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=categoria, estoque=10)
    colaborador = Colaborador.objects.create(nome="B", email="b@x.com", matricula="B1", ativo=True)

    form = EntregaForm(
        data={
            "colaborador": colaborador.pk,
            "epi": epi.pk,
            "quantidade": 1,
            "status": Entrega.Status.DEVOLVIDO,
            "data_prevista_devolucao": (timezone.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
        },
        instance=Entrega(pk=1),
    )
    assert not form.is_valid()
    assert "data_devolucao" in form.errors


@pytest.mark.django_db
def test_formulario_solicitacao_valida_regras_basicas():
    """
    Testa as regras básicas do formulário de Solicitação:
    - quantidade deve ser maior que zero
    - EPI deve estar ativo
    """
    categoria = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=categoria, estoque=10, ativo=True)

    # Quantidade inválida
    form = SolicitacaoForm(data={"epi": epi.pk, "quantidade": 0})
    assert not form.is_valid()
    assert "quantidade" in form.errors

    # EPI inativo
    epi.ativo = False
    epi.save()
    form = SolicitacaoForm(data={"epi": epi.pk, "quantidade": 1})
    assert not form.is_valid()
    assert "epi" in form.errors
