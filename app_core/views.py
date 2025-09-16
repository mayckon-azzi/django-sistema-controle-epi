# app_core/views.py
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.utils import timezone

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega, Solicitacao
from app_epis.models import EPI


def home(request):
    # Descobre dinamicamente os códigos de status de Entrega
    status_codes = {code for code, _ in Entrega.Status.choices}

    # "Fora do estoque" = qualquer status que NÃO seja DEVOLVIDO nem CANCELADO
    fora_do_estoque = [s for s in status_codes if s not in {"DEVOLVIDO", "CANCELADO"}]

    agora = timezone.now()

    devolvidos_mes = 0
    if "DEVOLVIDO" in status_codes:
        devolvidos_mes = (
            Entrega.objects.filter(
                status="DEVOLVIDO",
                data_entrega__year=agora.year,
                data_entrega__month=agora.month,
            )
            .only("id")  # micro-otimização
            .count()
        )

    ctx = {
        "total_colaboradores": Colaborador.objects.only("id").count(),
        "total_epis": EPI.objects.only("id").count(),
        "estoque_total": (EPI.objects.aggregate(total=Coalesce(Sum("estoque"), 0)).get("total", 0)),
        "entregas_ativas": Entrega.objects.filter(status__in=fora_do_estoque).only("id").count(),
        "devolvidos_mes": devolvidos_mes,
        "solicitacoes_pendentes": Solicitacao.objects.filter(status=Solicitacao.Status.PENDENTE)
        .only("id")
        .count(),
    }

    if request.user.is_authenticated and hasattr(request.user, "colaborador"):
        ctx["minhas_solicitacoes_abertas"] = (
            Solicitacao.objects.filter(
                colaborador=request.user.colaborador,
                status__in=[Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA],
            )
            .only("id")
            .count()
        )

    return render(request, "app_core/pages/home.html", ctx)


def testar_mensagens(request):
    messages.success(request, "Sucesso! Exemplo de mensagem.")
    messages.info(request, "Info: isso é apenas um teste.")
    messages.warning(request, "Atenção: algo a verificar.")
    messages.error(request, "Erro: exemplo simulado.")
    return redirect("app_core:home")
