# app_colaboradores/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.crypto import get_random_string

from .models import Colaborador


def _bootstrapify_fields(form):
    """
    Aplica classes Bootstrap nos widgets, sem sobrescrever classes existentes
    e ignorando HiddenInput.
    """
    for name, field in form.fields.items():
        w = field.widget
        if isinstance(w, forms.HiddenInput):
            continue

        base = w.attrs.get("class", "")

        if isinstance(w, forms.CheckboxInput):
            w.attrs["class"] = (base + " form-check-input").strip()
            if name in {"ativo", "criar_usuario"}:
                w.attrs["role"] = "switch"

        elif isinstance(w, (forms.Select, forms.SelectMultiple)):
            w.attrs["class"] = (base + " form-select").strip()

        else:
            w.attrs["class"] = (base + " form-control").strip()


# ===================================================================
#                           Colaborador
# ===================================================================


class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["nome", "email", "matricula", "cargo", "setor", "telefone", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Nome completo"}),
            "email": forms.EmailInput(attrs={"placeholder": "email@empresa.com"}),
            "matricula": forms.TextInput(attrs={"placeholder": "Ex.: C123"}),
            "cargo": forms.TextInput(attrs={"placeholder": "Opcional"}),
            "setor": forms.TextInput(attrs={"placeholder": "Opcional"}),
            "telefone": forms.TextInput(attrs={"placeholder": "Opcional"}),
            "ativo": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrapify_fields(self)

    def clean_matricula(self):
        value = (self.cleaned_data.get("matricula") or "").strip().upper()
        if not value:
            return value
        qs = Colaborador.objects.filter(matricula__iexact=value)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Já existe um colaborador com esta matrícula.")
        return value


class ColaboradorAdminForm(ColaboradorForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Grupos do usuário",
        widget=forms.SelectMultiple(),
    )
    criar_usuario = forms.BooleanField(
        required=False,
        initial=False,
        label="Criar usuário de acesso?",
        widget=forms.CheckboxInput(),
    )
    username = forms.CharField(
        required=False, max_length=150, label="Username", widget=forms.TextInput()
    )
    password1 = forms.CharField(required=False, label="Senha", widget=forms.PasswordInput())
    password2 = forms.CharField(
        required=False, label="Confirmar senha", widget=forms.PasswordInput()
    )

    class Meta(ColaboradorForm.Meta):
        fields = ColaboradorForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        u = getattr(self.instance, "user", None)
        if u:
            self.fields["criar_usuario"].widget = forms.HiddenInput()
            self.fields["username"].widget = forms.HiddenInput()
            self.fields["password1"].widget = forms.HiddenInput()
            self.fields["password2"].widget = forms.HiddenInput()
            self.fields["groups"].initial = u.groups.all()

        _bootstrapify_fields(self)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("username"):
            cleaned["username"] = cleaned["username"].strip()

        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 or p2:
            if not p1 or not p2:
                self.add_error("password1", "Informe e confirme a senha.")
            elif p1 != p2:
                self.add_error("password2", "As senhas não conferem.")

        if cleaned.get("criar_usuario") and cleaned.get("username"):
            if User.objects.filter(username=cleaned["username"]).exists():
                self.add_error("username", "Este username já existe.")

        return cleaned

    def _build_unique_username(self):
        """
        Gera um username único a partir de:
        1) username informado; 2) matrícula; 3) prefixo do e-mail; 4) 'user'
        """
        base = (self.cleaned_data.get("username") or "").strip()
        if not base:
            base = (self.cleaned_data.get("matricula") or "").strip()
        if not base:
            email = (self.cleaned_data.get("email") or "").strip()
            base = email.split("@")[0] if email else "user"

        candidate = base
        i = 1
        while User.objects.filter(username=candidate).exists():
            candidate = f"{base}{i}"
            i += 1
        return candidate

    @transaction.atomic
    def save(self, commit=True):
        colab = super().save(commit=commit)
        u = getattr(colab, "user", None)

        if u:
            email = self.cleaned_data.get("email")
            if email is not None:
                u.email = email

            ativo = self.cleaned_data.get("ativo")
            if ativo is not None:
                u.is_active = bool(ativo)

            if "groups" in self.cleaned_data:
                u.groups.set(self.cleaned_data["groups"])

            if commit:
                u.save()
            return colab

        if self.cleaned_data.get("criar_usuario"):
            username = self._build_unique_username()
            password = self.cleaned_data.get("password1") or get_random_string(12)
            u = User.objects.create_user(
                username=username,
                email=self.cleaned_data.get("email") or colab.email,
                password=password,
            )
            u.is_active = bool(self.cleaned_data.get("ativo", True))

            if "groups" in self.cleaned_data:
                u.groups.set(self.cleaned_data["groups"])

            if commit:
                u.save()

            colab.user = u
            if commit:
                colab.save(update_fields=["user"])

        return colab


# ===================================================================
#                           Registro de Usuário
# ===================================================================


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput())
    nome = forms.CharField(max_length=150, required=True, widget=forms.TextInput())
    matricula = forms.CharField(max_length=30, required=True, widget=forms.TextInput())

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.setdefault("placeholder", "usuário")
        self.fields["email"].widget.attrs.setdefault("placeholder", "email@empresa.com")
        self.fields["password1"].widget.attrs.setdefault("placeholder", "Senha")
        self.fields["password2"].widget.attrs.setdefault("placeholder", "Confirmar senha")
        self.fields["nome"].widget.attrs.setdefault("placeholder", "Nome completo")
        self.fields["matricula"].widget.attrs.setdefault("placeholder", "Ex.: C123")
        _bootstrapify_fields(self)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            colab, _ = Colaborador.objects.get_or_create(
                email=self.cleaned_data["email"],
                defaults={
                    "nome": self.cleaned_data["nome"],
                    "matricula": (self.cleaned_data["matricula"] or "").strip().upper(),
                    "ativo": True,
                    "user": user,
                },
            )
            if not colab.user:
                colab.user = user
                colab.save(update_fields=["user"])

            try:
                g, _ = Group.objects.get_or_create(name="Colaborador")
                user.groups.add(g)
            except Exception:
                pass
        return user


class LoginFormBootstrap(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Seu usuário"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "••••••••", "id": "id_password"}
        )


class ColaboradorFotoForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["foto"]
        widgets = {
            "foto": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"})
        }
