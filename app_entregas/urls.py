from django.urls import path

from . import views

app_name = "app_entregas"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.CriarEntregaView.as_view(), name="criar"),
    # Solicitações - colaborador
    path(
        "solicitacoes/nova/",
        views.CriarSolicitacaoView.as_view(),
        name="criar_solicitacao",
    ),
    path(
        "solicitacoes/minhas/",
        views.MinhasSolicitacoesView.as_view(),
        name="minhas_solicitacoes",
    ),
    # Ações rápidas
    path("<int:pk>/marcar/devolvido/", views.marcar_devolvido, name="marcar_devolvido"),
    path("<int:pk>/marcar/perdido/", views.marcar_perdido, name="marcar_perdido"),
    # Solicitações - almoxarife (gerenciar)
    path(
        "solicitacoes/gerenciar/",
        views.SolicitacoesGerenciarView.as_view(),
        name="solicitacoes_gerenciar",
    ),
    path(
        "solicitacoes/<int:pk>/aprovar/",
        views.aprovar_solicitacao,
        name="aprovar_solicitacao",
    ),
    path(
        "solicitacoes/<int:pk>/reprovar/",
        views.reprovar_solicitacao,
        name="reprovar_solicitacao",
    ),
    path(
        "solicitacoes/<int:pk>/atender/",
        views.atender_solicitacao,
        name="atender_solicitacao",
    ),
    # Entrega
    path("<int:pk>/", views.DetalheEntregaView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", views.AtualizarEntregaView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.ExcluirEntregaView.as_view(), name="excluir"),
]
