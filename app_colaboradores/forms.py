from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group, User

from .models import Colaborador


def _bootstrapify_fields(form):
    """
    Adiciona classes Bootstrap apropriadas a todos os widgets do form,
    sem sobrescrever classes já definidas, e sem aplicar em HiddenInput.
    - Checkbox -> form-check-input (com role="switch" se for booleano tipo "ativo")
    - Select/SelectMultiple -> form-select
    - Demais -> form-control
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
        return (self.cleaned_data["matricula"] or "").strip().upper()


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
        u = getattr(self.instance, "user", None)
        if not u and cleaned.get("criar_usuario"):
            username = (cleaned.get("username") or "").strip()
            p1, p2 = cleaned.get("password1"), cleaned.get("password2")
            if not username:
                self.add_error("username", "Informe o username.")
            elif User.objects.filter(username=username).exists():
                self.add_error("username", "Este username já existe.")
            if not p1 or not p2:
                self.add_error("password1", "Informe e confirme a senha.")
            elif p1 != p2:
                self.add_error("password2", "As senhas não conferem.")
        return cleaned

    def save(self, commit=True):
        colab = super().save(commit=commit)
        u = getattr(colab, "user", None)

        if u:
            if "groups" in self.cleaned_data:
                u.groups.set(self.cleaned_data["groups"])
                if commit:
                    u.save()
            return colab

        if self.cleaned_data.get("criar_usuario"):
            u = User.objects.create_user(
                username=self.cleaned_data["username"],
                email=self.cleaned_data.get("email") or colab.email,
                password=self.cleaned_data["password1"],
            )
            colab.user = u
            if commit:
                colab.save()
            if "groups" in self.cleaned_data:
                u.groups.set(self.cleaned_data["groups"])
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
                    "matricula": self.cleaned_data["matricula"],
                    "ativo": True,
                    "user": user,
                },
            )
            if not colab.user:
                colab.user = user
                colab.save()

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
