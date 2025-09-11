from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import EPI, CategoriaEPI
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import EPIForm
from django.views.generic import UpdateView, DeleteView
from django.db.models import ProtectedError

def lista(request):
    q = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "")

    qs = EPI.objects.select_related("categoria").all()
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(codigo__icontains=q) | Q(categoria__nome__icontains=q))
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "epis": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "q": q,
        "categoria_id": categoria_id,
        "categorias": CategoriaEPI.objects.all(),
    }
    return render(request, "app_epis/pages/list.html", context)

class CriarEPIView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    model = EPI
    form_class = EPIForm
    template_name = 'app_epis/pages/form.html'
    success_url = reverse_lazy('app_epis:lista')

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "EPI criado com sucesso.")
        return resp
    
class AtualizarEPIView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    model = EPI
    form_class = EPIForm
    template_name = 'app_epis/pages/form.html'
    success_url = reverse_lazy('app_epis:lista')

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "EPI atualizado com sucesso.")
        return resp

class ExcluirEPIView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    model = EPI
    template_name = 'app_epis/pages/confirm_delete.html'
    success_url = reverse_lazy('app_epis:lista')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            resp = super().delete(request, *args, **kwargs)
            messages.success(self.request, "EPI excluído com sucesso.")
            return resp
        except ProtectedError:
            messages.error(self.request, "Não é possível excluir este EPI porque há entregas associadas.")
            return redirect(self.success_url)