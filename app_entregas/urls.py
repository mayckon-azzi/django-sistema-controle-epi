from django.urls import path
from . import views

app_name = "app_entregas"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("novo/", views.CriarEntregaView.as_view(), name="criar"),
]
