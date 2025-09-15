# app_entregas/admin.py
from django.contrib import admin

from .models import Entrega, Solicitacao


@admin.register(Solicitacao)
class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "criado_em", "colaborador", "epi", "quantidade", "status")
    list_filter = ("status", "epi")
    search_fields = (
        "colaborador__nome",
        "colaborador__email",
        "epi__nome",
        "epi__codigo",
    )
    date_hierarchy = "criado_em"
    autocomplete_fields = ("colaborador", "epi")


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "data_entrega",
        "colaborador",
        "epi",
        "quantidade",
        "status",
        "solicitacao",
    )
    list_filter = ("status", "epi")
    search_fields = (
        "colaborador__nome",
        "colaborador__email",
        "epi__nome",
        "epi__codigo",
    )
    date_hierarchy = "data_entrega"
    autocomplete_fields = ("colaborador", "epi", "solicitacao")
