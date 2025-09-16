from django import forms
from django.db.utils import OperationalError, ProgrammingError

from .models import EPI, CategoriaEPI

# Categorias mais comuns
DEFAULT_CATEGORIAS = [
    "Luvas de proteção",
    "Óculos de proteção",
    "Capacete de segurança",
    "Protetor auricular",
    "Máscaras",
    "Calçado de segurança",
    "Protetor facial",
    "Avental",
    "Creme protetor",
    "Uniforme (calça/jaqueta)",
    "Mangotes",
]


def _bootstrapify(widget: forms.Widget, extra_role_switch=False):
    base = widget.attrs.get("class", "")
    if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
        widget.attrs["class"] = (base + " form-check-input").strip()
        if extra_role_switch:
            widget.attrs["role"] = "switch"
    elif isinstance(widget, forms.Select):
        widget.attrs["class"] = (base + " form-select").strip()
    else:
        widget.attrs["class"] = (base + " form-control").strip()
    widget.attrs.setdefault("autocomplete", "off")


def _ensure_default_categories():
    """Cria categorias padrão se necessário (ignora com segurança em migrações iniciais)."""
    try:
        for nome in DEFAULT_CATEGORIAS:
            CategoriaEPI.objects.get_or_create(nome=nome)
    except (OperationalError, ProgrammingError):
        pass


class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = [
            "nome",
            "codigo",
            "categoria",
            "tamanho",
            "ativo",
            "estoque",
            "estoque_minimo",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"placeholder": "Ex.: LUV-010"}),
            "nome": forms.TextInput(attrs={"placeholder": "Nome do EPI"}),
            "tamanho": forms.Select(),
            "estoque": forms.NumberInput(attrs={"min": 0, "step": "1", "inputmode": "numeric"}),
            "estoque_minimo": forms.NumberInput(
                attrs={"min": 0, "step": "1", "inputmode": "numeric"}
            ),
            "ativo": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        _ensure_default_categories()
        try:
            self.fields["categoria"].queryset = CategoriaEPI.objects.order_by("nome")
            if not self.instance.pk:
                first = self.fields["categoria"].queryset.first()
                if first:
                    self.initial.setdefault("categoria", first.pk)
        except (OperationalError, ProgrammingError):
            pass

        for name, field in self.fields.items():
            _bootstrapify(field.widget, extra_role_switch=(name == "ativo"))

    def clean(self):
        cleaned = super().clean()
        est = cleaned.get("estoque")
        min_ = cleaned.get("estoque_minimo")
        # marque o campo correto como inválido
        if est is not None and est < 0:
            self.add_error("estoque", "Valores não podem ser negativos.")
        if min_ is not None and min_ < 0:
            self.add_error("estoque_minimo", "Valores não podem ser negativos.")
        return cleaned
