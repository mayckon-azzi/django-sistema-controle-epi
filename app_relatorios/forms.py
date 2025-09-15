from django import forms
from app_entregas.models import Entrega
from app_colaboradores.models import Colaborador
from app_epis.models import EPI


class RelatorioEntregasForm(forms.Form):
    data_de = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    data_ate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    colaborador = forms.ModelChoiceField(
        queryset=Colaborador.objects.order_by("nome"),
        required=False,
        empty_label="Todos os colaboradores",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    epi = forms.ModelChoiceField(
        queryset=EPI.objects.order_by("nome"),
        required=False,
        empty_label="Todos os EPIs",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Todos os status")] + list(Entrega.Status.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean(self):
        cleaned = super().clean()
        de = cleaned.get("data_de")
        ate = cleaned.get("data_ate")
        if de and ate and de > ate:
            self.add_error("data_ate", "Data final deve ser maior ou igual à inicial.")
        return cleaned
