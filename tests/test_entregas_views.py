# tests/test_entregas_views.py
from datetime import timedelta

import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega, Solicitacao
from app_epis.models import EPI, CategoriaEPI


def login_com_permissoes(client, *codenames):
    """
    Cria um usuário com permissões específicas e realiza login.
    """
    usuario = User.objects.create_user("usuario_test", password="x")
    permissoes = Permission.objects.filter(codename__in=codenames)
    usuario.user_permissions.add(*permissoes)
    client.force_login(usuario)
    return usuario


@pytest.mark.django_db
def test_criar_entrega_exige_login_e_permissao(client):
    """
    Verifica se a página de criação de entrega exige login,
    redirecionando usuários anônimos.
    """
    url = reverse("app_entregas:criar")
    resposta = client.get(url)
    assert resposta.status_code in (302, 303)


@pytest.mark.django_db
def test_criar_entrega_atualiza_estoque_e_exibe_mensagem(client):
    """
    Testa se a criação de uma entrega ajusta corretamente o estoque
    e exibe mensagem de sucesso.
    """
    login_com_permissoes(client, "add_entrega")
    categoria = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=categoria, estoque=5)
    colaborador = Colaborador.objects.create(nome="Z", email="z@x.com", matricula="Z1", ativo=True)

    url = reverse("app_entregas:criar")
    resposta = client.post(
        url,
        data={
            "colaborador": colaborador.pk,
            "epi": epi.pk,
            "quantidade": 2,
            "status": Entrega.Status.EMPRESTADO,
            "data_prevista_devolucao": (timezone.now() + timedelta(days=3)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "observacao": "teste",
        },
        follow=True,
    )
    assert resposta.status_code == 200
    epi.refresh_from_db()
    assert epi.estoque == 3
    assert "registrada com sucesso" in resposta.content.decode().lower()


@pytest.mark.django_db
def test_atualizar_e_excluir_entrega_ajusta_estoque_e_mensagens(client):
    """
    Testa se atualização e exclusão de entrega ajustam o estoque corretamente
    e exibem mensagens de confirmação.
    """
    login_com_permissoes(client, "add_entrega", "change_entrega", "delete_entrega")
    categoria = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(codigo="C1", nome="Cap", categoria=categoria, estoque=4)
    colaborador = Colaborador.objects.create(nome="Y", email="y@x.com", matricula="Y1", ativo=True)

    # Criar entrega
    url_create = reverse("app_entregas:criar")
    client.post(
        url_create,
        data={
            "colaborador": colaborador.pk,
            "epi": epi.pk,
            "quantidade": 1,
            "status": Entrega.Status.EMPRESTADO,
            "data_prevista_devolucao": (timezone.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
        },
        follow=True,
    )
    epi.refresh_from_db()
    assert epi.estoque == 3

    entrega = Entrega.objects.latest("id")

    # Atualizar entrega
    url_edit = reverse("app_entregas:editar", kwargs={"pk": entrega.pk})
    resposta = client.post(
        url_edit,
        data={
            "colaborador": colaborador.pk,
            "epi": epi.pk,
            "quantidade": 1,
            "status": Entrega.Status.DEVOLVIDO,
            "data_prevista_devolucao": (timezone.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "data_devolucao": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        },
        follow=True,
    )
    assert resposta.status_code == 200
    epi.refresh_from_db()
    assert epi.estoque == 4
    assert "atualizada com sucesso" in resposta.content.decode().lower()

    # Excluir entrega
    url_del = reverse("app_entregas:excluir", kwargs={"pk": entrega.pk})
    resposta = client.post(url_del, follow=True)
    assert resposta.status_code == 200


@pytest.mark.django_db
def test_solicitacoes_criar_aprovar_reprovar_atender(client):
    """
    Testa todo o fluxo de solicitações:
    - criação
    - aprovação
    - atendimento
    - devolução
    - reprovação
    """
    usuario = login_com_permissoes(
        client, "add_solicitacao", "change_solicitacao", "change_entrega"
    )
    colaborador = Colaborador.objects.create(
        nome="U", email="u@x.com", matricula="U1", ativo=True, user=usuario
    )
    categoria = CategoriaEPI.objects.create(nome="Óculos")
    epi = EPI.objects.create(codigo="O1", nome="Óculos", categoria=categoria, estoque=10)

    # Criar solicitação
    url_new = reverse("app_entregas:criar_solicitacao")
    resposta = client.post(
        url_new, data={"epi": epi.pk, "quantidade": 2, "observacao": ""}, follow=True
    )
    assert resposta.status_code == 200
    solicitacao = Solicitacao.objects.get()
    assert solicitacao.colaborador == colaborador

    # Aprovar solicitação
    url_aprovar = reverse("app_entregas:aprovar_solicitacao", kwargs={"pk": solicitacao.pk})
    resposta = client.post(url_aprovar, follow=True)
    assert resposta.status_code == 200
    solicitacao.refresh_from_db()
    assert solicitacao.status == Solicitacao.Status.APROVADA

    # Atender solicitação
    url_atender = reverse("app_entregas:atender_solicitacao", kwargs={"pk": solicitacao.pk})
    resposta = client.post(url_atender, follow=True)
    assert resposta.status_code == 200
    solicitacao.refresh_from_db()
    assert solicitacao.status == Solicitacao.Status.ATENDIDA
    epi.refresh_from_db()
    assert epi.estoque == 8

    # Marcar devolvido
    entrega = Entrega.objects.latest("id")
    url_devolvido = reverse("app_entregas:marcar_devolvido", kwargs={"pk": entrega.pk})
    resposta = client.post(url_devolvido, follow=True)
    assert resposta.status_code == 200
    epi.refresh_from_db()
    assert epi.estoque == 10
    assert "devolvida" in resposta.content.decode().lower()

    # Reprovar solicitação
    solicitacao2 = Solicitacao.objects.create(colaborador=colaborador, epi=epi, quantidade=1)
    url_reprovar = reverse("app_entregas:reprovar_solicitacao", kwargs={"pk": solicitacao2.pk})
    resposta = client.post(url_reprovar, follow=True)
    assert resposta.status_code == 200
    solicitacao2.refresh_from_db()
    assert solicitacao2.status == Solicitacao.Status.REPROVADA
