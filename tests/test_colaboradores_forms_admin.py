# tests/test_colaboradores_forms_admin.py
import pytest
from django.contrib.auth.models import Group, User

from app_colaboradores.forms import ColaboradorAdminForm
from app_colaboradores.models import Colaborador


@pytest.mark.django_db
def test_criar_colaborador_cria_usuario_e_grupos_quando_selecionado():
    """
    Testa se ao criar um colaborador pelo AdminForm com a opção de criar usuário marcada,
    o usuário e os grupos associados são criados corretamente.
    """
    grupo = Group.objects.create(name="almoxarife")
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
            "groups": [grupo.id],
        }
    )
    assert form.is_valid(), form.errors
    colaborador = form.save()
    assert colaborador.pk is not None
    assert colaborador.user is not None
    assert grupo in colaborador.user.groups.all()
    assert colaborador.user.is_active is True
    assert colaborador.user.email == "joao@empresa.com"


@pytest.mark.django_db
def test_adminform_atualiza_campos_usuario_existente_e_grupos():
    """
    Testa se o AdminForm atualiza corretamente os campos do usuário existente
    e os grupos associados ao salvar o formulário.
    """
    grupo = Group.objects.create(name="almoxarife")
    usuario = User.objects.create_user("maria", email="maria@x.com", password="x", is_active=True)
    colaborador = Colaborador.objects.create(
        nome="Maria", email="maria@x.com", matricula="M1", user=usuario, ativo=True
    )

    form = ColaboradorAdminForm(
        instance=colaborador,
        data={
            "nome": "Maria",
            "email": "novo@empresa.com",
            "matricula": "M1",
            "cargo": "",
            "setor": "",
            "telefone": "",
            "ativo": "",
            "groups": [grupo.id],
        },
    )
    assert form.is_valid(), form.errors
    colaborador = form.save()
    colaborador.refresh_from_db()
    usuario.refresh_from_db()
    assert usuario.email == "novo@empresa.com"
    assert usuario.is_active is False
    assert list(usuario.groups.all()) == [grupo]


@pytest.mark.django_db
def test_adminform_senha_invalida_gera_erro():
    """
    Testa se o AdminForm detecta quando as senhas fornecidas não correspondem
    e retorna erro de validação no campo password2.
    """
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
