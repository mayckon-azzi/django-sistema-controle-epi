from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

APPS_MODELS = {
    "app_colaboradores": ["colaborador"],
    "app_epis": ["epi", "categoriaepi"],
    "app_entregas": ["solicitacao", "entrega"],
}

def perms_of(model, *actions):
    ctype = ContentType.objects.get(app_label=model._meta.app_label, model=model._meta.model_name)
    return Permission.objects.filter(content_type=ctype, codename__in=[f"{a}_{model._meta.model_name}" for a in actions])

class Command(BaseCommand):
    help = "Cria/atualiza grupos padrão (Colaborador, Almoxarife) com permissões do sistema."

    def handle(self, *args, **options):
        from app_colaboradores.models import Colaborador
        from app_epis.models import EPI, CategoriaEPI
        from app_entregas.models import Solicitacao, Entrega

        # grupos
        g_colab, _ = Group.objects.get_or_create(name="Colaborador")
        g_almox, _ = Group.objects.get_or_create(name="Almoxarife")

        # limpa para reaplicar
        g_colab.permissions.clear()
        g_almox.permissions.clear()

        # Colaborador: pode ver EPIs, criar/ver solicitações
        g_colab.permissions.add(
            *perms_of(EPI, "view"),
            *perms_of(CategoriaEPI, "view"),
            *perms_of(Solicitacao, "add", "view"),
            # (opcional) ver entregas próprias: manter sem para já não expor
        )

        # Almoxarife: gerencia quase tudo
        g_almox.permissions.add(
            *perms_of(EPI, "add", "change", "delete", "view"),
            *perms_of(CategoriaEPI, "add", "change", "delete", "view"),
            *perms_of(Solicitacao, "view", "change"),  # aprovar/reprovar/atender
            *perms_of(Entrega, "add", "change", "delete", "view"),
            *perms_of(Colaborador, "add", "change", "delete", "view"),
        )

        self.stdout.write(self.style.SUCCESS("Grupos atualizados com sucesso."))