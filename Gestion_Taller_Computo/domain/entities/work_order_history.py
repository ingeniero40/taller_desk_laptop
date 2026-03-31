from sqlmodel import Field
import datetime
from typing import Optional
import uuid
from .base import BaseEntity


class WorkOrderHistory(BaseEntity, table=True):
    """
    Entidad de Auditoría — Historial de cambios de una Orden de Trabajo.

    Cada vez que el estado, técnico o notas de una OT cambian,
    se registra una entrada inmutable en esta tabla.
    """
    __tablename__: str = "work_order_history"

    # Referencia a la orden de trabajo
    work_order_id: uuid.UUID = Field(
        foreign_key="work_orders.id",
        nullable=False,
        index=True
    )

    # Quién realizó el cambio (opcional si es acción del sistema)
    changed_by_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.id"
    )

    # Transición de estado
    from_status: Optional[str] = Field(default=None)   # Estado anterior
    to_status: str = Field(nullable=False)              # Estado nuevo

    # Notas técnicas del cambio
    notes: Optional[str] = Field(default=None)

    # Timestamp explícito del cambio (puede diferir de created_at)
    changed_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )
