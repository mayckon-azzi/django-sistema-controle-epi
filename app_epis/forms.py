from django import forms
from .models import EPI

class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = ["codigo", "nome", "categoria", "tamanho", "ativo"]
        widgets = {
            "codigo": forms.TextInput(attrs={"placeholder": "Ex.: LUV-010"}),
            "nome": forms.TextInput(attrs={"placeholder": "Nome do EPI"}),
        }

    def clean_codigo(self):
        return self.cleaned_data["codigo"].strip().upper()
