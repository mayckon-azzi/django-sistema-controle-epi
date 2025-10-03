# tests/test_models.py
import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_criacao_usuario():
    """
    Verifica se é possível criar um usuário no sistema
    e se o registro recebe uma chave primária (PK) válida.
    """
    User = get_user_model()
    usuario = User.objects.create_user(username="jo", password="x")
    assert usuario.pk is not None
