from django.db import models
from django.utils import timezone

class Solicitacao(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        APROVADA = "APROVADA", "Aprovada"
        REPROVADA = "REPROVADA", "Reprovada"
        ATENDIDA = "ATENDIDA", "Atendida"
        CANCELADA = "CANCELADA", "Cancelada"

    colaborador = models.ForeignKey(
        "app_colaboradores.Colaborador",
        on_delete=models.PROTECT,
        related_name="solicitacoes",
    )
    epi = models.ForeignKey(
        "app_epis.EPI",
        on_delete=models.PROTECT,
        related_name="solicitacoes",
    )
    quantidade = models.PositiveIntegerField(default=1)
    observacao = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDENTE
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Solicitação #{self.pk} - {self.colaborador} - {self.epi} ({self.quantidade})"


class Entrega(models.Model):
    class Status(models.TextChoices):
        ENTREGUE = "ENTREGUE", "Entregue"
        DEVOLVIDO = "DEVOLVIDO", "Devolvido"
        CANCELADO = "CANCELADO", "Cancelado"

    colaborador = models.ForeignKey(
        "app_colaboradores.Colaborador",
        on_delete=models.PROTECT,
        related_name="entregas",
    )
    epi = models.ForeignKey(
        "app_epis.EPI",
        on_delete=models.PROTECT,
        related_name="entregas",
    )
    solicitacao = models.ForeignKey(
        "app_entregas.Solicitacao",
        on_delete=models.PROTECT,
        related_name="entregas",
        null=True,
        blank=True,  # legado sem vínculo
    )
    data_entrega = models.DateTimeField(default=timezone.now)
    quantidade = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ENTREGUE
    )
    observacao = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data_entrega"]

    def __str__(self):
        return f"{self.epi} → {self.colaborador} ({self.quantidade})"
