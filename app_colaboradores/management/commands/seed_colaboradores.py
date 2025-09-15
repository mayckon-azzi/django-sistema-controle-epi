from django.core.management.base import BaseCommand

from app_colaboradores.models import Colaborador

SEED = [
    {
        "nome": "Ana Souza",
        "email": "ana@empresa.com",
        "matricula": "C001",
        "cargo": "Analista",
        "setor": "TI",
        "telefone": "11999990001",
    },
    {
        "nome": "Bruno Lima",
        "email": "bruno@empresa.com",
        "matricula": "C002",
        "cargo": "Técnico",
        "setor": "Manutenção",
        "telefone": "11999990002",
    },
    {
        "nome": "Carla Dias",
        "email": "carla@empresa.com",
        "matricula": "C003",
        "cargo": "Supervisor",
        "setor": "Operações",
        "telefone": "11999990003",
    },
    {
        "nome": "Diego Alves",
        "email": "diego@empresa.com",
        "matricula": "C004",
        "cargo": "Auxiliar",
        "setor": "Almoxarifado",
        "telefone": "11999990004",
    },
    {
        "nome": "Elaine Melo",
        "email": "elaine@empresa.com",
        "matricula": "C005",
        "cargo": "Engenheira",
        "setor": "Segurança",
        "telefone": "11999990005",
    },
    {
        "nome": "Fabio Neri",
        "email": "fabio@empresa.com",
        "matricula": "C006",
        "cargo": "Coordenador",
        "setor": "RH",
        "telefone": "11999990006",
    },
    {
        "nome": "Gabriela Luz",
        "email": "gabriela@empresa.com",
        "matricula": "C007",
        "cargo": "Assistente",
        "setor": "Compras",
        "telefone": "11999990007",
    },
    {
        "nome": "Henrique Reis",
        "email": "henrique@empresa.com",
        "matricula": "C008",
        "cargo": "Analista",
        "setor": "TI",
        "telefone": "11999990008",
    },
    {
        "nome": "colaborador",
        "email": "colaborador@empresa.com",
        "matricula": "C009",
        "cargo": "Técnico",
        "setor": "Qualidade",
        "telefone": "11999990009",
    },
    {
        "nome": "almoxarife",
        "email": "almoxarife@empresa.com",
        "matricula": "C010",
        "cargo": "almoxarife",
        "setor": "TI",
        "telefone": "11999990010",
    },
]


class Command(BaseCommand):
    help = "Popula colaboradores de exemplo"

    def handle(self, *args, **kwargs):
        for d in SEED:
            Colaborador.objects.get_or_create(email=d["email"], defaults=d)
        self.stdout.write(self.style.SUCCESS("Seed de colaboradores concluído."))
