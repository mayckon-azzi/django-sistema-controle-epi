from django.urls import path
from . import views

app_name = "app_epis"

urlpatterns = [
    path("", views.lista, name="lista"),
]
