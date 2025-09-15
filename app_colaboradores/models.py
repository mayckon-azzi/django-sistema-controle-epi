from django.contrib.auth.models import User
from django.db import models


class Colaborador(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="colaborador",
    )
    nome = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    matricula = models.CharField(max_length=30, unique=True)
    cargo = models.CharField(max_length=80, blank=True)
    setor = models.CharField(max_length=80, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to="colaboradores/%Y/%m/", blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.matricula})"


class Meta:
    ordering = ["nome"]
