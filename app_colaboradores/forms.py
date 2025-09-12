from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Colaborador

class ColaboradorForm(forms.ModelForm):
	class Meta:
		model = Colaborador
		fields = ['nome','email','matricula','cargo','setor','telefone','ativo']
		widgets = {
				"nome": forms.TextInput(attrs={"placeholder": "Nome completo"}),
				"email": forms.EmailInput(attrs={"placeholder": "email@empresa.com"}),
				"matricula": forms.TextInput(attrs={"placeholder": "Ex.: C123"}),
				"cargo": forms.TextInput(attrs={"placeholder": "Opcional"}),
				"setor": forms.TextInput(attrs={"placeholder": "Opcional"}),
				"telefone": forms.TextInput(attrs={"placeholder": "Opcional"}),
		}
		
	def clean_matricula(self):
			return self.cleaned_data["matricula"].strip().upper()
	
class ColaboradorAdminForm(ColaboradorForm):
	groups = forms.ModelMultipleChoiceField(
			queryset=Group.objects.all(), required=False, label="Grupos do usuário",
			help_text="Atribui grupos ao usuário vinculado a este colaborador."
	)

	class Meta(ColaboradorForm.Meta):
			fields = ColaboradorForm.Meta.fields  # campos do colaborador

	def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			u = getattr(self.instance, "user", None)
			if u:
					self.fields["groups"].initial = u.groups.all()
			else:
					# sem usuário vinculado, não faz sentido mostrar grupos
					self.fields.pop("groups", None)

	def save(self, commit=True):
			colab = super().save(commit=commit)
			u = getattr(colab, "user", None)
			if u and "groups" in self.cleaned_data:
					u.groups.set(self.cleaned_data["groups"])
					if commit:
							u.save()
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
