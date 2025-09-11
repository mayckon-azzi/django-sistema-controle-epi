from django.urls import path
from . import views

app_name = "app_entregas"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.CriarEntregaView.as_view(), name="criar"),
    path("<int:pk>/", views.DetalheEntregaView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", views.AtualizarEntregaView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.ExcluirEntregaView.as_view(), name="excluir"),
]
