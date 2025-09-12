from django import forms
from django.core.exceptions import ValidationError
from .models import Entrega, Solicitacao

class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ["colaborador", "epi", "quantidade", "status", "observacao"]
        widgets = {
            "quantidade": forms.NumberInput(attrs={"min": 1}),
            "observacao": forms.TextInput(attrs={"placeholder": "Opcional"}),
        }

    def clean_quantidade(self):
        q = self.cleaned_data["quantidade"]
        if q < 1:
            raise ValidationError("Quantidade deve ser ≥ 1.")
        return q

    def clean(self):
        cleaned = super().clean()
        colab = cleaned.get("colaborador")
        epi = cleaned.get("epi")
        status = cleaned.get("status")
        obs = (cleaned.get("observacao") or "").strip()

        if status == Entrega.Status.DEVOLVIDO and not obs:
            self.add_error("observacao", "Informe o motivo/observação para devolução.")
        if colab and not colab.ativo:
            self.add_error("colaborador", "Colaborador inativo — não é possível registrar entrega.")
        if epi and not epi.ativo:
            self.add_error("epi", "EPI inativo — não é possível registrar entrega.")
        return cleaned


class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ["epi", "quantidade", "justificativa"]

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
