from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from .models import Colaborador

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ['nome','email','matricula','cargo','setor','telefone','ativo']
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Nome completo", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "email@empresa.com", "class": "form-control"}),
            "matricula": forms.TextInput(attrs={"placeholder": "Ex.: C123", "class": "form-control"}),
            "cargo": forms.TextInput(attrs={"placeholder": "Opcional", "class": "form-control"}),
            "setor": forms.TextInput(attrs={"placeholder": "Opcional", "class": "form-control"}),
            "telefone": forms.TextInput(attrs={"placeholder": "Opcional", "class": "form-control"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_matricula(self):
        return (self.cleaned_data["matricula"] or "").strip().upper()


class ColaboradorAdminForm(ColaboradorForm):
    # Permite atribuir grupos e, se não houver usuário, criar um na hora.
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), required=False, label="Grupos do usuário",
        widget=forms.SelectMultiple(attrs={"class": "form-select"})
    )
    criar_usuario = forms.BooleanField(required=False, initial=False, label="Criar usuário de acesso?", widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    username = forms.CharField(required=False, max_length=150, label="Username", widget=forms.TextInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(required=False, label="Senha", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(required=False, label="Confirmar senha", widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta(ColaboradorForm.Meta):
        fields = ColaboradorForm.Meta.fields  # mantém campos do colaborador

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        u = getattr(self.instance, "user", None)
        if u:
            # Se já tem usuário vinculado, escondemos os campos de criação
            self.fields["criar_usuario"].widget = forms.HiddenInput()
            self.fields["username"].widget = forms.HiddenInput()
            self.fields["password1"].widget = forms.HiddenInput()
            self.fields["password2"].widget = forms.HiddenInput()
            self.fields["groups"].initial = u.groups.all()

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

        # Se já tem usuário, apenas sincroniza os grupos
        if u:
            if "groups" in self.cleaned_data:
                u.groups.set(self.cleaned_data["groups"])
                if commit:
                    u.save()
            return colab

        # Se marcou para criar usuário agora
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


class RegisterForm(UserCreationForm):
	email = forms.EmailField(required=True)
	nome = forms.CharField(max_length=150, required=True)
	matricula = forms.CharField(max_length=30, required=True)

	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

	def save(self, commit=True):
			user = super().save(commit=commit)
			if commit:
					# cria/vincula Colaborador ao novo usuário
					colab, _ = Colaborador.objects.get_or_create(
							email=self.cleaned_data['email'],
							defaults={
									'nome': self.cleaned_data['nome'],
									'matricula': self.cleaned_data['matricula'],
									'ativo': True,
									'user': user,
							},
					)
					if not colab.user:
							colab.user = user
							colab.save()

					# coloca o usuário no grupo "Colaborador" (se existir)
					try:
							g, _ = Group.objects.get_or_create(name="Colaborador")
							user.groups.add(g)
					except Exception:
							pass
			return user
