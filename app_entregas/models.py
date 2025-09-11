from django.db import models
from django.utils import timezone

class Entrega(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        APROVADA = "APROVADA", "Aprovada"
        REPROVADA = "REPROVADA", "Reprovada"
        ATENDIDA = "ATENDIDA", "Atendida"
        CANCELADA = "CANCELADA", "Cancelada"

    colaborador = models.ForeignKey(
        "app_colaboradores.Colaborador", on_delete=models.PROTECT, related_name="entregas"
    )
    epi = models.ForeignKey(
        "app_epis.EPI", on_delete=models.PROTECT, related_name="entregas"
    )
    data_entrega = models.DateTimeField(default=timezone.now)
    quantidade = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    observacao = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.colaborador} - {self.epi} ({self.quantidade})"
