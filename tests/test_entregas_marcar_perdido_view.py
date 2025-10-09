# tests/test_entregas_marcar_perdido_view.py
import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega
from app_epis.models import EPI, CategoriaEPI


def login_com_permissoes(client, *codenames):
    """Cria usuário com permissões e faz login."""
    u = User.objects.create_user("tester", password="x")
    perms = Permission.objects.filter(codename__in=codenames)
    u.user_permissions.add(*perms)
    client.force_login(u)
    return u


@pytest.mark.django_db
def test_marcar_perdido_aceita_post_e_mantem_efeito_no_estoque(client):
    """
    Dado uma entrega EMPRÉSTIMO/EM_USO, ao marcar PERDIDO via POST:
    - status muda para PERDIDO
    - data_devolucao é preenchida
    - o estoque do EPI permanece com o mesmo efeito líquido (-q)
      (ou seja, não deve aumentar nem diminuir nesse passo)
    - mensagem de sucesso é exibida
    """
    login_com_permissoes(client, "change_entrega")

    categoria = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=categoria, estoque=10)
    colab = Colaborador.objects.create(nome="Ana", email="a@x.com", matricula="A1", ativo=True)

    entrega = Entrega.objects.create(
        colaborador=colab,
        epi=epi,
        quantidade=2,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=timezone.now(),
    )

    estoque_antes = epi.estoque

    url = reverse("app_entregas:marcar_perdido", kwargs={"pk": entrega.pk})
    resp = client.post(url, follow=True)

    assert resp.status_code == 200
    entrega.refresh_from_db()
    epi.refresh_from_db()

    assert entrega.status == Entrega.Status.PERDIDO
    assert entrega.data_devolucao is not None
    assert epi.estoque == estoque_antes

    msgs = [m.message.lower() for m in list(resp.context["messages"])]
    assert any("perdida" in m for m in msgs)


@pytest.mark.django_db
def test_marcar_perdido_rejeita_status_invalidos_e_mostra_warning(client):
    """
    Se a entrega NÃO estiver em EMPRESTADO/EM_USO (ex.: FORNECIDO/DEVOLVIDO),
    a view deve exibir mensagem de aviso e não alterar o status.
    """
    login_com_permissoes(client, "change_entrega")

    categoria = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(codigo="C1", nome="Cap", categoria=categoria, estoque=5)
    colab = Colaborador.objects.create(nome="Bruno", email="b@x.com", matricula="B1", ativo=True)

    entrega = Entrega.objects.create(
        colaborador=colab,
        epi=epi,
        quantidade=1,
        status=Entrega.Status.FORNECIDO,
        data_entrega=timezone.now(),
    )

    url = reverse("app_entregas:marcar_perdido", kwargs={"pk": entrega.pk})
    resp = client.post(url, follow=True)

    assert resp.status_code == 200
    entrega.refresh_from_db()
    assert entrega.status == Entrega.Status.FORNECIDO

    msgs = [m.message.lower() for m in list(resp.context["messages"])]
    assert any("somente entregas" in m and "perdidas" in m for m in msgs)


@pytest.mark.django_db
def test_marcar_perdido_get_redireciona_sem_efeito(client):
    """
    A view aceita apenas POST. Requisições GET devem redirecionar sem efeitos colaterais.
    """
    login_com_permissoes(client, "change_entrega")

    categoria = CategoriaEPI.objects.create(nome="Óculos")
    epi = EPI.objects.create(codigo="O1", nome="Óculos", categoria=categoria, estoque=7)
    colab = Colaborador.objects.create(nome="Carla", email="c@x.com", matricula="C1", ativo=True)

    entrega = Entrega.objects.create(
        colaborador=colab,
        epi=epi,
        quantidade=1,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=timezone.now(),
    )

    url = reverse("app_entregas:marcar_perdido", kwargs={"pk": entrega.pk})
    resp = client.get(url, follow=False)
    assert resp.status_code in (302, 303)
    entrega.refresh_from_db()
    assert entrega.status == Entrega.Status.EMPRESTADO
