from django.urls import path
from . import views

app_name = "app_entregas"

urlpatterns = [
    path("", views.lista, name="lista"),
]
