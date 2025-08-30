from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Colaborador

class ColaboradorForm(forms.ModelForm):
	class Meta:
		model = Colaborador
		fields = ['nome', 'email', 'matricula', 'cargo', 'setor', 'telefone', 'ativo']

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
			Colaborador.objects.create(
				user=user,
				nome=self.cleaned_data['nome'],
				email=self.cleaned_data['email'],
				matricula=self.cleaned_data['matricula'],
				ativo=True,
			)
		return user
