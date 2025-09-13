from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from app_colaboradores.models import Colaborador
from app_epis.models import EPI
from app_entregas.models import Entrega, Solicitacao

def home(request):
    ctx = {
        "total_colaboradores": Colaborador.objects.count(),
        "total_epis": EPI.objects.count(),
        "estoque_total": EPI.objects.aggregate(total=Sum("estoque")).get("total") or 0,
        "entregas_ativas": Entrega.objects.filter(status=Entrega.Status.ENTREGUE).count(),
        "devolvidos_mes": Entrega.objects.filter(
            status=Entrega.Status.DEVOLVIDO,
            data_entrega__year=timezone.now().year,
            data_entrega__month=timezone.now().month,
        ).count(),
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
