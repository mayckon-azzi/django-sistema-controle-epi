# tests/test_colaboradores_perfil_fluxos_completos.py
import pytest
from django.contrib.auth.models import Permission, User
from django.core.files.base import ContentFile
from django.urls import reverse

from app_colaboradores.models import Colaborador


def _perm(user, codename):
    user.user_permissions.add(Permission.objects.get(codename=codename))


@pytest.mark.django_db
def test_perfil_sem_colaborador_com_perm_add_redireciona_para_criar_e_informa(client):
    """Sem perfil: se usuário tem permissão de 'add_colaborador', redireciona para criar com mensagem informativa."""
    u = User.objects.create_user("u1", email="u1@x.com", password="x")
    _perm(u, "add_colaborador")
    client.force_login(u)

    r = client.get(reverse("app_colaboradores:perfil"), follow=True)
    assert r.status_code == 200
    assert r.request["PATH_INFO"].endswith(reverse("app_colaboradores:criar"))
    msgs = [m.message.lower() for m in list(r.context["messages"])]
    assert any("crie seu perfil" in m for m in msgs)


@pytest.mark.django_db
def test_perfil_sem_colaborador_sem_perm_redireciona_home_com_erro(client):
    """
    Sem perfil e sem permissão: redireciona para home com mensagem de erro.
    """
    u = User.objects.create_user("u2", email="u2@x.com", password="x")
    client.force_login(u)

    r = client.get(reverse("app_colaboradores:perfil"), follow=True)
    assert r.status_code == 200
    assert r.request["PATH_INFO"].endswith(reverse("app_core:home"))
    msgs = [m.message.lower() for m in list(r.context["messages"])]
    assert any("não possui um perfil de colaborador" in m for m in msgs)


@pytest.mark.django_db
def test_perfil_pk_de_terceiro_sem_permissao_retornando_403(client):
    """
    Acessar perfil por pk de outro colaborador sem permissão 'view_colaborador' deve resultar em 403.
    """

    alvo_user = User.objects.create_user("alvo", email="a@x.com", password="x")
    alvo_colab = Colaborador.objects.create(
        nome="Alvo", email="a@x.com", matricula="A1", user=alvo_user
    )

    req_user = User.objects.create_user("req", email="r@x.com", password="x")
    Colaborador.objects.create(nome="Req", email="r@x.com", matricula="R1", user=req_user)

    client.force_login(req_user)
    r = client.get(reverse("app_colaboradores:perfil_pk", kwargs={"pk": alvo_colab.pk}))
    assert r.status_code == 403


@pytest.mark.django_db
def test_perfil_get_contexto_traz_colaborador_e_form_de_foto(client):
    """
    Confere que o contexto do perfil inclui 'colaborador' e 'foto_form'.
    """
    u = User.objects.create_user("u3", email="u3@x.com", password="x")
    colab = Colaborador.objects.create(nome="U3", email="u3@x.com", matricula="U3", user=u)
    client.force_login(u)

    r = client.get(reverse("app_colaboradores:perfil"))
    assert r.status_code == 200

    def _get_from_ctx(key):
        for d in getattr(r, "context", []) or []:
            if key in d:
                return d[key]
        raise KeyError(key)

    colab_ctx = _get_from_ctx("colaborador")
    assert colab_ctx.pk == colab.pk
    assert _get_from_ctx("foto_form") is not None


@pytest.mark.django_db
def test_perfil_post_remover_sem_foto_mostra_info(client):
    """Ao enviar POST com 'remover' sem foto, deve informar que não há foto para remover."""
    u = User.objects.create_user("u4", email="u4@x.com", password="x")
    Colaborador.objects.create(nome="U4", email="u4@x.com", matricula="U4", user=u)
    client.force_login(u)

    r = client.post(reverse("app_colaboradores:perfil"), data={"remover": "1"}, follow=True)
    assert r.status_code == 200
    msgs = [m.message.lower() for m in list(r.context["messages"])]
    assert any("não possui foto" in m for m in msgs)


@pytest.mark.django_db
def test_perfil_post_remover_com_foto_remove_e_sucesso(client, settings, tmp_path):
    """Remove a foto quando presente e exibe mensagem de sucesso."""
    settings.MEDIA_ROOT = tmp_path  # isola gravações
    u = User.objects.create_user("u5", email="u5@x.com", password="x")
    colab = Colaborador.objects.create(nome="U5", email="u5@x.com", matricula="U5", user=u)

    colab.foto.save("qualquer.bin", ContentFile(b"abc"), save=True)
    assert colab.foto
    client.force_login(u)

    r = client.post(reverse("app_colaboradores:perfil"), data={"remover": "1"}, follow=True)
    assert r.status_code == 200
    colab.refresh_from_db()
    assert not colab.foto
    msgs = [m.message.lower() for m in list(r.context["messages"])]
    assert any("foto removida com sucesso" in m for m in msgs)


@pytest.mark.django_db
def test_perfil_post_invalido_permanece_na_pagina_e_recria_contexto(client):
    """
    POST sem arquivo (e sem 'remover') é inválido.
    A view não redireciona: re-renderiza a página de perfil via self.get(...),
    garantindo que o contexto contenha 'colaborador' e 'foto_form'.
    """
    u = User.objects.create_user("u6", email="u6@x.com", password="x")
    colab = Colaborador.objects.create(nome="U6", email="u6@x.com", matricula="U6", user=u)
    client.force_login(u)

    r = client.post(reverse("app_colaboradores:perfil"), data={}, follow=True)
    assert r.status_code == 200

    template_names = {t.name for t in (r.templates or []) if t.name}
    assert "app_colaboradores/pages/perfil.html" in template_names

    def _get_from_ctx(key):
        for d in getattr(r, "context", []) or []:
            if key in d:
                return d[key]
        raise KeyError(key)

    colab_ctx = _get_from_ctx("colaborador")
    assert colab_ctx.pk == colab.pk
    assert _get_from_ctx("foto_form") is not None
