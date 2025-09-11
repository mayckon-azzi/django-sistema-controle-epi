from django.db import models
from django.utils import timezone

class Entrega(models.Model):
    class Status(models.TextChoices):
        ENTREGUE = "ENTREGUE", "Entregue"
        DEVOLVIDO = "DEVOLVIDO", "Devolvido"
        CANCELADO = "CANCELADO", "Cancelado"

    colaborador = models.ForeignKey(
        "app_colaboradores.Colaborador", on_delete=models.PROTECT, related_name="entregas"
    )
    epi = models.ForeignKey(
        "app_epis.EPI", on_delete=models.PROTECT, related_name="entregas"
    )
    data_entrega = models.DateTimeField(default=timezone.now)
    quantidade = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ENTREGUE)
    observacao = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data_entrega"]

    def __str__(self):
        return f"{self.epi} → {self.colaborador} ({self.quantidade})"
