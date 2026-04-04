from sqlmodel import Field
import datetime
from typing import Optional
import uuid
from .base import BaseEntity


class WorkOrderComment(BaseEntity, table=True):
    """
    Comentario sobre una Orden de Trabajo.

    is_internal=True  → visible solo para el equipo técnico
    is_internal=False → visible también para el cliente (portal)
    """

    __tablename__: str = "work_order_comments"

    work_order_id: uuid.UUID = Field(
        foreign_key="work_orders.id", nullable=False, index=True
    )
    author_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    author_name: Optional[str] = Field(default=None)  # Cache del nombre
    content: str = Field(nullable=False)
    is_internal: bool = Field(default=True)  # True = solo staff
