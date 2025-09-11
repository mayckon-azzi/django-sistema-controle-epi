from django.contrib import admin
from .models import Colaborador

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "matricula", "cargo", "setor", "ativo")
    search_fields = ("nome", "email", "matricula", "cargo", "setor", "telefone")
    list_filter = ("ativo", "setor", "cargo")
    list_per_page = 20
    ordering = ("nome",)
