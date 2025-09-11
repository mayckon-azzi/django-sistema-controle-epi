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

# Create your views here.
def lista(request):
    q = request.GET.get("q", "").strip()

    qs = Colaborador.objects.all()
    if q:
        qs = qs.filter(
            Q(nome__icontains=q) |
            Q(email__icontains=q) |
            Q(matricula__icontains=q) |
            Q(cargo__icontains=q) |
            Q(setor__icontains=q)
        )

    paginator = Paginator(qs, 10)  # 10 por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "colaboradores": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "q": q,
    }
    return render(request, "app_colaboradores/pages/list.html", context)

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

class AtualizarColaboradorView(LoginRequiredMixin, UpdateView):
	login_url = reverse_lazy('app_colaboradores:entrar') 
	model = Colaborador
	form_class = ColaboradorForm
	template_name = 'app_colaboradores/pages/form.html'
	success_url = reverse_lazy('app_colaboradores:lista')

class ExcluirColaboradorView(LoginRequiredMixin, DeleteView):
	login_url = reverse_lazy('app_colaboradores:entrar')  
	model = Colaborador
	template_name = 'app_colaboradores/pages/confirm_delete.html'
	success_url = reverse_lazy('app_colaboradores:lista')

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

from app_colaboradores.models import Colaborador
dados = [
    dict(nome="Ana Souza", email="ana@empresa.com", matricula="C001", cargo="Analista", setor="TI", telefone="11999990001"),
    dict(nome="Bruno Lima", email="bruno@empresa.com", matricula="C002", cargo="Técnico", setor="Manutenção", telefone="11999990002"),
    dict(nome="Carla Dias", email="carla@empresa.com", matricula="C003", cargo="Supervisor", setor="Operações", telefone="11999990003"),
    dict(nome="Diego Alves", email="diego@empresa.com", matricula="C004", cargo="Auxiliar", setor="Almoxarifado", telefone="11999990004"),
    dict(nome="Elaine Melo", email="elaine@empresa.com", matricula="C005", cargo="Engenheira", setor="Segurança", telefone="11999990005"),
    dict(nome="Fabio Neri", email="fabio@empresa.com", matricula="C006", cargo="Coordenador", setor="RH", telefone="11999990006"),
    dict(nome="Gabriela Luz", email="gabriela@empresa.com", matricula="C007", cargo="Assistente", setor="Compras", telefone="11999990007"),
    dict(nome="Henrique Reis", email="henrique@empresa.com", matricula="C008", cargo="Analista", setor="TI", telefone="11999990008"),
    dict(nome="Iara Nunes", email="iara@empresa.com", matricula="C009", cargo="Técnica", setor="Qualidade", telefone="11999990009"),
    dict(nome="João Prado", email="joao@empresa.com", matricula="C010", cargo="Estagiário", setor="TI", telefone="11999990010"),
]
for d in dados:
  Colaborador.objects.get_or_create(email=d["email"], defaults=d)
Colaborador.objects.count()

from app_colaboradores.models import Colaborador
dados = [
    dict(nome="Ana Souza", email="ana@empresa.com", matricula="C001", cargo="Analista", setor="TI", telefone="11999990001"),
    dict(nome="Bruno Lima", email="bruno@empresa.com", matricula="C002", cargo="Técnico", setor="Manutenção", telefone="11999990002"),
    dict(nome="Carla Dias", email="carla@empresa.com", matricula="C003", cargo="Supervisor", setor="Operações", telefone="11999990003"),
    dict(nome="Diego Alves", email="diego@empresa.com", matricula="C004", cargo="Auxiliar", setor="Almoxarifado", telefone="11999990004"),
    dict(nome="Elaine Melo", email="elaine@empresa.com", matricula="C005", cargo="Engenheira", setor="Segurança", telefone="11999990005"),
    dict(nome="Fabio Neri", email="fabio@empresa.com", matricula="C006", cargo="Coordenador", setor="RH", telefone="11999990006"),
    dict(nome="Gabriela Luz", email="gabriela@empresa.com", matricula="C007", cargo="Assistente", setor="Compras", telefone="11999990007"),
    dict(nome="Henrique Reis", email="henrique@empresa.com", matricula="C008", cargo="Analista", setor="TI", telefone="11999990008"),
    dict(nome="Iara Nunes", email="iara@empresa.com", matricula="C009", cargo="Técnica", setor="Qualidade", telefone="11999990009"),
    dict(nome="João Prado", email="joao@empresa.com", matricula="C010", cargo="Estagiário", setor="TI", telefone="11999990010"),
]
for d in dados:
    Colaborador.objects.get_or_create(email=d["email"], defaults=d)
print(Colaborador.objects.count())

