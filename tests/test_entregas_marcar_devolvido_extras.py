# tests/test_entregas_marcar_devolvido_extras.py
import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega
from app_epis.models import EPI, CategoriaEPI


def _login(client, *codenames):
    u = User.objects.create_user("op", password="x")
    u.user_permissions.add(*Permission.objects.filter(codename__in=codenames))
    client.force_login(u)
    return u


@pytest.mark.django_db
def test_marcar_devolvido_rejeita_get_sem_efeito(client):
    """
    marcar_devolvido aceita apenas POST: GET deve redirecionar sem efeitos.
    """
    _login(client, "change_entrega")
    cat = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(codigo="C1", nome="Cap", categoria=cat, estoque=5)
    col = Colaborador.objects.create(nome="D", email="d@x.com", matricula="D1", ativo=True)
    e = Entrega.objects.create(
        colaborador=col,
        epi=epi,
        quantidade=1,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=timezone.now(),
    )

    url = reverse("app_entregas:marcar_devolvido", kwargs={"pk": e.pk})
    r = client.get(url)
    assert r.status_code in (302, 303)
    e.refresh_from_db()
    assert e.status == Entrega.Status.EMPRESTADO
