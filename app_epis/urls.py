from django.urls import path
from . import views

app_name = "app_epis"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.CriarEPIView.as_view(), name="criar"),
    path("<int:pk>/editar/", views.AtualizarEPIView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.ExcluirEPIView.as_view(), name="excluir"),
]
