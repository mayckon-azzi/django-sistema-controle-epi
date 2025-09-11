from django import forms
from .models import Solicitacao
from django.core.exceptions import ValidationError


class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ["epi", "quantidade", "observacao"]

    def clean_quantidade(self):
        q = self.cleaned_data["quantidade"]
        if q < 1:
            raise ValidationError("Quantidade deve ser ≥ 1.")
        return q

    def clean_epi(self):
        e = self.cleaned_data["epi"]
        if not e.ativo:
            raise ValidationError("EPI inativo não pode ser solicitado.")
        return e
    

