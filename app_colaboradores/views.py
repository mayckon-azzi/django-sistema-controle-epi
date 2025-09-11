from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Colaborador
from .forms import ColaboradorForm, RegisterForm
from django.db.utils import OperationalError, ProgrammingError  
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.
# def lista(request):
#     q = request.GET.get("q", "").strip()

#     qs = Colaborador.objects.all()
#     if q:
#         qs = qs.filter(
#             Q(nome__icontains=q) |
#             Q(email__icontains=q) |
#             Q(matricula__icontains=q) |
#             Q(cargo__icontains=q) |
#             Q(setor__icontains=q)
#         )

#     paginator = Paginator(qs, 10)  # 10 por página
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     context = {
#         "colaboradores": page_obj.object_list,
#         "page_obj": page_obj,
#         "paginator": paginator,
#         "is_paginated": page_obj.has_other_pages(),
#         "q": q,
#     }
#     return render(request, "app_colaboradores/pages/list.html", context)

class EntrarView(LoginView):
	template_name = 'app_colaboradores/pages/login.html'
	redirect_authenticated_user = True
	def get_success_url(self):
		return reverse_lazy('app_colaboradores:lista')

class ListaColaboradoresView(LoginRequiredMixin, ListView):
	login_url = reverse_lazy('app_colaboradores:entrar')  
	model = Colaborador
	template_name = 'app_colaboradores/pages/list.html'
	context_object_name = 'colaboradores'
	paginate_by = 10
	def get_queryset(self):
		queryset = super().get_queryset()
		busca = self.request.GET.get('q', '').strip()
		if busca:
			from django.db.models import Q
			queryset = queryset.filter(
				Q(nome__icontains=busca) |
				Q(email__icontains=busca) |
				Q(matricula__icontains=busca)
			)
		return queryset

class CriarColaboradorView(LoginRequiredMixin, CreateView):
	login_url = reverse_lazy('app_colaboradores:entrar') 
	model = Colaborador
	form_class = ColaboradorForm
	template_name = 'app_colaboradores/pages/form.html'
	success_url = reverse_lazy('app_colaboradores:lista')

	def form_valid(self, form):
		resp = super().form_valid(form)
		messages.success(self.request, "Colaborador criado com sucesso.")
		return resp

class AtualizarColaboradorView(LoginRequiredMixin, UpdateView):
	login_url = reverse_lazy('app_colaboradores:entrar') 
	model = Colaborador
	form_class = ColaboradorForm
	template_name = 'app_colaboradores/pages/form.html'
	success_url = reverse_lazy('app_colaboradores:lista')

	def form_valid(self, form):
		resp = super().form_valid(form)
		messages.success(self.request, "Colaborador atualizado com sucesso.")
		return resp

class ExcluirColaboradorView(LoginRequiredMixin, DeleteView):
	login_url = reverse_lazy('app_colaboradores:entrar')  
	model = Colaborador
	template_name = 'app_colaboradores/pages/confirm_delete.html'
	success_url = reverse_lazy('app_colaboradores:lista')

	def delete(self, request, *args, **kwargs):
		messages.success(self.request, "Colaborador excluído com sucesso.")
		return super().delete(request, *args, **kwargs)

@staff_member_required(login_url="app_colaboradores:entrar")
def registrar(request):
	erro_banco = None
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		try:
			if form.is_valid():
				form.save()
				return redirect('app_colaboradores:entrar')
		except (OperationalError, ProgrammingError):
			erro_banco = (
				"Banco de dados não inicializado. "
				"Execute as migrações antes de registrar usuários: "
				"python manage.py makemigrations"
				"python manage.py migrate"
			)
	else:
		form = RegisterForm()
	return render(
		request,
		'app_colaboradores/pages/register.html',
		{'form': form, 'erro_banco': erro_banco}
	)

