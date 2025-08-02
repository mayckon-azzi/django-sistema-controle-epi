from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('destinos/', views.destinos, name='destinos'),
    path('galeria/', views.galeria, name='galeria'),
    path('sobre/', views.sobre, name='sobre'),
]
