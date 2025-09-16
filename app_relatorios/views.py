# app_relatorios/views.py
import csv

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Case, Count, F, IntegerField, Sum, Value, When
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from app_entregas.models import Entrega

from .forms import RelatorioEntregasForm


def _filtrar_qs(request):
    form = RelatorioEntregasForm(request.GET or None)
    qs = Entrega.objects.select_related("epi", "colaborador")
    if form.is_valid():
        cd = form.cleaned_data
        if cd.get("data_de"):
            qs = qs.filter(data_entrega__date__gte=cd["data_de"])
        if cd.get("data_ate"):
            qs = qs.filter(data_entrega__date__lte=cd["data_ate"])
        if cd.get("colaborador"):
            qs = qs.filter(colaborador=cd["colaborador"])
        if cd.get("epi"):
            qs = qs.filter(epi=cd["epi"])
        if cd.get("status"):
            qs = qs.filter(status=cd["status"])
    return form, qs.order_by("-data_entrega", "-id")


class RelatorioEntregasView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "app_entregas.view_entrega"
    raise_exception = True
    login_url = reverse_lazy("app_colaboradores:entrar")
    template_name = "app_relatorios/pages/entregas.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form, qs = _filtrar_qs(self.request)

        status_codes = [code for code, _ in Entrega.Status.choices]
        # Tudo que não é DEVOLVIDO é considerado "fora do estoque"
        fora_do_estoque = [s for s in status_codes if s != "DEVOLVIDO"]

        agg = qs.aggregate(
            registros=Count("id"),
            quantidade_total=Sum("quantidade"),
            total_entregue=Sum(
                Case(
                    When(status__in=fora_do_estoque, then=F("quantidade")),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ),
            total_devolvido=Sum(
                Case(
                    When(status="DEVOLVIDO", then=F("quantidade")),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ),
        )

        por_epi = (
            qs.values("epi__id", "epi__nome", "epi__codigo")
            .annotate(
                entregues=Sum(
                    Case(
                        When(status__in=fora_do_estoque, then=F("quantidade")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
                devolvidos=Sum(
                    Case(
                        When(status="DEVOLVIDO", then=F("quantidade")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
            )
            .order_by("epi__nome", "epi__codigo")
        )

        por_colab = (
            qs.values("colaborador__id", "colaborador__nome")
            .annotate(
                entregues=Sum(
                    Case(
                        When(status__in=fora_do_estoque, then=F("quantidade")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
                devolvidos=Sum(
                    Case(
                        When(status="DEVOLVIDO", then=F("quantidade")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
            )
            .order_by("colaborador__nome")
        )

        ctx.update(
            {
                "form": form,
                "qs": qs[:200],  # lista (slice) para não estourar tela
                "agg": agg,
                "por_epi": por_epi,
                "por_colab": por_colab,
            }
        )
        return ctx
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        raise PermissionDenied


class ExportarEntregasCSVView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "app_entregas.view_entrega"
    raise_exception = True
    login_url = reverse_lazy("app_colaboradores:entrar")
    template_name = ""

    def get(self, request, *args, **kwargs):
        form, qs = _filtrar_qs(request)
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="relatorio_entregas.csv"'
        w = csv.writer(resp, delimiter=";")
        w.writerow(
            [
                "Data Entrega",
                "Data Devolução Prevista",
                "Data Devolução",
                "Colaborador",
                "EPI",
                "Quantidade",
                "Status",
                "Observação",
            ]
        )
        for e in qs.iterator():
            w.writerow(
                [
                    e.data_entrega.strftime("%d/%m/%Y %H:%M"),
                    (
                        e.data_prevista_devolucao.strftime("%d/%m/%Y %H:%M")
                        if e.data_prevista_devolucao
                        else "-"
                    ),
                    (e.data_devolucao.strftime("%d/%m/%Y %H:%M") if e.data_devolucao else "-"),
                    e.colaborador.nome,
                    f"{e.epi.nome} ({e.epi.codigo})",
                    e.quantidade,
                    e.get_status_display(),
                    (e.observacao or "").replace("\n", " ").strip(),
                ]
            )
        return resp
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        raise PermissionDenied
