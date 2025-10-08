# tests/test_solicitacoes_fluxos_extras.py
import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from app_colaboradores.models import Colaborador
from app_entregas.models import Solicitacao
from app_epis.models import EPI, CategoriaEPI


def _login(client, *codenames):
    u = User.objects.create_user("gestor", password="x")
    perms = Permission.objects.filter(codename__in=codenames)
    u.user_permissions.add(*perms)
    client.force_login(u)
    return u


@pytest.mark.django_db
def test_criar_solicitacao_sem_colaborador_ativo_redireciona_para_home_com_erro(client):
    """
    CriarSolicitacaoView.dispatch: sem vínculo de colaborador (ou inativo) => erro e redirect para home.
    """
    _login(client, "add_solicitacao")
    url = reverse("app_entregas:criar_solicitacao")
    r = client.get(url, follow=True)
    assert r.status_code == 200
    assert r.request["PATH_INFO"].endswith(reverse("app_core:home"))


@pytest.mark.django_db
def test_minhas_solicitacoes_sem_colaborador_retorna_lista_vazia(client, django_user_model):
    """
    MinhasSolicitacoesView: usuário sem colaborador => queryset vazio.
    """
    user = django_user_model.objects.create_user("x", password="x")
    client.force_login(user)
    url = reverse("app_entregas:minhas_solicitacoes")
    r = client.get(url)
    assert r.status_code == 200
    assert list(r.context["solicitacoes"]) == []


@pytest.mark.django_db
def test_solicitacoes_gerenciar_filtra_por_status_e_contexto(client):
    """
    SolicitacoesGerenciarView: filtra por status (default PENDENTE / com param APROVADA) e injeta contexto auxiliar.
    """
    _login(client, "change_solicitacao")
    col = Colaborador.objects.create(nome="Ana", email="a@x.com", matricula="A1", ativo=True)
    cat = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(codigo="C1", nome="Cap", categoria=cat, estoque=5)

    s1 = Solicitacao.objects.create(colaborador=col, epi=epi, quantidade=1)  # default PENDENTE
    s2 = Solicitacao.objects.create(
        colaborador=col, epi=epi, quantidade=1, status=Solicitacao.Status.APROVADA
    )

    r = client.get(reverse("app_entregas:solicitacoes_gerenciar"))
    assert r.status_code == 200
    ctx = r.context[-1]
    assert ctx["status_selected"] == "PENDENTE"
    assert "PENDENTE" in ctx["statuses_manage"]
    assert "APROVADA" in ctx["statuses_manage"]
    ids = {s.pk for s in r.context["solicitacoes"]}
    assert s1.pk in ids and s2.pk not in ids

    r2 = client.get(reverse("app_entregas:solicitacoes_gerenciar") + "?status=APROVADA")
    assert r2.status_code == 200
    ids2 = {s.pk for s in r2.context["solicitacoes"]}
    assert s2.pk in ids2 and s1.pk not in ids2
    assert r2.context["status_selected"] == "APROVADA"


@pytest.mark.django_db
def test_aprovar_reprovar_solicitacao_com_status_invalido_mostra_warning(client):
    """
    Quando a solicitação não está PENDENTE, aprovar/reprovar deve apenas avisar e redirecionar.
    """
    _login(client, "change_solicitacao")
    col = Colaborador.objects.create(nome="B", email="b@x.com", matricula="B1", ativo=True)
    cat = CategoriaEPI.objects.create(nome="Óculos")
    epi = EPI.objects.create(codigo="O1", nome="Óculos", categoria=cat, estoque=3)
    s = Solicitacao.objects.create(
        colaborador=col, epi=epi, quantidade=1, status=Solicitacao.Status.APROVADA
    )

    url_aprovar = reverse("app_entregas:aprovar_solicitacao", kwargs={"pk": s.pk})
    r = client.post(url_aprovar, follow=True)
    assert r.status_code == 200
    assert "somente solicitações pendentes" in r.content.decode().lower()

    url_reprovar = reverse("app_entregas:reprovar_solicitacao", kwargs={"pk": s.pk})
    r2 = client.post(url_reprovar, follow=True)
    assert r2.status_code == 200
    assert "somente solicitações pendentes" in r2.content.decode().lower()


@pytest.mark.django_db
def test_atender_solicitacao_get_renderiza_confirmacao_e_status_invalido_emite_warning(client):
    """
    atender_solicitacao:
    - GET com solicitação **PENDENTE** deve renderizar a página de confirmação (200).
    - POST com solicitação em **REPROVADA** deve avisar (warning) e redirecionar (302 -> 200 após follow).
    """
    _login(client, "change_solicitacao")
    col = Colaborador.objects.create(nome="C", email="c@x.com", matricula="C1", ativo=True)
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=5)

    s_pendente = Solicitacao.objects.create(
        colaborador=col, epi=epi, quantidade=1, status=Solicitacao.Status.PENDENTE
    )
    r_get = client.get(reverse("app_entregas:atender_solicitacao", kwargs={"pk": s_pendente.pk}))
    assert r_get.status_code == 200
    template_names = {t.name for t in (r_get.templates or []) if t.name}
    assert "app_entregas/pages/solicitacao_atender_confirm.html" in template_names

    s_reprovada = Solicitacao.objects.create(
        colaborador=col, epi=epi, quantidade=1, status=Solicitacao.Status.REPROVADA
    )
    r_post = client.post(
        reverse("app_entregas:atender_solicitacao", kwargs={"pk": s_reprovada.pk}), follow=True
    )
    assert r_post.status_code == 200
    assert r_post.request["PATH_INFO"].endswith(reverse("app_entregas:solicitacoes_gerenciar"))
    assert "apenas solicitações pendentes/aprovadas" in r_post.content.decode().lower()
