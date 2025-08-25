from django.urls import path
from . import views 

app_name = "app_colaboradores"

urlpatterns = [
    path("", views.lista, name="lista")
]
