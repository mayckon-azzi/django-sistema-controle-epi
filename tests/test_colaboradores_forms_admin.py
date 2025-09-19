# tests/test_colaboradores_forms_admin.py
import pytest
from django.contrib.auth.models import Group, User
from app_colaboradores.forms import ColaboradorAdminForm
from app_colaboradores.models import Colaborador


@pytest.mark.django_db
def test_adminform_creates_user_and_groups_when_checked():
    g = Group.objects.create(name="almoxarife")
    form = ColaboradorAdminForm(
        data={
            "nome": "João da Silva",
            "email": "joao@empresa.com",
            "matricula": "C123",
            "cargo": "",
            "setor": "",
            "telefone": "",
            "ativo": "on",
            "criar_usuario": "on",
            "groups": [g.id],
        }
    )
    assert form.is_valid(), form.errors
    colab = form.save()
    assert colab.pk is not None
    assert colab.user is not None
    assert g in colab.user.groups.all()
    assert colab.user.is_active is True
    assert colab.user.email == "joao@empresa.com"


@pytest.mark.django_db
def test_adminform_updates_existing_user_fields_and_groups():
    g = Group.objects.create(name="almoxarife")
    u = User.objects.create_user("maria", email="maria@x.com", password="x", is_active=True)
    c = Colaborador.objects.create(
        nome="Maria", email="maria@x.com", matricula="M1", user=u, ativo=True
    )

    form = ColaboradorAdminForm(
        instance=c,
        data={
            "nome": "Maria",
            "email": "novo@empresa.com",
            "matricula": "M1",
            "cargo": "",
            "setor": "",
            "telefone": "",
            "ativo": "",  
            "groups": [g.id],
        },
    )
    assert form.is_valid(), form.errors
    colab = form.save()
    colab.refresh_from_db()
    u.refresh_from_db()
    assert u.email == "novo@empresa.com"
    assert u.is_active is False
    assert list(u.groups.all()) == [g]


@pytest.mark.django_db
def test_adminform_clean_password_mismatch_raises_error():
    form = ColaboradorAdminForm(
        data={
            "nome": "Teste",
            "email": "t@x.com",
            "matricula": "T1",
            "cargo": "",
            "setor": "",
            "telefone": "",
            "ativo": "on",
            "criar_usuario": "on",
            "username": "teste",
            "password1": "a",
            "password2": "b", 
        }
    )
    assert not form.is_valid()
    assert "password2" in form.errors
