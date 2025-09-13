from django import forms
from .models import EPI


class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = ["nome", "codigo", "categoria", "tamanho", "ativo", "estoque", "estoque_minimo"]
        widgets = {
            "codigo": forms.TextInput(attrs={"placeholder": "Ex.: LUV-010"}),
            "nome": forms.TextInput(attrs={"placeholder": "Nome do EPI"}),
            "estoque": forms.NumberInput(attrs={"min": 0}),
            "estoque_minimo": forms.NumberInput(attrs={"min": 0}),
            "tamanho": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            w = field.widget
            base = w.attrs.get("class", "")

            if isinstance(w, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                w.attrs["class"] = (base + " form-check-input").strip()
            elif isinstance(w, forms.Select):
                w.attrs["class"] = (base + " form-select").strip()
            else:
                w.attrs["class"] = (base + " form-control").strip()

            w.attrs.setdefault("autocomplete", "off")

        self.fields["ativo"].widget.attrs.update({"role": "switch"})

        for num_name in ("estoque", "estoque_minimo"):
            if num_name in self.fields:
                self.fields[num_name].widget.attrs.setdefault("step", "1")
                self.fields[num_name].widget.attrs.setdefault("inputmode", "numeric")

    def clean(self):
        cleaned = super().clean()
        est = cleaned.get("estoque") or 0
        min_ = cleaned.get("estoque_minimo") or 0
        if min_ < 0 or est < 0:
            self.add_error("estoque", "Valores não podem ser negativos.")
        return cleaned
