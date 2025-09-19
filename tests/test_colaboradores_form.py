# tests/test_colaboradores_form.py
import pytest
from app_colaboradores.forms import ColaboradorForm
from app_colaboradores.models import Colaborador


@pytest.mark.django_db
def test_matricula_unica():
    Colaborador.objects.create(nome="X", matricula="ABC")
    form = ColaboradorForm(
        data={
            "nome": "Y",
            "matricula": "ABC",
            "email": "",
            "funcao": "",
            "setor": "",
            "telefone": "",
            "ativo": "on",
        }
    )
    assert not form.is_valid()
    assert "matrícula" in str(form.errors.get("matricula", "[]")).lower()
