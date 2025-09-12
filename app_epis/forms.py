from django import forms
from .models import EPI

class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = ["nome", "codigo", "categoria", "ativo", "estoque", "estoque_minimo"]
        widgets = {
            "codigo": forms.TextInput(attrs={"placeholder": "Ex.: LUV-010"}),
            "nome": forms.TextInput(attrs={"placeholder": "Nome do EPI"}),
            "estoque": forms.NumberInput(attrs={"min": 0}),
            "estoque_minimo": forms.NumberInput(attrs={"min": 0}), 
        }

    def clean(self):
        cleaned = super().clean()
        est = cleaned.get("estoque") or 0
        min_ = cleaned.get("estoque_minimo") or 0
        if min_ < 0 or est < 0:
            self.add_error("estoque", "Valores não podem ser negativos.")
        return cleaned


