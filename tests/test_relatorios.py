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


def criar_usuario_com_permissao_view_entrega():
    """
    Cria um usuário com permissão de visualizar entregas.
    """
    usuario = User.objects.create_user("rel", password="x")
    usuario.user_permissions.add(Permission.objects.get(codename="view_entrega"))
    return usuario


@pytest.mark.django_db
def test_validacao_periodo_datas_relatorio():
    """
    Testa se o formulário de relatório de entregas valida corretamente
    quando a data de término é anterior à data inicial.
    """
    form = RelatorioEntregasForm(
        data={
            "data_de": "2025-01-10",
            "data_ate": "2025-01-01",
        }
    )
    assert not form.is_valid()
    assert "data_ate" in form.errors


@pytest.mark.django_db
def test_permissoes_acesso_relatorios(client):
    """
    Testa se as views de relatórios exigem login e permissões adequadas.
    """
    url_index = reverse("app_relatorios:index")
    url_exportar = reverse("app_relatorios:exportar")

    # Usuário anônimo
    resp = client.get(url_index)
    assert resp.status_code in (302, 303)
    resp = client.get(url_exportar)
    assert resp.status_code in (302, 303)

    # Usuário sem permissão
    usuario = User.objects.create_user("nope", password="x")
    client.force_login(usuario)
    assert client.get(url_index).status_code == 403
    assert client.get(url_exportar).status_code == 403

    # Usuário com permissão
    usuario2 = criar_usuario_com_permissao_view_entrega()
    client.force_login(usuario2)
    assert client.get(url_index).status_code == 200
    assert client.get(url_exportar).status_code == 200


@pytest.mark.django_db
def test_agregacoes_e_filtros_contexto_relatorio(client):
    """
    Testa se o contexto da view de relatórios contém agregações corretas
    e se os filtros aplicados funcionam conforme esperado.
    """
    categoria = CategoriaEPI.objects.create(nome="Luvas")
    epi = EPI.objects.create(codigo="L1", nome="Luva", categoria=categoria, estoque=50)
    colaborador = Colaborador.objects.create(
        nome="Ana", email="a@x.com", matricula="A1", ativo=True
    )
    agora = timezone.now()

    # Criar entregas
    Entrega.objects.create(
        colaborador=colaborador,
        epi=epi,
        quantidade=2,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=agora,
    )
    Entrega.objects.create(
        colaborador=colaborador,
        epi=epi,
        quantidade=3,
        status=Entrega.Status.FORNECIDO,
        data_entrega=agora,
    )
    Entrega.objects.create(
        colaborador=colaborador,
        epi=epi,
        quantidade=1,
        status=Entrega.Status.DEVOLVIDO,
        data_entrega=agora - timedelta(days=1),
        data_devolucao=agora,
    )

    usuario = criar_usuario_com_permissao_view_entrega()
    client.force_login(usuario)
    url = reverse("app_relatorios:index")
    resp = client.get(url, data={"data_de": (agora - timedelta(days=2)).date().isoformat()})
    assert resp.status_code == 200
    ctx = resp.context
    assert "agg" in ctx and "por_epi" in ctx and "por_colab" in ctx and "qs" in ctx

    agg = ctx["agg"]
    assert agg["total_entregue"] == 5
    assert agg["total_devolvido"] == 1
    assert agg["registros"] == 3
    assert agg["quantidade_total"] == 6
    assert len(ctx["qs"]) == 3


@pytest.mark.django_db
def test_exportacao_csv_relatorio(client):
    """
    Testa se a exportação de relatório para CSV aplica filtros corretamente
    e mantém o formato esperado.
    """
    categoria = CategoriaEPI.objects.create(nome="Capacete")
    epi = EPI.objects.create(codigo="C1", nome="Cap", categoria=categoria, estoque=10)
    colaborador = Colaborador.objects.create(
        nome="Bruno", email="b@x.com", matricula="B1", ativo=True
    )
    agora = timezone.now()

    Entrega.objects.create(
        colaborador=colaborador,
        epi=epi,
        quantidade=1,
        status=Entrega.Status.EMPRESTADO,
        data_entrega=agora,
    )
    Entrega.objects.create(
        colaborador=colaborador,
        epi=epi,
        quantidade=4,
        status=Entrega.Status.DEVOLVIDO,
        data_entrega=agora - timedelta(hours=2),
        data_devolucao=agora - timedelta(hours=1),
        observacao="ok\nlinha",
    )

    usuario = criar_usuario_com_permissao_view_entrega()
    client.force_login(usuario)
    url = reverse("app_relatorios:exportar")
    resp = client.get(url, data={"status": Entrega.Status.DEVOLVIDO})
    assert resp.status_code == 200
    assert "text/csv" in resp["Content-Type"]

    conteudo = resp.content.decode("utf-8")
    leitor = csv.reader(io.StringIO(conteudo), delimiter=";")
    linhas = list(leitor)

    # Cabeçalho CSV
    assert linhas[0] == [
        "Data Entrega",
        "Data Devolução Prevista",
        "Data Devolução",
        "Colaborador",
        "EPI",
        "Quantidade",
        "Status",
        "Observação",
    ]

    # Linha de dados
    assert len(linhas) == 2
    linha_dado = linhas[1]
    assert linha_dado[3] == "Bruno"
    assert linha_dado[4].startswith("Cap (C1)")
    assert linha_dado[5] == "4"
    assert linha_dado[6].lower() == "devolvido"
    assert "linha" in linha_dado[7] and "\n" not in linha_dado[7]
