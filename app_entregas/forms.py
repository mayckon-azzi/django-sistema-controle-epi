from django import forms
from .models import Entrega

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
            raise forms.ValidationError("Quantidade deve ser ≥ 1.")
        return q
