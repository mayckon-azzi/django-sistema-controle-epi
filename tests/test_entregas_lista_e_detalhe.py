# tests/test_entregas_lista_e_detalhe.py
import pytest
from django.urls import reverse
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega
from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db
def test_lista_filtra_por_q_colaborador_epi_status_e_monta_base_query(client, django_user_model):
    """
    Lista de entregas: aplica filtros por q/colaborador/epi/status e constrói 'base_query' sem 'page'.
    Valida parâmetros via parsing (resistente a URL encoding) e confirma o resultado pela lista do contexto.
    """
    from urllib.parse import parse_qs

    user = django_user_model.objects.create_user("u", password="x")
    client.force_login(user)

    cat = CategoriaEPI.objects.create(nome="Luvas")
    epi1 = EPI.objects.create(codigo="L1", nome="Luva Nitrílica", categoria=cat, estoque=10)
    epi2 = EPI.objects.create(codigo="L2", nome="Luva Térmica", categoria=cat, estoque=10)
    col1 = Colaborador.objects.create(nome="Ana", email="ana@x.com", matricula="A1", ativo=True)
    col2 = Colaborador.objects.create(nome="Bruno", email="bruno@x.com", matricula="B1", ativo=True)

    e1 = Entrega.objects.create(
        colaborador=col1,
        epi=epi1,
        quantidade=1,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=timezone.now(),
    )
    Entrega.objects.create(
        colaborador=col2,
        epi=epi2,
        quantidade=1,
        status=Entrega.Status.DEVOLVIDO,
        data_entrega=timezone.now(),
        data_devolucao=timezone.now(),
    )

    url = reverse("app_entregas:lista")
    params = {
        "q": "nitrílica",
        "colaborador": str(col1.pk),
        "epi": str(epi1.pk),
        "status": Entrega.Status.EMPRESTADO,
        "page": "2",
    }
    r = client.get(url, params)
    assert r.status_code == 200

    ctx = r.context[-1]
    assert ctx["q"] == params["q"]
    assert ctx["colaborador_id"] == params["colaborador"]
    assert ctx["epi_id"] == params["epi"]
    assert ctx["status"] == params["status"]

    bq = ctx["base_query"]
    assert "page=" not in bq
    parsed = parse_qs(bq, keep_blank_values=True)
    assert parsed.get("q", [None])[0] == params["q"]
    assert parsed.get("colaborador", [None])[0] == params["colaborador"]
    assert parsed.get("epi", [None])[0] == params["epi"]
    assert parsed.get("status", [None])[0] == params["status"]

    entregas_list = list(ctx["entregas"])
    assert len(entregas_list) == 1
    assert entregas_list[0].pk == e1.pk
    assert entregas_list[0].colaborador_id == col1.pk
    assert entregas_list[0].epi_id == epi1.pk
    assert entregas_list[0].status == Entrega.Status.EMPRESTADO


@pytest.mark.django_db
def test_detalhe_entrega_renderiza_template_e_contexto(client, django_user_model):
    """
    Detalhe de entrega: renderiza o template e expõe 'entrega' no contexto.
    """
    user = django_user_model.objects.create_user("u2", password="x")
    client.force_login(user)

    cat = CategoriaEPI.objects.create(nome="Óculos")
    epi = EPI.objects.create(codigo="O1", nome="Óculos de proteção", categoria=cat, estoque=5)
    col = Colaborador.objects.create(nome="Clara", email="c@x.com", matricula="C1", ativo=True)
    e = Entrega.objects.create(
        colaborador=col,
        epi=epi,
        quantidade=1,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=timezone.now(),
    )

    r = client.get(reverse("app_entregas:detalhe", kwargs={"pk": e.pk}))
    assert r.status_code == 200
    template_names = {t.name for t in (r.templates or []) if t.name}
    assert "app_entregas/pages/detail.html" in template_names
    assert r.context["entrega"].pk == e.pk
