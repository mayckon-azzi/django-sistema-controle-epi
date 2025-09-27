# app_core/management/commands/seed_all.py
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Roda todos os seeds: colaboradores, epis, entregas, relatorios (na ordem recomendada)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-relatorios", action="store_true", help="Não executar seed_relatorios"
        )
        parser.add_argument("--no-entregas", action="store_true", help="Não executar seed_entregas")

    def handle(self, *args, **options):
        self.stdout.write("Iniciando seed completo...")

        self.stdout.write(self.style.NOTICE("1) seed_colaboradores"))
        call_command("seed_colaboradores")

        self.stdout.write(self.style.NOTICE("2) seed_epis"))
        call_command("seed_epis")

        if not options["no_entregas"]:
            self.stdout.write(self.style.NOTICE("3) seed_entregas"))
            call_command("seed_entregas")
        else:
            self.stdout.write(self.style.WARNING("Pulado seed_entregas"))

        if not options["no_relatorios"]:
            self.stdout.write(self.style.NOTICE("4) seed_relatorios"))
            call_command("seed_relatorios")
        else:
            self.stdout.write(self.style.WARNING("Pulado seed_relatorios"))

        self.stdout.write(self.style.SUCCESS("Seed completo finalizado."))
