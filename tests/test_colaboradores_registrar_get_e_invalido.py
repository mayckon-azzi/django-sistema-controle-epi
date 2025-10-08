# tests/test_colaboradores_registrar_get_e_invalido.py
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_registrar_get_renderiza_formulario(client):
    """Garante que o GET do registrar renderiza a página com o formulário."""
    r = client.get(reverse("app_colaboradores:registrar"))
    assert r.status_code == 200
    assert "form" in r.context


@pytest.mark.django_db
def test_registrar_post_invalido_permanece_na_pagina_e_exibe_erros(client):
    """
    Envia dados inválidos (ex.: senhas diferentes / campos obrigatórios faltando)
    e verifica que permanece na página exibindo erros de validação.
    """
    r = client.post(
        reverse("app_colaboradores:registrar"),
        data={
            "username": "novo",
            "email": "novo@empresa.com",
            "password1": "Senha12345!",
            "password2": "OutraSenha!",
            "nome": "",
            "matricula": "",
        },
    )
    assert r.status_code == 200
    assert "form" in r.context
    assert r.context["form"].errors
