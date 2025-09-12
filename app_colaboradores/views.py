from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Colaborador
from .forms import ColaboradorAdminForm, ColaboradorForm, RegisterForm
from django.db.utils import OperationalError, ProgrammingError  
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required





class EntrarView(LoginView):
	template_name = 'app_colaboradores/pages/login.html'
	redirect_authenticated_user = True
	def get_success_url(self):
		return reverse_lazy('app_colaboradores:lista')

# LISTA: só para quem tem permissão de ver colaboradores
class ListaColaboradoresView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    permission_required = "app_colaboradores.view_colaborador"
    raise_exception = True

    model = Colaborador
    template_name = 'app_colaboradores/pages/list.html'
    context_object_name = 'colaboradores'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = (self.request.GET.get('q') or '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(nome__icontains=q) | Q(email__icontains=q) |
                Q(matricula__icontains=q) | Q(cargo__icontains=q) | Q(setor__icontains=q)
            )
        return qs.order_by('nome','id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["base_query"] = params.urlencode()  
        return ctx

# CRIAR
class CriarColaboradorView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    permission_required = "app_colaboradores.add_colaborador"
    raise_exception = True
    model = Colaborador
    template_name = 'app_colaboradores/pages/form.html'
    success_url = reverse_lazy('app_colaboradores:lista')

    def get_form_class(self):
        u = self.request.user
        if u.is_superuser or u.groups.filter(name="Almoxarife").exists():
            return ColaboradorAdminForm   
        return ColaboradorForm

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "Colaborador criado.")
        return resp

# EDITAR: usa form com grupos para Almoxarife/Admin
class AtualizarColaboradorView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    permission_required = "app_colaboradores.change_colaborador"
    raise_exception = True
    model = Colaborador
    template_name = 'app_colaboradores/pages/form.html'
    success_url = reverse_lazy('app_colaboradores:lista')

    def get_form_class(self):
        u = self.request.user
        return ColaboradorAdminForm if (u.is_superuser or u.groups.filter(name="Almoxarife").exists()) else ColaboradorForm

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "Colaborador atualizado.")
        return resp
		
class ExcluirColaboradorView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    login_url = reverse_lazy('app_colaboradores:entrar')
    permission_required = "app_colaboradores.delete_colaborador"
    raise_exception = True

    model = Colaborador
    template_name = 'app_colaboradores/pages/confirm_delete.html'
    success_url = reverse_lazy('app_colaboradores:lista')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Colaborador excluído.")
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

