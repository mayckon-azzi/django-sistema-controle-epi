# app_entregas/management/commands/seed_entregas.py
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega, Solicitacao
from app_epis.models import EPI


class Command(BaseCommand):
    help = "Popula solicitações e entregas de exemplo (idempotente na medida do possível)."

    def handle(self, *args, **options):
        now = timezone.now()

        colaboradores = list(Colaborador.objects.all())
        epis = list(EPI.objects.filter(ativo=True))

        if not colaboradores or not epis:
            self.stdout.write(
                self.style.WARNING(
                    "Precisa de Colaboradores e EPIs. Rode os seeds de colaboradores e epis primeiro."
                )
            )
            return

        created_solic = 0
        created_entreg = 0

        for i in range(1, 11):
            col = random.choice(colaboradores)
            epi = random.choice(epis)
            quantidade = random.randint(1, 3)

            observ = f"Seed solicitacao #{i} - {col.matricula} - {epi.codigo}"
            solicitacao, s_created = Solicitacao.objects.get_or_create(
                colaborador=col,
                epi=epi,
                quantidade=quantidade,
                observacao=observ,
                defaults={"status": Solicitacao.Status.PENDENTE},
            )
            if s_created:
                created_solic += 1

            if random.choice([True, False]):
                if Entrega.objects.filter(solicitacao=solicitacao).exists():
                    continue
                # /*entrega=*/#
                Entrega.objects.create(
                    colaborador=col,
                    epi=epi,
                    quantidade=quantidade,
                    status=Entrega.Status.EMPRESTADO,
                    data_entrega=now - timedelta(days=random.randint(1, 10)),
                    data_prevista_devolucao=now + timedelta(days=random.randint(3, 14)),
                    observacao=f"Atendida via seed para solicitacao #{solicitacao.pk}",
                    solicitacao=solicitacao,
                )
                solicitacao.status = Solicitacao.Status.ATENDIDA
                solicitacao.save(update_fields=["status"])
                created_entreg += 1

        for i in range(1, 6):
            col = random.choice(colaboradores)
            epi = random.choice(epis)
            quantidade = random.randint(1, 2)
            status = random.choice(
                [
                    Entrega.Status.EMPRESTADO,
                    Entrega.Status.EM_USO,
                    Entrega.Status.FORNECIDO,
                    Entrega.Status.DEVOLVIDO,
                ]
            )
            observ = f"Seed entrega standalone #{i} - {col.matricula} - {epi.codigo}"
            data_entrega = now - timedelta(days=i)
            if Entrega.objects.filter(
                observacao=observ, data_entrega__date=data_entrega.date()
            ).exists():
                continue
            Entrega.objects.create(
                colaborador=col,
                epi=epi,
                quantidade=quantidade,
                status=status,
                data_entrega=data_entrega,
                data_prevista_devolucao=(
                    (data_entrega + timedelta(days=7))
                    if status in (Entrega.Status.EMPRESTADO, Entrega.Status.EM_USO)
                    else None
                ),
                data_devolucao=(
                    (data_entrega + timedelta(days=3))
                    if status == Entrega.Status.DEVOLVIDO
                    else None
                ),
                observacao=observ,
            )
            created_entreg += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Solicitações criadas: {created_solic}; Entregas criadas: {created_entreg}"
            )
        )
