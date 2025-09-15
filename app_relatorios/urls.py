from django.urls import path

from .views import ExportarEntregasCSVView, RelatorioEntregasView

app_name = "app_relatorios"

urlpatterns = [
    path("", RelatorioEntregasView.as_view(), name="index"),
    path("exportar/", ExportarEntregasCSVView.as_view(), name="exportar"),
]
