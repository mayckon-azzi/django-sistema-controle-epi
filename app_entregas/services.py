from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from app_epis.models import EPI
from .models import Entrega

def _mov_value(status: str, qtd: int) -> int:
    """
    Mapeia o status da Entrega para movimento de estoque:
      ENTREGUE  => -qtd  (saída)
      DEVOLVIDO => +qtd  (entrada)
      CANCELADO =>  0
    """
    if status == Entrega.Status.ENTREGUE:
        return -int(qtd or 0)
    if status == Entrega.Status.DEVOLVIDO:
        return +int(qtd or 0)
    return 0  # CANCELADO

@transaction.atomic
def _apply_delta(epi_id: int, delta: int) -> int:
    """
    Aplica delta no estoque do EPI, de forma atômica.
    delta > 0  => entrada
    delta < 0  => saída (valida para não ficar negativo)
    Retorna o estoque atualizado.
    """
    epi = EPI.objects.select_for_update(of=("self",)).get(pk=epi_id)  # em SQLite o lock é limitado, mas é seguro usar
    # valida saída
    if delta < 0 and epi.estoque < abs(delta):
        raise ValidationError("Estoque insuficiente para a operação.")
    # aplica F() para evitar race conditions
    EPI.objects.filter(pk=epi_id).update(estoque=F("estoque") + delta)
    epi.refresh_from_db(fields=["estoque"])
    if epi.estoque < 0:
        # reforço (deveria ser impossível com a validação + constraint)
        raise ValidationError("Operação resultaria em estoque negativo.")
    return epi.estoque

@transaction.atomic
def movimenta_por_entrega(nova: Entrega, antiga: Entrega | None = None) -> None:
    """
    Reconciliador de estoque com base em uma Entrega nova/atualizada.
    - Se antiga is None => criação
    - Se trocou EPI/status/quantidade => aplica deltas corretos
    """
    if antiga is None:
        delta = _mov_value(nova.status, nova.quantidade)
        if delta:
            _apply_delta(nova.epi_id, delta)
        return

    # Atualização: pode ter mudado epi, status ou quantidade
    old_delta = _mov_value(antiga.status, antiga.quantidade)
    new_delta = _mov_value(nova.status, nova.quantidade)

    if antiga.epi_id == nova.epi_id:
        # Ajuste apenas no mesmo EPI
        delta = new_delta - old_delta
        if delta:
            _apply_delta(nova.epi_id, delta)
    else:
        # Reverte efeito antigo no EPI antigo e aplica efeito novo no EPI novo
        if old_delta:
            _apply_delta(antiga.epi_id, -old_delta)
        if new_delta:
            _apply_delta(nova.epi_id, new_delta)

@transaction.atomic
def movimenta_por_exclusao(entrega: Entrega) -> None:
    """
    Ao excluir uma Entrega, desfaz o movimento que ela aplicou.
    ENTREGUE  ( -q ) -> desfazendo => +q
    DEVOLVIDO ( +q ) -> desfazendo => -q  (valida estoque!)
    CANCELADO (  0 ) -> nada
    """
    delta = _mov_value(entrega.status, entrega.quantidade)
    if delta:
        _apply_delta(entrega.epi_id, -delta)
