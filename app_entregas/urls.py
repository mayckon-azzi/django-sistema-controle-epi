from django.urls import path
from . import views

app_name = "app_entregas"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.CriarEntregaView.as_view(), name="criar"),
    # Solicitações
    path("solicitacoes/nova/", views.CriarSolicitacaoView.as_view(), name="criar_solicitacao"),
    path("solicitacoes/minhas/", views.MinhasSolicitacoesView.as_view(), name="minhas_solicitacoes"),
    path("<int:pk>/", views.DetalheEntregaView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", views.AtualizarEntregaView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.ExcluirEntregaView.as_view(), name="excluir"),
]
