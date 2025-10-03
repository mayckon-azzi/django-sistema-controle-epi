# tests/test_colaboradores_views_extra.py
from itertools import count

import pytest
from django.contrib.auth.models import Permission, User
from django.db import IntegrityError
from django.urls import reverse

from app_colaboradores.models import Colaborador

_seq = count(1)


def criar_usuario_com_permissao(*codenames, app_label="app_colaboradores"):
    """
    Cria um usuário de teste com permissões específicas.
    """
    sufixo = next(_seq)
    base = "_".join(codenames) if codenames else "noperm"
    usuario = User.objects.create_user(f"u_{base}_{sufixo}", password="x")
    if codenames:
        permissoes = Permission.objects.filter(
            codename__in=codenames, content_type__app_label=app_label
        )
        usuario.user_permissions.add(*permissoes)
    return usuario


@pytest.mark.django_db
def test_login_respeita_next_e_redireciona_por_permissoes(client):
    """
    Testa se o login respeita o parâmetro 'next' e redireciona corretamente
    de acordo com as permissões do usuário.
    """
    usuario = criar_usuario_com_permissao()
    client.force_login(usuario)
    url = reverse("app_colaboradores:entrar") + "?next=" + reverse("app_relatorios:index")
    resposta = client.get(url, follow=False)
    assert resposta.status_code in (302, 303)
    assert resposta.headers["Location"].endswith(reverse("app_relatorios:index"))

    usuario = criar_usuario_com_permissao("view_colaborador")
    client.force_login(usuario)
    resposta = client.get(reverse("app_colaboradores:entrar"), follow=False)
    assert resposta.headers["Location"].endswith(reverse("app_colaboradores:lista"))

    usuario = criar_usuario_com_permissao("view_solicitacao", app_label="app_entregas")
    client.force_login(usuario)
    resposta = client.get(reverse("app_colaboradores:entrar"), follow=False)
    assert resposta.headers["Location"].endswith(reverse("app_entregas:lista"))

    usuario = criar_usuario_com_permissao()
    client.force_login(usuario)
    resposta = client.get(reverse("app_colaboradores:entrar"), follow=False)
    assert resposta.headers["Location"].endswith(reverse("app_core:home"))


@pytest.mark.django_db
def test_lista_colaboradores_anonimo_redireciona_para_login(client):
    """
    Verifica se usuário anônimo é redirecionado para a página de login
    ao acessar a listagem de colaboradores.
    """
    resposta = client.get(reverse("app_colaboradores:lista"), follow=False)
    assert resposta.status_code in (302, 303)


@pytest.mark.django_db
def test_lista_colaboradores_sem_permissao_retorna_403(client):
    """
    Verifica se usuário sem permissão 'view_colaborador' recebe status 403.
    """
    usuario = criar_usuario_com_permissao()
    client.force_login(usuario)
    resposta = client.get(reverse("app_colaboradores:lista"))
    assert resposta.status_code == 403


@pytest.mark.django_db
def test_criar_colaborador_integrity_error_exibe_mensagem(monkeypatch, client):
    """
    Testa se um erro de integridade (duplicidade) ao criar colaborador
    gera a mensagem de erro adequada.
    """
    usuario = criar_usuario_com_permissao("add_colaborador", "view_colaborador")
    client.force_login(usuario)

    from app_colaboradores import views as v

    def falha_save(self, *a, **k):
        raise IntegrityError("dup")

    monkeypatch.setattr(v.ColaboradorAdminForm, "save", falha_save)

    resposta = client.post(
        reverse("app_colaboradores:criar"),
        data={"nome": "X", "email": "x@x.com", "matricula": "Z1"},
        follow=True,
    )
    assert resposta.status_code == 200
    assert "não foi possível criar" in resposta.content.decode().lower()


@pytest.mark.django_db
def test_atualizar_colaborador_integrity_error_exibe_mensagem(monkeypatch, client):
    """
    Testa se um erro de integridade ao atualizar colaborador
    gera a mensagem de erro adequada.
    """
    usuario = criar_usuario_com_permissao("change_colaborador", "view_colaborador")
    client.force_login(usuario)
    colaborador = Colaborador.objects.create(nome="Y", email="y@x.com", matricula="Y1")

    from app_colaboradores import views as v

    def falha_save(self, *a, **k):
        raise IntegrityError("conflict")

    monkeypatch.setattr(v.ColaboradorAdminForm, "save", falha_save)

    resposta = client.post(
        reverse("app_colaboradores:editar", kwargs={"pk": colaborador.pk}),
        data={"nome": "Y", "email": "y@x.com", "matricula": "Y1"},
        follow=True,
    )
    assert resposta.status_code == 200
    assert "não foi possível atualizar" in resposta.content.decode().lower()


@pytest.mark.django_db
def test_excluir_colaborador_adiciona_query_deleted_e_exibe_mensagem(client):
    """
    Testa se a exclusão de um colaborador adiciona parâmetro 'deleted=1'
    na URL, mantém o colaborador com soft delete e exibe mensagem de confirmação.
    """
    usuario = criar_usuario_com_permissao("delete_colaborador", "view_colaborador")
    client.force_login(usuario)
    colaborador = Colaborador.objects.create(nome="Del", matricula="D1", email="d@x.com")

    resposta = client.post(
        reverse("app_colaboradores:excluir", kwargs={"pk": colaborador.pk}),
        follow=True,
    )
    assert resposta.redirect_chain
    final_url, _ = resposta.redirect_chain[-1]
    assert "deleted=1" in final_url
    assert "desativado" in resposta.content.decode().lower()
    colaborador.refresh_from_db()
    assert colaborador.ativo is False


@pytest.mark.django_db
def test_registrar_colaborador_cria_usuario_e_colaborador(client):
    """
    Testa se o registro de colaborador cria corretamente o usuário e o colaborador.
    """
    resposta = client.post(
        reverse("app_colaboradores:registrar"),
        data={
            "username": "novo",
            "email": "novo@empresa.com",
            "password1": "Senha12345!",
            "password2": "Senha12345!",
            "nome": "Novo Usuário",
            "matricula": "N1",
        },
        follow=True,
    )
    assert resposta.status_code == 200
    assert "cadastro realizado com sucesso" in resposta.content.decode().lower()
    usuario = User.objects.get(username="novo")
    colaborador = Colaborador.objects.get(email="novo@empresa.com")
    assert colaborador.user == usuario
