import pytest
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.db import IntegrityError
from django.test import RequestFactory
from django.urls import reverse

from app_colaboradores.forms import ColaboradorForm
from app_colaboradores.models import Colaborador
from app_core import urls as core_urls
from app_core import views as core_views
from app_entregas.forms import SolicitacaoForm
from app_entregas.models import Entrega
from app_entregas.services import _mov_value
from app_epis.forms import EPIForm
from app_epis.models import EPI, CategoriaEPI
from app_relatorios.forms import RelatorioEntregasForm

# ============================================================
# ======================= APP_CORE ===========================
# ============================================================


# Unitário
@pytest.mark.django_db
def test_unit_core_urls_app_name_eh_app_core():
    """
    Garante que o namespace da app está configurado corretamente em urls.py (app_name == 'app_core').
    """
    assert getattr(core_urls, "app_name", None) == "app_core"


# Unitário
@pytest.mark.django_db
def test_unit_core_home_view_responde_200_com_usuario_anonimo():
    """
    Chama diretamente a função de view 'home' (sem stack HTTP), injeta AnonymousUser e valida HTTP 200.
    """
    rf = RequestFactory()
    req = rf.get("/")
    req.user = AnonymousUser()
    resp = core_views.home(req)
    assert resp.status_code == 200


# Integração
@pytest.mark.django_db
def test_integracao_core_rota_home_responde_200(client):
    """
    Usa o client para acessar a rota nomeada 'app_core:home' passando por URLs/middlewares e valida HTTP 200.
    """
    r = client.get(reverse("app_core:home"))
    assert r.status_code == 200


# Integração
@pytest.mark.django_db
def test_integracao_core_rota_teste_mensagens_redireciona_para_home_e_exibe_mensagem_sucesso(
    client,
):
    """
    Acessa 'app_core:teste_mensagens', verifica redirecionamento para 'home' e presença de mensagem 'Sucesso'.
    """
    r = client.get(reverse("app_core:teste_mensagens"), follow=True)
    assert r.redirect_chain[-1][0].endswith(reverse("app_core:home"))
    msgs = [m.message for m in list(r.context["messages"])]
    assert any("Sucesso" in m for m in msgs)


# ============================================================
# ================== APP_COLABORADORES =======================
# ============================================================


# Unitário
@pytest.mark.django_db
def test_unit_colaborador_str_formata_nome_e_matricula():
    """
    Verifica se __str__ do Colaborador retorna 'Nome (MATRICULA)'.
    """
    c = Colaborador.objects.create(nome="Ana", email="a@x.com", matricula="C1")
    assert str(c) == "Ana (C1)"


# Unitário
@pytest.mark.django_db
def test_unit_colaborador_form_recusa_matricula_duplicada_case_insensitive():
    """
    Valida que o form bloqueia matrícula duplicada (case-insensitive).
    """
    Colaborador.objects.create(nome="B", email="b@x.com", matricula="M1")
    form = ColaboradorForm(data={"nome": "X", "email": "x@x.com", "matricula": "m1"})
    assert not form.is_valid()
    assert "matricula" in form.errors


# Integração
@pytest.mark.django_db
def test_integracao_colaboradores_rota_lista_sem_login_redireciona(client):
    """Acessa 'app_colaboradores:lista' sem autenticação e valida redirecionamento (302/301)."""
    r = client.get(reverse("app_colaboradores:lista"))
    assert r.status_code in (301, 302)


# Integração
@pytest.mark.django_db
def test_integracao_colaboradores_rota_lista_responde_200_para_usuario_com_permissao(client):
    """
    Cria usuário com permissão 'view_colaborador', faz login e valida que a lista responde 200.
    """
    u = User.objects.create_user("u", "u@x.com", "p")
    perm = Permission.objects.get(codename="view_colaborador")
    u.user_permissions.add(perm)
    client.force_login(u)
    r = client.get(reverse("app_colaboradores:lista"))
    assert r.status_code == 200


# ============================================================
# ======================== APP_EPIS ==========================
# ============================================================


# Unitário
@pytest.mark.django_db
def test_unit_epi_model_recusa_criacao_com_estoque_negativo():
    """
    Tenta criar EPI com estoque negativo e espera IntegrityError conforme regra do model.
    """
    cat = CategoriaEPI.objects.create(nome="Luvas")
    with pytest.raises(IntegrityError):
        EPI.objects.create(nome="Luva X", codigo="L1", categoria=cat, estoque=-1)


