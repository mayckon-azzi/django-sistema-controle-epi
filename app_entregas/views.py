from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Entrega
from app_colaboradores.models import Colaborador
from app_epis.models import EPI
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import EntregaForm
from django.views.generic import UpdateView, DeleteView, DetailView


def lista(request):
    q = request.GET.get("q", "").strip()
    colaborador_id = request.GET.get("colaborador", "")
    epi_id = request.GET.get("epi", "")
    status = request.GET.get("status", "")

    qs = Entrega.objects.select_related("colaborador", "epi", "epi__categoria")

    if q:
        qs = qs.filter(
            Q(colaborador__nome__icontains=q) |
            Q(colaborador__email__icontains=q) |
            Q(colaborador__matricula__icontains=q) |
            Q(epi__nome__icontains=q) |
            Q(epi__codigo__icontains=q)
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

class CriarEntregaView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    model = Entrega
    form_class = EntregaForm
    template_name = 'app_entregas/pages/form.html'
    success_url = reverse_lazy('app_entregas:lista')

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "Entrega registrada com sucesso.")
        return resp
    
class AtualizarEntregaView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    model = Entrega
    form_class = EntregaForm
    template_name = 'app_entregas/pages/form.html'
    success_url = reverse_lazy('app_entregas:lista')

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "Entrega atualizada com sucesso.")
        return resp

class ExcluirEntregaView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    model = Entrega
    template_name = 'app_entregas/pages/confirm_delete.html'
    success_url = reverse_lazy('app_entregas:lista')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Entrega excluída com sucesso.")
        return super().delete(request, *args, **kwargs)
    
class DetalheEntregaView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    model = Entrega
    template_name = 'app_entregas/pages/detail.html'
    context_object_name = 'entrega'