from django.urls import path
from django.contrib.auth.views import LogoutView

from app_core import views
from .views import (
    EntrarView,
    ListaColaboradoresView,
    CriarColaboradorView,
    AtualizarColaboradorView,
    ExcluirColaboradorView,
    PerfilView,
    registrar,
)

app_name = "app_colaboradores"

urlpatterns = [
    # Autenticação
    path("login/", EntrarView.as_view(), name="entrar"),
    path("sair/", LogoutView.as_view(next_page="app_core:home"), name="sair"),
    path("registrar/", registrar, name="registrar"),
    
    # CRUD Colaboradores
    path("", ListaColaboradoresView.as_view(), name="lista"),
    path("novo/", CriarColaboradorView.as_view(), name="criar"),
    path("<int:pk>/editar/", AtualizarColaboradorView.as_view(), name="editar"),
    path("<int:pk>/excluir/", ExcluirColaboradorView.as_view(), name="excluir"),
    path("perfil/", PerfilView.as_view(), name="perfil"),
    path("perfil/<int:pk>/", PerfilView.as_view(), name="perfil_pk"),
]
