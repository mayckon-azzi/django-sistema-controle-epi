# app_epis/management/commands/seed_epis.py
from django.core.management.base import BaseCommand

from app_epis.models import EPI, CategoriaEPI

SEED = [
    {
        "codigo": "CAP-001",
        "nome": "Capacete de Segurança",
        "categoria": "Capacete",
        "tamanho": "U",
        "estoque": 25,
        "estoque_minimo": 5,
    },
    {
        "codigo": "LUV-010",
        "nome": "Luva Nitrílica",
        "categoria": "Luvas",
        "tamanho": "M",
        "estoque": 120,
        "estoque_minimo": 20,
    },
    {
        "codigo": "OCL-200",
        "nome": "Óculos Incolor",
        "categoria": "Óculos",
        "tamanho": "U",
        "estoque": 60,
        "estoque_minimo": 10,
    },
    {
        "codigo": "BOT-050",
        "nome": "Bota PVC",
        "categoria": "Bota",
        "tamanho": "G",
        "estoque": 40,
        "estoque_minimo": 8,
    },
    {
        "codigo": "PAU-007",
        "nome": "Protetor Auricular",
        "categoria": "Protetor Auricular",
        "tamanho": "U",
        "estoque": 200,
        "estoque_minimo": 30,
    },
    {
        "codigo": "LUV-011",
        "nome": "Luva Vaqueta",
        "categoria": "Luvas",
        "tamanho": "G",
        "estoque": 80,
        "estoque_minimo": 15,
    },
    {
        "codigo": "MAS-001",
        "nome": "Máscara PFF2",
        "categoria": "Máscaras",
        "tamanho": "U",
        "estoque": 150,
        "estoque_minimo": 30,
    },
    {
        "codigo": "AVL-001",
        "nome": "Avental PVC",
        "categoria": "Avental",
        "tamanho": "U",
        "estoque": 35,
        "estoque_minimo": 5,
    },
    {
        "codigo": "MGT-001",
        "nome": "Mangote de Raspa",
        "categoria": "Mangotes",
        "tamanho": "U",
        "estoque": 60,
        "estoque_minimo": 10,
    },
    {
        "codigo": "CRT-001",
        "nome": "Cremedel Protetor",
        "categoria": "Creme protetor",
        "tamanho": "U",
        "estoque": 300,
        "estoque_minimo": 50,
    },
]


class Command(BaseCommand):
    help = "Popula EPIs de exemplo (idempotente)."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for d in SEED:
            cat_name = d.pop("categoria")
            categoria, _ = CategoriaEPI.objects.get_or_create(nome=cat_name)
            epi, was_created = EPI.objects.get_or_create(
                codigo=d["codigo"],
                defaults={
                    "nome": d["nome"],
                    "categoria": categoria,
                    "tamanho": d.get("tamanho", ""),
                    "estoque": d.get("estoque", 0),
                    "estoque_minimo": d.get("estoque_minimo", 0),
                    "ativo": d.get("ativo", True),
                },
            )
            if was_created:
                created += 1
            else:
                # Atualiza alguns campos se necessário (não sobrescreve tudo)
                changed = False
                if epi.nome != d["nome"]:
                    epi.nome = d["nome"]
                    changed = True
                if epi.categoria_id != categoria.id:
                    epi.categoria = categoria
                    changed = True
                if d.get("tamanho") and epi.tamanho != d["tamanho"]:
                    epi.tamanho = d["tamanho"]
                    changed = True
                if "estoque" in d and epi.estoque != d["estoque"]:
                    epi.estoque = d["estoque"]
                    changed = True
                if "estoque_minimo" in d and epi.estoque_minimo != d["estoque_minimo"]:
                    epi.estoque_minimo = d["estoque_minimo"]
                    changed = True
                if changed:
                    epi.save(
                        update_fields=["nome", "categoria", "tamanho", "estoque", "estoque_minimo"]
                    )
                    updated += 1

        total = EPI.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f"EPIs: criados={created} atualizados={updated} total={total}")
        )
