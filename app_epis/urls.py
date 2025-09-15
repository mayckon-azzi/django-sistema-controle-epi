from django.urls import path

from .views import AtualizarEPIView, CriarEPIView, ExcluirEPIView, ListaEPIView

app_name = "app_epis"

urlpatterns = [
    path("", ListaEPIView.as_view(), name="lista"),
    path("novo/", CriarEPIView.as_view(), name="criar"),
    path("<int:pk>/editar/", AtualizarEPIView.as_view(), name="editar"),
    path("<int:pk>/excluir/", ExcluirEPIView.as_view(), name="excluir"),
]
