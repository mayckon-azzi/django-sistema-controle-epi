from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy

from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import (
    CreateView, UpdateView, DeleteView, DetailView, ListView
)
from .models import Solicitacao, Entrega
from app_colaboradores.models import Colaborador
from app_epis.models import EPI
from .forms import SolicitacaoForm, EntregaForm
from django.db import transaction
from django.core.exceptions import ValidationError
from .services import movimenta_por_entrega, movimenta_por_exclusao


def lista(request):
    q = request.GET.get("q", "").strip()
    colaborador_id = request.GET.get("colaborador", "")
    epi_id = request.GET.get("epi", "")
    status = request.GET.get("status", "")

    qs = Entrega.objects.select_related("colaborador", "epi", "epi__categoria")

    if q:
        qs = qs.filter(
            Q(colaborador__nome__icontains=q)
            | Q(colaborador__email__icontains=q)
            | Q(colaborador__matricula__icontains=q)
            | Q(epi__nome__icontains=q)
            | Q(epi__codigo__icontains=q)
        )
    if colaborador_id:
        qs = qs.filter(colaborador_id=colaborador_id)
    if epi_id:
        qs = qs.filter(epi_id=epi_id)
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "entregas": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "q": q,
        "colaborador_id": colaborador_id,
        "epi_id": epi_id,
        "status": status,
        "colaboradores": Colaborador.objects.all().only("id", "nome"),
        "epis": EPI.objects.all().only("id", "nome"),
        "statuses": Entrega.Status.choices,
    }
    return render(request, "app_entregas/pages/list.html", context)


# ===== ENTREGAS (somente com permissão) =====
class CriarEntregaView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "app_entregas.add_entrega"
    raise_exception = True
    login_url = reverse_lazy("app_colaboradores:entrar")
    model = Entrega
    form_class = EntregaForm
    template_name = "app_entregas/pages/form.html"
    success_url = reverse_lazy("app_entregas:lista")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                resp = super().form_valid(form)   # salva self.object
                movimenta_por_entrega(self.object, antiga=None)
        except ValidationError as ex:
            form.add_error(None, ex.message)
            return self.form_invalid(form)
        messages.success(self.request, "Entrega registrada com sucesso.")
        return resp

class AtualizarEntregaView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "app_entregas.change_entrega"
    raise_exception = True
    login_url = reverse_lazy("app_colaboradores:entrar")
    model = Entrega
    form_class = EntregaForm
    template_name = "app_entregas/pages/form.html"
    success_url = reverse_lazy("app_entregas:lista")

    def form_valid(self, form):
        antiga = Entrega.objects.get(pk=self.get_object().pk)
        try:
            with transaction.atomic():
                resp = super().form_valid(form)  # salva self.object atualizada
                movimenta_por_entrega(self.object, antiga=antiga)
        except ValidationError as ex:
            form.add_error(None, ex.message)
            return self.form_invalid(form)
        messages.success(self.request, "Entrega atualizada com sucesso.")
        return resp


class ExcluirEntregaView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "app_entregas.delete_entrega"
    raise_exception = True
    login_url = reverse_lazy("app_colaboradores:entrar")
    model = Entrega
    template_name = "app_entregas/pages/confirm_delete.html"
    success_url = reverse_lazy("app_entregas:lista")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            with transaction.atomic():
                movimenta_por_exclusao(self.object)
                messages.success(self.request, "Entrega excluída com sucesso.")
                return super().delete(request, *args, **kwargs)
        except ValidationError as ex:
            messages.error(self.request, ex.message)
            return redirect(self.success_url)

class DetalheEntregaView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy("app_colaboradores:entrar")
    model = Entrega
    template_name = "app_entregas/pages/detail.html"
    context_object_name = "entrega"


