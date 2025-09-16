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
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDENTE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Solicitação #{self.pk} - {self.colaborador} - {self.epi} ({self.quantidade})"


class Entrega(models.Model):
    class Status(models.TextChoices):
        EMPRESTADO = "EMPRESTADO", "Emprestado"
        EM_USO = "EM_USO", "Em uso"
        FORNECIDO = "FORNECIDO", "Fornecido"
        DEVOLVIDO = "DEVOLVIDO", "Devolvido"
        DANIFICADO = "DANIFICADO", "Danificado"
        PERDIDO = "PERDIDO", "Perdido"

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
        blank=True,
    )

    # Datas
    data_entrega = models.DateTimeField(default=timezone.now)
    data_prevista_devolucao = models.DateTimeField(null=True, blank=True)
    data_devolucao = models.DateTimeField(null=True, blank=True)

    # Dados
    quantidade = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EMPRESTADO)
    observacao = models.CharField("Observação", max_length=255, blank=True)
    observacao_devolucao = models.CharField("Observação na devolução", max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data_entrega"]

    def __str__(self):
        return f"{self.epi} → {self.colaborador} ({self.quantidade})"
