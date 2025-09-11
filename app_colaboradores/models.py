from django.db import models
from django.contrib.auth.models import User
from django.db import models

class Colaborador(models.Model):
    nome = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    matricula = models.CharField(max_length=30, unique=True)
    cargo = models.CharField(max_length=80, blank=True)
    setor = models.CharField(max_length=80, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

