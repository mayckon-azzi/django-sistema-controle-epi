from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from app_colaboradores.models import Colaborador
from app_epis.models import EPI
from app_entregas.models import Entrega, Solicitacao


def home(request):
    # Descobre dinamicamente os códigos de status existentes na model de Entrega
    status_codes = [code for code, _ in Entrega.Status.choices]

    # "Fora do estoque" = qualquer status que NÃO seja DEVOLVIDO nem CANCELADO
    fora_do_estoque = [s for s in status_codes if s not in {"DEVOLVIDO", "CANCELADO"}]

    agora = timezone.now()

    # Conta devoluções do mês apenas se o status existir na enum
    devolvidos_mes = 0
    if "DEVOLVIDO" in status_codes:
        devolvidos_mes = Entrega.objects.filter(
            status="DEVOLVIDO",
            data_entrega__year=agora.year,
            data_entrega__month=agora.month,
        ).count()

    ctx = {
        "total_colaboradores": Colaborador.objects.count(),
        "total_epis": EPI.objects.count(),
        "estoque_total": EPI.objects.aggregate(total=Sum("estoque")).get("total") or 0,
        # Ativos/fora do estoque (robusto a mudanças de enum)
        "entregas_ativas": Entrega.objects.filter(status__in=fora_do_estoque).count(),
        "devolvidos_mes": devolvidos_mes,
        "solicitacoes_pendentes": Solicitacao.objects.filter(
            status=Solicitacao.Status.PENDENTE
        ).count(),
    }

    if request.user.is_authenticated and hasattr(request.user, "colaborador"):
        ctx["minhas_solicitacoes_abertas"] = Solicitacao.objects.filter(
            colaborador=request.user.colaborador,
            status__in=[Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA],
        ).count()

    return render(request, "app_core/pages/home.html", ctx)


def testar_mensagens(request):
    messages.success(request, "Sucesso! Exemplo de mensagem.")
    messages.info(request, "Info: isso é apenas um teste.")
    messages.warning(request, "Atenção: algo a verificar.")
    messages.error(request, "Erro: exemplo simulado.")
    return redirect("app_core:home")
