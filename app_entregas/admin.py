from django.contrib import admin
from .models import Solicitacao

@admin.register(Solicitacao)
class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = ("data_entrega", "colaborador", "epi", "quantidade", "status")
    list_filter = ("status", "epi__categoria")
    search_fields = ("colaborador__nome", "colaborador__email", "colaborador__matricula",
                     "epi__nome", "epi__codigo")
    autocomplete_fields = ("colaborador", "epi")
    date_hierarchy = "data_entrega"
    list_per_page = 20
