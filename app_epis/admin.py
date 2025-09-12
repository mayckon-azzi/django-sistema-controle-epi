from django.contrib import admin
from .models import CategoriaEPI, EPI

@admin.register(CategoriaEPI)
class CategoriaEPIAdmin(admin.ModelAdmin):
    search_fields = ("nome",)

@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "estoque", "categoria", "tamanho", "ativo")
    search_fields = ("codigo", "nome", "categoria__nome")
    list_filter = ("ativo", "categoria", "tamanho")
    list_per_page = 20

