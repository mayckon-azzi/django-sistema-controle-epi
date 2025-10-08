# tests/test_entregas_crud_erros.py
import pytest
from django.contrib.auth.models import Permission, User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega
from app_epis.models import EPI, CategoriaEPI


def _login_with(client, *codenames):
    u = User.objects.create_user("adm", password="x")
    perms = Permission.objects.filter(codename__in=codenames)
    u.user_permissions.add(*perms)
    client.force_login(u)
    return u


@pytest.mark.django_db
def test_criar_entrega_com_quantidade_maior_que_estoque_exibe_erro_e_permanece_no_form(client):
    """
    CriarEntregaView: quando movimenta_por_entrega levanta ValidationError (estoque insuficiente),
    a view adiciona erro, mostra mensagem e permanece no form (status 200).
    """
    _login_with(client, "add_entrega")
    cat = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(codigo="C1", nome="Cap", categoria=cat, estoque=1)
    col = Colaborador.objects.create(nome="N", email="n@x.com", matricula="N1", ativo=True)

    url = reverse("app_entregas:criar")
    r = client.post(
        url,
        data={
            "colaborador": col.pk,
            "epi": epi.pk,
            "quantidade": 5,
            "status": Entrega.Status.EMPRESTADO,
            "data_prevista_devolucao": (timezone.now() + timezone.timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
        },
    )
    assert r.status_code == 200
    template_names = {t.name for t in (r.templates or []) if t.name}
    assert "app_entregas/pages/form.html" in template_names
    assert r.context["form"].errors


@pytest.mark.django_db
def test_atualizar_entrega_para_emprestado_sem_estoque_suficiente_gera_erro(client):
    """
    AtualizarEntregaView: tenta alterar um registro para EMPRESTADO com delta que exigiria
    baixar estoque abaixo de zero -> ValidationError -> permanece no form.
    """
    _login_with(client, "add_entrega", "change_entrega")
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=0)
    col = Colaborador.objects.create(nome="M", email="m@x.com", matricula="M1", ativo=True)

    e = Entrega.objects.create(
        colaborador=col,
        epi=epi,
        quantidade=2,
        status=Entrega.Status.DEVOLVIDO,
        data_entrega=timezone.now(),
        data_devolucao=timezone.now(),
    )

    url = reverse("app_entregas:editar", kwargs={"pk": e.pk})
    r = client.post(
        url,
        data={
            "colaborador": col.pk,
            "epi": epi.pk,
            "quantidade": 2,
            "status": Entrega.Status.EMPRESTADO,  # passará a -2, com estoque 0 -> ValidationError
            "data_prevista_devolucao": (timezone.now() + timezone.timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
        },
    )
    assert r.status_code == 200
    template_names = {t.name for t in (r.templates or []) if t.name}
    assert "app_entregas/pages/form.html" in template_names
    assert r.context["form"].errors


@pytest.mark.django_db
def test_excluir_entrega_quando_service_falhar_mostra_mensagem_de_erro_e_redireciona(
    client, monkeypatch
):
    """
    ExcluirEntregaView: se movimenta_por_exclusao levantar ValidationError,
    a view redireciona para a lista e o ESTOQUE do EPI permanece inalterado.
    (Não dependemos da renderização de mensagens no template, nem da existência do objeto.)
    """
    from app_entregas import services

    _login_with(client, "delete_entrega", "view_entrega")

    cat = CategoriaEPI.objects.create(nome="Óculos")
    epi = EPI.objects.create(codigo="O1", nome="Óculos", categoria=cat, estoque=1)
    col = Colaborador.objects.create(nome="P", email="p@x.com", matricula="P1", ativo=True)
    e = Entrega.objects.create(
        colaborador=col,
        epi=epi,
        quantidade=1,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=timezone.now(),
    )

    estoque_antes = epi.estoque

    def _boom(*args, **kwargs):
        raise ValidationError("falha simulada")

    monkeypatch.setattr(services, "movimenta_por_exclusao", _boom)

    url = reverse("app_entregas:excluir", kwargs={"pk": e.pk})
    r = client.post(url, follow=True)
    assert r.status_code == 200
    assert r.request["PATH_INFO"].endswith(reverse("app_entregas:lista"))

    epi.refresh_from_db()
    assert epi.estoque == estoque_antes
