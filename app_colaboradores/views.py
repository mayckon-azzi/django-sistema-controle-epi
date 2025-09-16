from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    ColaboradorAdminForm,
    ColaboradorForm,
    ColaboradorFotoForm,
    LoginFormBootstrap,
    RegisterForm,
)
from .models import Colaborador


class EntrarView(LoginView):
    template_name = "app_colaboradores/pages/login.html"
    form_class = LoginFormBootstrap
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.get_redirect_url()
        if next_url:
            return next_url

        user = self.request.user
        if user.has_perm("app_colaboradores.view_colaborador") or user.is_staff:
            return reverse_lazy("app_colaboradores:lista")
        if user.has_perm("app_entregas.view_solicitacao"):
            return reverse_lazy("app_entregas:lista")
        return reverse_lazy("app_core:home")


class ListaColaboradoresView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = reverse_lazy("app_colaboradores:entrar")
    permission_required = "app_colaboradores.view_colaborador"
    raise_exception = True

    model = Colaborador
    template_name = "app_colaboradores/pages/list.html"
    context_object_name = "colaboradores"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = (self.request.GET.get("q") or "").strip()
        if q:
            from django.db.models import Q

            qs = qs.filter(
                Q(nome__icontains=q)
                | Q(email__icontains=q)
                | Q(matricula__icontains=q)
                | Q(cargo__icontains=q)
                | Q(setor__icontains=q)
            )
        return qs.order_by("nome", "id")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["base_query"] = params.urlencode()
        return ctx


# CRIAR
class CriarColaboradorView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url = reverse_lazy("app_colaboradores:entrar")
    permission_required = "app_colaboradores.add_colaborador"
    raise_exception = True
    model = Colaborador
    template_name = "app_colaboradores/pages/form.html"
    success_url = reverse_lazy("app_colaboradores:criar")

    def get_form_class(self):
        u = self.request.user
        if u.is_superuser or u.groups.filter(name="Almoxarife").exists():
            return ColaboradorAdminForm
        return ColaboradorForm

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "Colaborador criado.")
        return resp


class AtualizarColaboradorView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = reverse_lazy("app_colaboradores:entrar")
    permission_required = "app_colaboradores.change_colaborador"
    raise_exception = True
    model = Colaborador
    template_name = "app_colaboradores/pages/form.html"
    success_url = reverse_lazy("app_colaboradores:lista")

    def get_form_class(self):
        u = self.request.user
        return (
            ColaboradorAdminForm
            if (u.is_superuser or u.groups.filter(name="Almoxarife").exists())
            else ColaboradorForm
        )

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, "Colaborador atualizado.")
        return resp


class ExcluirColaboradorView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    login_url = reverse_lazy("app_colaboradores:entrar")
    permission_required = "app_colaboradores.delete_colaborador"
    raise_exception = True

    model = Colaborador
    template_name = "app_colaboradores/pages/confirm_delete.html"
    success_url = reverse_lazy("app_colaboradores:lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Colaborador excluído.")
        return super().delete(request, *args, **kwargs)


def registrar(request):
    erro_banco = None
    if request.method == "POST":
        form = RegisterForm(request.POST)
        try:
            if form.is_valid():
                form.save()
                return redirect("app_colaboradores:entrar")
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
        "app_colaboradores/pages/register.html",
        {"form": form, "erro_banco": erro_banco},
    )


class PerfilView(LoginRequiredMixin, TemplateView):
    """
    - /colaboradores/perfil/         -> perfil do usuário logado (com auto-vínculo por e-mail)
    - /colaboradores/perfil/<pk>/    -> requer permissão 'view_colaborador', exceto se for o próprio
    """

    login_url = reverse_lazy("app_colaboradores:entrar")
    template_name = "app_colaboradores/pages/perfil.html"

    # --- helpers -------------------------------------------------------------
    def _get_or_autolink_user_colab(self):
        """Retorna o Colaborador do usuário. Se não houver, tenta vincular por e-mail (único)."""
        user = self.request.user
        colab = Colaborador.objects.filter(user=user).first()
        if colab:
            return colab

        email = (user.email or "").strip()
        if email:
            qs = Colaborador.objects.filter(user__isnull=True, email__iexact=email)
            if qs.count() == 1:
                colab = qs.first()
                colab.user = user
                colab.save(update_fields=["user"])
                messages.info(
                    self.request,
                    "Vinculamos automaticamente seu usuário ao perfil de colaborador existente.",
                )
                return colab
        return None

    def _resolve_colab(self):
        # cache caso já resolvido no dispatch
        if hasattr(self, "_colab"):
            return self._colab

        pk = self.kwargs.get("pk")
        my_colab = Colaborador.objects.filter(user=self.request.user).first()

        # Se pediu um PK e é o próprio, libera sem exigir view_colaborador
        if pk is not None and my_colab and my_colab.pk == pk:
            return my_colab

        if pk is not None:
            if not self.request.user.has_perm("app_colaboradores.view_colaborador"):
                raise PermissionDenied
            return get_object_or_404(Colaborador, pk=pk)

        # Sem PK: perfil próprio (já garantido no dispatch)
        return get_object_or_404(Colaborador, user=self.request.user)

    # --- dispatch / GET / POST ----------------------------------------------
    def dispatch(self, request, *args, **kwargs):
        # Quando acessa /perfil/ (sem pk), garanta que temos um Colaborador
        if "pk" not in kwargs:
            colab = self._get_or_autolink_user_colab()
            if not colab:
                if request.user.has_perm("app_colaboradores.add_colaborador"):
                    messages.info(
                        request,
                        "Seu usuário ainda não possui um perfil de colaborador. "
                        "Crie seu perfil para continuar.",
                    )
                    return redirect("app_colaboradores:criar")
                messages.error(
                    request,
                    "Seu usuário não possui um perfil de colaborador. "
                    "Solicite a um administrador para criar seu perfil.",
                )
                return redirect("app_core:home")
            # cache para reaproveitar
            self._colab = colab

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        colab = self._resolve_colab()
        ctx["colaborador"] = colab
        ctx["foto_form"] = ColaboradorFotoForm(instance=colab)
        return ctx

    def post(self, request, *args, **kwargs):
        colab = self._resolve_colab()

        if "remover" in request.POST:
            if colab.foto:
                colab.foto.delete(save=False)
                colab.foto = None
                colab.save()
                messages.success(request, "Foto removida com sucesso.")
            else:
                messages.info(request, "Este perfil não possui foto.")
            return redirect(
                (
                    "app_colaboradores:perfil"
                    if "pk" not in self.kwargs
                    else "app_colaboradores:perfil_pk"
                ),
                **({"pk": colab.pk} if "pk" in self.kwargs else {}),
            )

        form = ColaboradorFotoForm(request.POST, request.FILES, instance=colab)
        if form.is_valid():
            form.save()
            messages.success(request, "Foto atualizada com sucesso.")
            return redirect(
                (
                    "app_colaboradores:perfil"
                    if "pk" not in self.kwargs
                    else "app_colaboradores:perfil_pk"
                ),
                **({"pk": colab.pk} if "pk" in self.kwargs else {}),
            )

        messages.error(request, "Não foi possível atualizar a foto.")
        return self.get(request, *args, **kwargs)