# ===== SOLICITAÇÕES =====
class CriarSolicitacaoView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "app_entregas.add_solicitacao"
    raise_exception = True
    model = Solicitacao
    form_class = SolicitacaoForm
    template_name = "app_entregas/pages/solicitacao_form.html"
    success_url = reverse_lazy("app_entregas:minhas_solicitacoes")

    def dispatch(self, request, *args, **kwargs):
        # precisa ter Colaborador vinculado e ativo
        if not hasattr(request.user, "colaborador") or not request.user.colaborador.ativo:
            messages.error(request, "Sua conta não está vinculada a um Colaborador ativo.")
            return redirect("app_core:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.colaborador = self.request.user.colaborador
        messages.success(self.request, "Solicitação enviada com sucesso.")
        return super().form_valid(form)


class MinhasSolicitacoesView(LoginRequiredMixin, ListView):
    template_name = "app_entregas/pages/solicitacao_list.html"
    context_object_name = "solicitacoes"
    paginate_by = 10

    def get_queryset(self):
        if not hasattr(self.request.user, "colaborador"):
            return Solicitacao.objects.none()
        return Solicitacao.objects.filter(
            colaborador=self.request.user.colaborador
        ).select_related("epi")


# ===== GERENCIAR (almoxarife) =====
class SolicitacoesGerenciarView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "app_entregas.change_solicitacao"
    raise_exception = True
    template_name = "app_entregas/pages/solicitacao_manage_list.html"
    context_object_name = "solicitacoes"
    paginate_by = 12

    def get_queryset(self):
        qs = Solicitacao.objects.select_related("colaborador", "epi")
        status = self.request.GET.get("status") or "PENDENTE"
        if status in {"PENDENTE", "APROVADA"}:
            qs = qs.filter(status=status)
        return qs.order_by("-criado_em")
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # status permitidos para o filtro do almoxarife
        ctx["statuses_manage"] = ["PENDENTE", "APROVADA"]
        # status atualmente selecionado no filtro (com default)
        ctx["status_selected"] = self.request.GET.get("status") or "PENDENTE"
        return ctx

@require_POST
@permission_required("app_entregas.change_solicitacao", raise_exception=True)
def aprovar_solicitacao(request, pk):
    s = get_object_or_404(Solicitacao, pk=pk)
    if s.status != Solicitacao.Status.PENDENTE:
        messages.warning(request, "Somente solicitações PENDENTES podem ser aprovadas.")
        return redirect("app_entregas:solicitacoes_gerenciar")
    s.status = Solicitacao.Status.APROVADA
    s.save(update_fields=["status"])
    messages.success(request, "Solicitação aprovada.")
    return redirect("app_entregas:solicitacoes_gerenciar")


@require_POST
@permission_required("app_entregas.change_solicitacao", raise_exception=True)
def reprovar_solicitacao(request, pk):
    s = get_object_or_404(Solicitacao, pk=pk)
    if s.status != Solicitacao.Status.PENDENTE:
        messages.warning(request, "Somente solicitações PENDENTES podem ser reprovadas.")
        return redirect("app_entregas:solicitacoes_gerenciar")
    s.status = Solicitacao.Status.REPROVADA
    s.save(update_fields=["status"])
    messages.success(request, "Solicitação reprovada.")
    return redirect("app_entregas:solicitacoes_gerenciar")


@login_required
@permission_required("app_entregas.change_solicitacao", raise_exception=True)
def atender_solicitacao(request, pk):
    s = get_object_or_404(Solicitacao.objects.select_related("colaborador", "epi"), pk=pk)
    if s.status not in {Solicitacao.Status.APROVADA, Solicitacao.Status.PENDENTE}:
        messages.warning(request, "Apenas solicitações PENDENTES/APROVADAS podem ser atendidas.")
        return redirect("app_entregas:solicitacoes_gerenciar")

    if request.method == "POST":
        try:
            with transaction.atomic():
                e = Entrega.objects.create(
                    colaborador=s.colaborador,
                    epi=s.epi,
                    quantidade=s.quantidade,
                    status=Entrega.Status.ENTREGUE,
                    observacao=f"Atendida a solicitação #{s.pk}",
                    data_entrega=timezone.now(),
                    solicitacao=s,
                )
                movimenta_por_entrega(e, antiga=None)
                s.status = Solicitacao.Status.ATENDIDA
                s.save(update_fields=["status"])
        except ValidationError as ex:
            messages.error(request, f"Não foi possível atender: {ex.message}")
            return redirect("app_entregas:solicitacoes_gerenciar")

        messages.success(request, f"Solicitação atendida. Entrega #{e.pk} criada.")
        return redirect("app_entregas:lista")

    return render(request, "app_entregas/pages/solicitacao_atender_confirm.html", {"s": s})

