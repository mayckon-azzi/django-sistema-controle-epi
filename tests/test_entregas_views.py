# tests/test_entregas_views.py
from datetime import timedelta

import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega, Solicitacao
from app_epis.models import EPI, CategoriaEPI


def _login_with_perms(client, *codenames):
    u = User.objects.create_user("almox", password="x")
    perms = Permission.objects.filter(codename__in=codenames)
    u.user_permissions.add(*perms)
    client.force_login(u)
    return u


@pytest.mark.django_db
def test_criar_requires_login_and_perm(client):
    url = reverse("app_entregas:criar")
    resp = client.get(url)
    # LoginRequiredMixin primeiro -> redireciona anônimo
    assert resp.status_code in (302, 303)


@pytest.mark.django_db
def test_criar_entrega_updates_stock_and_shows_message(client):
    _login_with_perms(client, "add_entrega")
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=5)
    col = Colaborador.objects.create(nome="Z", email="z@x.com", matricula="Z1", ativo=True)

    url = reverse("app_entregas:criar")
    resp = client.post(
        url,
        data={
            "colaborador": col.pk,
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
    assert resp.status_code == 200
    epi.refresh_from_db()
    assert epi.estoque == 3
    assert "registrada com sucesso" in resp.content.decode().lower()


@pytest.mark.django_db
def test_atualizar_entrega_and_delete_adjusts_stock_and_messages(client):
    _login_with_perms(client, "add_entrega", "change_entrega", "delete_entrega")
    cat = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(codigo="C1", nome="Cap", categoria=cat, estoque=4)
    col = Colaborador.objects.create(nome="Y", email="y@x.com", matricula="Y1", ativo=True)

    # cria via view
    url_create = reverse("app_entregas:criar")
    client.post(
        url_create,
        data={
            "colaborador": col.pk,
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
    e = Entrega.objects.latest("id")

    # update -> DEVOLVIDO
    url_edit = reverse("app_entregas:editar", kwargs={"pk": e.pk})
    resp = client.post(
        url_edit,
        data={
            "colaborador": col.pk,
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
    assert resp.status_code == 200
    epi.refresh_from_db()
    assert epi.estoque == 4
    assert "atualizada com sucesso" in resp.content.decode().lower()

    # delete -> mensagem
    url_del = reverse("app_entregas:excluir", kwargs={"pk": e.pk})
    resp = client.post(url_del, follow=True)
    assert resp.status_code == 200


@pytest.mark.django_db
def test_solicitacoes_criar_aprovar_reprovar_atender_e_acoes_rapidas(client):
    # permissões necessárias
    u = _login_with_perms(client, "add_solicitacao", "change_solicitacao", "change_entrega")
    col = Colaborador.objects.create(nome="U", email="u@x.com", matricula="U1", ativo=True, user=u)
    cat = CategoriaEPI.objects.create(nome="Óculos")
    epi = EPI.objects.create(codigo="O1", nome="Óculos", categoria=cat, estoque=10)

    # criar solicitacao (colaborador logado e ativo)
    url_new = reverse("app_entregas:criar_solicitacao")
    resp = client.post(
        url_new, data={"epi": epi.pk, "quantidade": 2, "observacao": ""}, follow=True
    )
    assert resp.status_code == 200
    s = Solicitacao.objects.get()
    assert s.colaborador == col

    # aprovar
    url_ap = reverse("app_entregas:aprovar_solicitacao", kwargs={"pk": s.pk})
    resp = client.post(url_ap, follow=True)
    assert resp.status_code == 200
    s.refresh_from_db()
    assert s.status == Solicitacao.Status.APROVADA

    # atender -> cria entrega e reduz estoque
    url_att = reverse("app_entregas:atender_solicitacao", kwargs={"pk": s.pk})
    resp = client.post(url_att, follow=True)
    assert resp.status_code == 200
    s.refresh_from_db()
    assert s.status == Solicitacao.Status.ATENDIDA
    epi.refresh_from_db()
    assert epi.estoque == 8  # -2

    # ação rápida: marcar devolvido (repõe q=2)
    e = Entrega.objects.latest("id")
    url_dev = reverse("app_entregas:marcar_devolvido", kwargs={"pk": e.pk})
    resp = client.post(url_dev, follow=True)
    assert resp.status_code == 200
    epi.refresh_from_db()
    assert epi.estoque == 10
    assert "devolvida" in resp.content.decode().lower()

    # reprovar (em geral seria outra pendente, mas aqui exercita endpoint)
    s2 = Solicitacao.objects.create(colaborador=col, epi=epi, quantidade=1)
    url_rep = reverse("app_entregas:reprovar_solicitacao", kwargs={"pk": s2.pk})
    resp = client.post(url_rep, follow=True)
    assert resp.status_code == 200
    s2.refresh_from_db()
    assert s2.status == Solicitacao.Status.REPROVADA
