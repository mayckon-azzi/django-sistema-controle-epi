# tests/test_entregas_forms.py
from datetime import timedelta

import pytest
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.forms import EntregaForm, SolicitacaoForm
from app_entregas.models import Entrega
from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db
def test_entrega_form_requires_future_prevista_and_prevista_when_emprestado():
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=10)
    col = Colaborador.objects.create(nome="A", email="a@x.com", matricula="A1", ativo=True)

    form = EntregaForm(
        data={
            "colaborador": col.pk,
            "epi": epi.pk,
            "quantidade": 1,
            "status": Entrega.Status.EMPRESTADO,
        }
    )
    assert not form.is_valid()
    assert "data_prevista_devolucao" in form.errors

    form = EntregaForm(
        data={
            "colaborador": col.pk,
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

    form = EntregaForm(
        data={
            "colaborador": col.pk,
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
def test_entrega_form_requires_devolucao_when_final_status():
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=10)
    col = Colaborador.objects.create(nome="B", email="b@x.com", matricula="B1", ativo=True)

    form = EntregaForm(
        data={
            "colaborador": col.pk,
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
def test_solicitacao_form_basic_rules():
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=10, ativo=True)

    form = SolicitacaoForm(data={"epi": epi.pk, "quantidade": 0})
    assert not form.is_valid()
    assert "quantidade" in form.errors

    epi.ativo = False
    epi.save()
    form = SolicitacaoForm(data={"epi": epi.pk, "quantidade": 1})
    assert not form.is_valid()
    assert "epi" in form.errors
