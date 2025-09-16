import pytest

from app_epis.forms import DEFAULT_CATEGORIAS, EPIForm
from app_epis.models import CategoriaEPI


@pytest.mark.django_db
def test_epi_form_creates_default_categories_and_bootstrap_classes():
    # limpa e força _ensure_default_categories ser chamado
    CategoriaEPI.objects.all().delete()
    form = EPIForm()
    for nome in DEFAULT_CATEGORIAS:
        assert CategoriaEPI.objects.filter(nome=nome).exists()

    # smoke: widgets recebem classes bootstrap (sem depender do HTML)
    assert "form-control" in form.fields["nome"].widget.attrs.get("class", "")
    assert "form-select" in form.fields["tamanho"].widget.attrs.get("class", "")
    assert "form-check-input" in form.fields["ativo"].widget.attrs.get("class", "")


@pytest.mark.django_db
def test_epi_form_rejects_negative_values():
    cat = CategoriaEPI.objects.create(nome="Luvas")
    data = {
        "nome": "Luva X",
        "codigo": "LUV-1",
        "categoria": cat.id,
        "tamanho": "",
        "ativo": "on",
        "estoque": -1,
        "estoque_minimo": 0,
    }
    form = EPIForm(data=data)
    assert not form.is_valid()
    assert "estoque" in form.errors

    data2 = data | {"codigo": "LUV-2", "estoque": 1, "estoque_minimo": -5}
    form2 = EPIForm(data=data2)
    assert not form2.is_valid()
    assert "estoque_minimo" in form2.errors
