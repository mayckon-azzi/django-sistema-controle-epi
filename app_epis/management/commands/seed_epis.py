from django.core.management.base import BaseCommand

from app_epis.models import EPI, CategoriaEPI

SEED = [
    {
        "codigo": "CAP-001",
        "nome": "Capacete de Segurança",
        "categoria": "Capacete",
        "tamanho": "U",
    },
    {
        "codigo": "LUV-010",
        "nome": "Luva Nitrílica",
        "categoria": "Luva",
        "tamanho": "M",
    },
    {
        "codigo": "OCL-200",
        "nome": "Óculos Incolor",
        "categoria": "Óculos",
        "tamanho": "U",
    },
    {"codigo": "BOT-050", "nome": "Bota PVC", "categoria": "Bota", "tamanho": "G"},
    {
        "codigo": "PAU-007",
        "nome": "Protetor Auricular",
        "categoria": "Protetor Auricular",
        "tamanho": "U",
    },
    {"codigo": "LUV-011", "nome": "Luva Vaqueta", "categoria": "Luva", "tamanho": "G"},
]


class Command(BaseCommand):
    help = "Popula EPIs de exemplo"

    def handle(self, *args, **kwargs):
        for d in SEED:
            # Primeiro, obtém ou cria a categoria
            categoria, created = CategoriaEPI.objects.get_or_create(nome=d["categoria"])

            # Depois cria o EPI com a instância da categoria
            EPI.objects.get_or_create(
                codigo=d["codigo"],
                defaults={
                    "nome": d["nome"],
                    "categoria": categoria,  # Agora é uma instância, não string
                    "tamanho": d["tamanho"],
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Total de EPIs cadastrados: {EPI.objects.count()}"))
