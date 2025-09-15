from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from app_epis.models import EPI
from .models import Entrega


def _mov_value(status: str, qtd: int) -> int:
    """
    Efeito líquido deste registro no estoque:
      - EMPRESTADO / EM_USO / FORNECIDO => -q (sai do estoque)
      - DEVOLVIDO => 0  (ciclo completo: saiu e voltou → efeito líquido zero)
      - DANIFICADO / PERDIDO => -q  (não retorna ao estoque)
    """
    if status in {
        Entrega.Status.EMPRESTADO,
        Entrega.Status.EM_USO,
        Entrega.Status.FORNECIDO,
        Entrega.Status.DANIFICADO,
        Entrega.Status.PERDIDO,
    }:
        return -int(qtd or 0)
    if status == Entrega.Status.DEVOLVIDO:
        return 0
    # fallback defensivo
    return -int(qtd or 0)


@transaction.atomic
def _apply_delta(epi_id: int, delta: int) -> int:
    """
    Aplica delta no estoque do EPI, de forma atômica.
    delta > 0  => entrada
    delta < 0  => saída (valida para não ficar negativo)
    """
    epi = EPI.objects.select_for_update(of=("self",)).get(pk=epi_id)
    if delta < 0 and epi.estoque < abs(delta):
        raise ValidationError("Estoque insuficiente para a operação.")
    EPI.objects.filter(pk=epi_id).update(estoque=F("estoque") + delta)
    epi.refresh_from_db(fields=["estoque"])
    if epi.estoque < 0:
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

    old_delta = _mov_value(antiga.status, antiga.quantidade)
    new_delta = _mov_value(nova.status, nova.quantidade)

    if antiga.epi_id == nova.epi_id:
        delta = new_delta - old_delta
        if delta:
            _apply_delta(nova.epi_id, delta)
    else:
        if old_delta:
            _apply_delta(antiga.epi_id, -old_delta)
        if new_delta:
            _apply_delta(nova.epi_id, new_delta)


@transaction.atomic
def movimenta_por_exclusao(entrega: Entrega) -> None:
    """
    Ao excluir um registro, desfazemos o efeito líquido dele.
    Ex.: registro EMPRESTADO (-q) → excluir => +q
        registro DEVOLVIDO (0)    → excluir => 0
        registro PERDIDO  (-q)    → excluir => +q
    """
    delta = _mov_value(entrega.status, entrega.quantidade)
    if delta:
        _apply_delta(entrega.epi_id, -delta)
