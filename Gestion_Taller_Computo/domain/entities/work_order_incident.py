from sqlmodel import Field
import datetime
from typing import Optional
import uuid
from .base import BaseEntity


class WorkOrderIncident(BaseEntity, table=True):
    """
    Incidencia técnica registrada durante la reparación.

    Permite documentar:
    - Problemas inesperados encontrados
    - Soluciones aplicadas
    - Estado de resolución
    """

    __tablename__: str = "work_order_incidents"

    work_order_id: uuid.UUID = Field(
        foreign_key="work_orders.id", nullable=False, index=True
    )
    reported_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    problem_found: str = Field(nullable=False)  # Descripción del problema
    solution_applied: Optional[str] = Field(default=None)  # Solución aplicada
    is_resolved: bool = Field(default=False)
    resolved_at: Optional[datetime.datetime] = Field(default=None)