# Unitário
@pytest.mark.django_db
def test_unit_epi_form_recusa_estoque_negativo_no_submit():
    """
    Submete EPIForm com estoque negativo e valida erro no campo 'estoque'.
    """
    cat = CategoriaEPI.objects.create(nome="Óculos")
    form = EPIForm(
        data={
            "nome": "X",
            "codigo": "C1",
            "categoria": cat.id,
            "tamanho": "U",
            "ativo": True,
            "estoque": -1,
            "estoque_minimo": 0,
        }
    )
    assert not form.is_valid()
    assert "estoque" in form.errors


# Integração
@pytest.mark.django_db
def test_integracao_epi_rota_lista_responde_200(client):
    """
    Usa o client para acessar 'app_epis:lista' verificando a integração URLs→view→resposta.
    """
    r = client.get(reverse("app_epis:lista"))
    assert r.status_code == 200


# Integração
@pytest.mark.django_db
def test_integracao_epi_rota_lista_resolve_e_responde_200(client):
    """
    Resolve a URL via reverse('app_epis:lista') e confirma resposta HTTP 200 via client.get().
    """
    url = reverse("app_epis:lista")
    response = client.get(url)
    assert response.status_code == 200


# ============================================================
# ====================== APP_ENTREGAS ========================
# ============================================================


# Unitário
@pytest.mark.django_db
def test_unit_entregas_services_mov_value_aplica_regra_de_movimentacao():
    """
    Confere a regra de movimentação de estoque: emprestado reduz, devolvido não altera.
    """
    assert _mov_value(Entrega.Status.EMPRESTADO, 2) == -2
    assert _mov_value(Entrega.Status.DEVOLVIDO, 3) == 0


# Unitário
@pytest.mark.django_db
def test_unit_entregas_solicitacao_form_recusa_quantidade_menor_que_um():
    """
    Valida que SolicitacaoForm rejeita quantidade < 1.
    """
    form = SolicitacaoForm(data={"epi": None, "quantidade": 0, "observacao": ""})
    assert not form.is_valid()
    assert "quantidade" in form.errors


# Integração
@pytest.mark.django_db
def test_integracao_entregas_rota_lista_responde_200(client):
    """
    Acessa 'app_entregas:lista' com client e valida HTTP 200.
    """
    r = client.get(reverse("app_entregas:lista"))
    assert r.status_code == 200


# Integração
@pytest.mark.django_db
def test_integracao_entregas_rota_criar_sem_login_redireciona(client):
    """
    Garante que 'app_entregas:criar' exige autenticação, retornando redirecionamento.
    """
    r = client.get(reverse("app_entregas:criar"))
    assert r.status_code in (301, 302)


# ============================================================
# ===================== APP_RELATORIOS =======================
# ============================================================


# Unitário
@pytest.mark.django_db
def test_unit_relatorios_form_intervalo_de_datas_invalido():
    """
    Fornece período invertido (data_de > data_ate) e espera erro em 'data_ate'.
    """
    form = RelatorioEntregasForm(data={"data_de": "2025-12-31", "data_ate": "2025-01-01"})
    assert not form.is_valid()
    assert "data_ate" in form.errors


# Unitário
@pytest.mark.django_db
def test_unit_relatorios_form_campos_opcionais_podem_ficar_em_branco():
    """
    Submete form vazio e valida que é aceito quando filtros são opcionais.
    """
    form = RelatorioEntregasForm(data={})
    assert form.is_valid()


# Integração
@pytest.mark.django_db
def test_integracao_relatorios_rota_index_exige_autenticacao(client):
    """
    Acessa 'app_relatorios:index' sem login e espera redirecionamento (auth requerida).
    """
    r = client.get(reverse("app_relatorios:index"))
    assert r.status_code in (301, 302)


# Integração
@pytest.mark.django_db
def test_integracao_relatorios_rota_exportar_exige_autenticacao(client):
    """
    Acessa 'app_relatorios:exportar' sem login e espera redirecionamento (auth requerida).
    """
    r = client.get(reverse("app_relatorios:exportar"))
    assert r.status_code in (301, 302)
