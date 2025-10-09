# tests/test_epis_forms.py
import pytest

from app_epis.forms import DEFAULT_CATEGORIAS, EPIForm
from app_epis.models import CategoriaEPI


@pytest.mark.django_db
def test_formulario_epi_cria_categorias_padrao_e_classes_bootstrap():
    """
    Verifica se o formulário EPI cria categorias padrão quando não existem
    e se os campos possuem as classes CSS corretas do Bootstrap.
    """
    CategoriaEPI.objects.all().delete()
    form = EPIForm()
    for nome in DEFAULT_CATEGORIAS:
        assert CategoriaEPI.objects.filter(nome=nome).exists()

    assert "form-control" in form.fields["nome"].widget.attrs.get("class", "")
    assert "form-select" in form.fields["tamanho"].widget.attrs.get("class", "")
    assert "form-check-input" in form.fields["ativo"].widget.attrs.get("class", "")


@pytest.mark.django_db
def test_formulario_epi_rejeita_valores_negativos():
    """
    Testa se o formulário EPI valida corretamente valores negativos
    nos campos 'estoque' e 'estoque_minimo'.
    """
    cat = CategoriaEPI.objects.create(nome="Luvas")

    dados = {
        "nome": "Luva X",
        "codigo": "LUV-1",
        "categoria": cat.id,
        "tamanho": "",
        "ativo": "on",
        "estoque": -1,
        "estoque_minimo": 0,
    }
    form = EPIForm(data=dados)
    assert not form.is_valid()
    assert "estoque" in form.errors

    dados2 = dados | {"codigo": "LUV-2", "estoque": 1, "estoque_minimo": -5}
    form2 = EPIForm(data=dados2)
    assert not form2.is_valid()
    assert "estoque_minimo" in form2.errors
