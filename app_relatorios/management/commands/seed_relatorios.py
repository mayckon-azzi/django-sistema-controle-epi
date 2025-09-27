# app_relatorios/management/commands/seed_relatorios.py
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega
from app_epis.models import EPI


class Command(BaseCommand):
    help = "Popula entregas variadas para alimentar relatórios (idempotente parcial)."

    def handle(self, *args, **options):
        now = timezone.now()
        colaboradores = list(Colaborador.objects.all())
        epis = list(EPI.objects.filter(ativo=True))

        if not colaboradores or not epis:
            self.stdout.write(
                self.style.WARNING(
                    "Precisa de Colaboradores e EPIs. Rode os seeds de colaboradores/epis primeiro."
                )
            )
            return

        created = 0
        statuses = [s[0] for s in Entrega.Status.choices]

        for days_back in range(0, 30, 3):
            for _ in range(2):
                col = random.choice(colaboradores)
                epi = random.choice(epis)
                quantidade = random.randint(1, 4)
                status = random.choice(statuses)
                data_entrega = now - timedelta(days=days_back)
                observ = f"Seed relatorio {data_entrega.date()} - {col.matricula} - {epi.codigo} - {status}"

                if Entrega.objects.filter(
                    data_entrega__date=data_entrega.date(),
                    colaborador=col,
                    epi=epi,
                    observacao=observ,
                ).exists():
                    continue

                data_prev = (
                    data_entrega + timedelta(days=7)
                    if status in (Entrega.Status.EMPRESTADO, Entrega.Status.EM_USO)
                    else None
                )
                data_dev = (
                    (data_entrega + timedelta(days=random.randint(1, 6)))
                    if status
                    in (Entrega.Status.DEVOLVIDO, Entrega.Status.DANIFICADO, Entrega.Status.PERDIDO)
                    else None
                )

                Entrega.objects.create(
                    colaborador=col,
                    epi=epi,
                    quantidade=quantidade,
                    status=status,
                    data_entrega=data_entrega,
                    data_prevista_devolucao=data_prev,
                    data_devolucao=data_dev,
                    observacao=observ,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Entregas criadas para relatórios: {created}"))
