from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Entrega, Solicitacao


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = [
            "colaborador",
            "epi",
            "quantidade",
            "status",
            "data_prevista_devolucao",
            "data_devolucao",
            "observacao",
            "observacao_devolucao",
        ]
        widgets = {
            "colaborador": forms.Select(attrs={"class": "form-select"}),
            "epi": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={"min": 1, "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "data_prevista_devolucao": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "data_devolucao": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "observacao": forms.Textarea(
                attrs={"rows": 2, "class": "form-control", "placeholder": "Opcional"}
            ),
            "observacao_devolucao": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                    "placeholder": "Informe detalhes da devolução (opcional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ocultar "Devolvido/Danificado/Perdido" no CADASTRO (apenas no EDITAR exibem)
        hide_when_create = {
            Entrega.Status.DEVOLVIDO,
            Entrega.Status.DANIFICADO,
            Entrega.Status.PERDIDO,
        }
        if self.instance is None or self.instance.pk is None:
            self.fields["status"].choices = [
                c for c in self.fields["status"].choices if c[0] not in hide_when_create
            ]

        # Placeholders úteis
        self.fields["data_prevista_devolucao"].widget.attrs.setdefault(
            "placeholder", "Ex.: 2025-12-31 17:30"
        )
        self.fields["data_devolucao"].widget.attrs.setdefault(
            "placeholder", "Ex.: 2025-12-31 09:00"
        )

    def clean_quantidade(self):
        q = self.cleaned_data.get("quantidade") or 0
        if q < 1:
            raise ValidationError("Quantidade deve ser ≥ 1.")
        return q

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")
        dt_prev = cleaned.get("data_prevista_devolucao")
        dt_dev = cleaned.get("data_devolucao")
        now = timezone.now()

        status_norm = (str(status or "").replace(" ", "_").upper())
        # “Data prevista” precisa ser futura quando informada
        if dt_prev and dt_prev <= now:
            self.add_error(
                "data_prevista_devolucao",
                "A data prevista precisa ser posterior a agora.",
            )

        if status_norm in {"EMPRESTADO", "EM_USO"} and not dt_prev:
            self.add_error(
                "data_prevista_devolucao",
                "Informe a data prevista de devolução para este status.",
            )
            
       
        if status_norm in {"DEVOLVIDO", "DANIFICADO", "PERDIDO"}:
            if not dt_dev:
                self.add_error("data_devolucao", "Informe a data da devolução.")
            elif dt_dev < cleaned.get("data_entrega", now):
                self.add_error(
                    "data_devolucao",
                    "A data da devolução não pode ser anterior à entrega.",
                )
        return cleaned

class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ["epi", "quantidade", "observacao"]
        widgets = {
            "epi": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={"min": 1, "class": "form-control"}),
            "observacao": forms.Textarea(
                attrs={
                    "placeholder": "Justificativa/observação (opcional)",
                    "rows": 2,
                    "class": "form-control",
                }
            ),
        }

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
