from django.urls import path

from . import views

app_name = "app_core"

urlpatterns = [
    path("", views.home, name="home"),
    path("teste-mensagens/", views.testar_mensagens, name="teste_mensagens"),
]
