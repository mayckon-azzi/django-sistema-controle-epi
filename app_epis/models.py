# app_epis/models.py
from django.db import IntegrityError, models


class CategoriaEPI(models.Model):
    nome = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Categoria de EPI"
        verbose_name_plural = "Categorias de EPI"

    def __str__(self):
        return self.nome


class EPI(models.Model):
    TAMANHO_CHOICES = [
        ("PP", "PP"),
        ("P", "P"),
        ("M", "M"),
        ("G", "G"),
        ("GG", "GG"),
        ("U", "Único"),
    ]
    codigo = models.CharField("Código", max_length=30, unique=True)
    nome = models.CharField(max_length=120)
    categoria = models.ForeignKey(CategoriaEPI, on_delete=models.PROTECT, related_name="epis")
    tamanho = models.CharField(max_length=3, choices=TAMANHO_CHOICES, blank=True)
    ativo = models.BooleanField(default=True)
    estoque = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.codigo})" if self.codigo else self.nome

    def save(self, *args, **kwargs):
        if self.estoque is not None and self.estoque < 0:
            raise IntegrityError("Estoque não pode ser negativo.")
        if self.estoque_minimo is not None and self.estoque_minimo < 0:
            raise IntegrityError("Estoque mínimo não pode ser negativo.")
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="epi_estoque_nao_negativo",
                condition=models.Q(estoque__gte=0),
            ),
            models.CheckConstraint(
                name="epi_estoque_minimo_nao_negativo",
                condition=models.Q(estoque_minimo__gte=0),
            ),
        ]
