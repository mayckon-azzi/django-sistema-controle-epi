# tests/test_relatorios.py
import csv
import io
from datetime import timedelta

import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega
from app_epis.models import EPI, CategoriaEPI
from app_relatorios.forms import RelatorioEntregasForm


def _user_with_perm_view_entrega():
    u = User.objects.create_user("rel", password="x")
    u.user_permissions.add(Permission.objects.get(codename="view_entrega"))
    return u


@pytest.mark.django_db
def test_form_date_range_validation():
    form = RelatorioEntregasForm(
        data={
            "data_de": "2025-01-10",
            "data_ate": "2025-01-01",
        }
    )
    assert not form.is_valid()
    assert "data_ate" in form.errors


@pytest.mark.django_db
def test_permissions_on_views(client):
    idx = reverse("app_relatorios:index")
    exp = reverse("app_relatorios:exportar")

    r = client.get(idx)
    assert r.status_code in (302, 303)
    r = client.get(exp)
    assert r.status_code in (302, 303)

    u = User.objects.create_user("nope", password="x")
    client.force_login(u)
    assert client.get(idx).status_code == 403
    assert client.get(exp).status_code == 403

    u2 = _user_with_perm_view_entrega()
    client.force_login(u2)
    assert client.get(idx).status_code == 200
    assert client.get(exp).status_code == 200


@pytest.mark.django_db
def test_context_aggregations_and_filters(client):
    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=cat, estoque=50)
    col = Colaborador.objects.create(nome="Ana", email="a@x.com", matricula="A1", ativo=True)
    now = timezone.now()

    Entrega.objects.create(
        colaborador=col, epi=epi, quantidade=2, status=Entrega.Status.EMPRESTADO, data_entrega=now
    )
    Entrega.objects.create(
        colaborador=col, epi=epi, quantidade=3, status=Entrega.Status.FORNECIDO, data_entrega=now
    )
    Entrega.objects.create(
        colaborador=col,
        epi=epi,
        quantidade=1,
        status=Entrega.Status.DEVOLVIDO,
        data_entrega=now - timedelta(days=1),
        data_devolucao=now,
    )

    u = _user_with_perm_view_entrega()
    client.force_login(u)
    url = reverse("app_relatorios:index")
    r = client.get(url, data={"data_de": (now - timedelta(days=2)).date().isoformat()})
    assert r.status_code == 200

    ctx = r.context
    assert "agg" in ctx and "por_epi" in ctx and "por_colab" in ctx and "qs" in ctx

    agg = ctx["agg"]
    assert agg["total_entregue"] == 5
    assert agg["total_devolvido"] == 1
    assert agg["registros"] == 3
    assert agg["quantidade_total"] == 6
    assert len(ctx["qs"]) == 3


@pytest.mark.django_db
def test_export_csv_filters_and_format(client):
    cat = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(codigo="C1", nome="Cap", categoria=cat, estoque=10)
    col = Colaborador.objects.create(nome="Bruno", email="b@x.com", matricula="B1", ativo=True)
    now = timezone.now()

    Entrega.objects.create(
        colaborador=col, epi=epi, quantidade=1, status=Entrega.Status.EMPRESTADO, data_entrega=now
    )
    Entrega.objects.create(
        colaborador=col,
        epi=epi,
        quantidade=4,
        status=Entrega.Status.DEVOLVIDO,
        data_entrega=now - timedelta(hours=2),
        data_devolucao=now - timedelta(hours=1),
        observacao="ok\nlinha",
    )

    u = _user_with_perm_view_entrega()
    client.force_login(u)
    url = reverse("app_relatorios:exportar")
    r = client.get(url, data={"status": Entrega.Status.DEVOLVIDO})
    assert r.status_code == 200
    assert "text/csv" in r["Content-Type"]

    content = r.content.decode("utf-8")
    rd = csv.reader(io.StringIO(content), delimiter=";")
    rows = list(rd)
    assert rows[0] == [
        "Data Entrega",
        "Data Devolução Prevista",
        "Data Devolução",
        "Colaborador",
        "EPI",
        "Quantidade",
        "Status",
        "Observação",
    ]
    assert len(rows) == 2
    data_row = rows[1]
    assert data_row[3] == "Bruno"
    assert data_row[4].startswith("Cap (C1)")
    assert data_row[5] == "4"
    assert data_row[6].lower() == "devolvido"
    assert "linha" in data_row[7] and "\n" not in data_row[7]
