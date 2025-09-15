from django.shortcuts import redirect
from django.db.models import Q, F, BooleanField, Case, When, Value
from django.db.models import ProtectedError
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from .models import EPI, CategoriaEPI
from .forms import EPIForm


class ListaEPIView(ListView):
    model = EPI
    template_name = "app_epis/pages/list.html"
    context_object_name = "epis"
    paginate_by = 10

    def get_queryset(self):
        qs = EPI.objects.select_related("categoria")

        q = (self.request.GET.get("q") or "").strip()
        categoria_id = self.request.GET.get("categoria") or ""
        only_active = self.request.GET.get("ativos") == "1"
        below_min = self.request.GET.get("abaixo") == "1"
        order = self.request.GET.get("ordenar") or "nome"

        # Exibe resultados sempre (removi o "gate" que escondia sem filtros)
        if q:
            qs = qs.filter(
                Q(nome__icontains=q)
                | Q(codigo__icontains=q)
                | Q(categoria__nome__icontains=q)
            )
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        if only_active:
            qs = qs.filter(ativo=True)
        if below_min:
            qs = qs.filter(estoque__lte=F("estoque_minimo"))

        qs = qs.annotate(
            abaixo_min=Case(
                When(estoque__lte=F("estoque_minimo"), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )

        ordering = {
            "nome": "nome",
            "-nome": "-nome",
            "estoque": "estoque",
            "-estoque": "-estoque",
            "categoria": "categoria__nome",
            "codigo": "codigo",
        }.get(order, "nome")

        return qs.order_by(ordering, "id")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "q": self.request.GET.get("q", ""),
                "categoria_id": self.request.GET.get("categoria", ""),
                "categorias": CategoriaEPI.objects.all(),
                "only_active": self.request.GET.get("ativos") == "1",
                "below_min": self.request.GET.get("abaixo") == "1",
                "ordenar": self.request.GET.get("ordenar") or "nome",
                "ordenacoes": [
                    ("nome", "Nome A→Z"),
                    ("-nome", "Nome Z→A"),
                    ("estoque", "Estoque ↑"),
                    ("-estoque", "Estoque ↓"),
                    ("categoria", "Categoria"),
                    ("codigo", "Código"),
                ],
            }
        )
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["base_query"] = params.urlencode()
        return ctx


class CriarEPIView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "app_epis.add_epi"
    raise_exception = True
    login_url = reverse_lazy("app_colaboradores:entrar")
    model = EPI
    form_class = EPIForm
    template_name = "app_epis/pages/form.html"
    # Permanece na tela de cadastro após salvar
    success_url = reverse_lazy("app_epis:criar")

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "EPI criado com sucesso.")
        return resp

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Não foi possível criar o EPI. Verifique os campos destacados.",
        )
        return super().form_invalid(form)


class AtualizarEPIView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "app_epis.change_epi"
    raise_exception = True
    login_url = reverse_lazy("app_colaboradores:entrar")
    model = EPI
    form_class = EPIForm
    template_name = "app_epis/pages/form.html"

    # Permanece na tela de edição após salvar
    def get_success_url(self):
        messages.success(self.request, "EPI atualizado com sucesso.")
        return reverse("app_epis:editar", kwargs={"pk": self.object.pk})

    def form_invalid(self, form):
        messages.error(
            self.request, "Não foi possível atualizar. Verifique os campos destacados."
        )
        return super().form_invalid(form)


class ExcluirEPIView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "app_epis.delete_epi"
    raise_exception = True
    login_url = reverse_lazy("app_colaboradores:entrar")
    model = EPI
    template_name = "app_epis/pages/confirm_delete.html"
    success_url = reverse_lazy("app_epis:lista")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            resp = super().delete(request, *args, **kwargs)
            messages.success(self.request, "EPI excluído com sucesso.")
            return resp
        except ProtectedError:
            messages.error(
                self.request,
                "Não é possível excluir este EPI porque há entregas associadas.",
            )
            return redirect(self.success_url)
