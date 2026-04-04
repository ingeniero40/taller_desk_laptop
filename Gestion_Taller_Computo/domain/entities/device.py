from sqlmodel import Field, Relationship
from typing import Optional, List
import uuid
from .base import BaseEntity


class Device(BaseEntity, table=True):
    __tablename__: str = "devices"

    brand: str = Field(index=True, nullable=False)
    model: str = Field(index=True, nullable=False)
    serial_number: str = Field(unique=True, index=True, nullable=False)

    # Relación con el Cliente (User con rol CUSTOMER)
    customer_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)

    # Campos de Admisión
    physical_condition: Optional[str] = Field(
        default=None
    )  # Descripción del estado físico
    accessories: Optional[str] = Field(default=None)  # Lista de accesorios entregados
    photo_url: Optional[str] = Field(default=None)  # URL o path de foto de admisión
    device_type: Optional[str] = Field(default="Laptop/PC")  # Tipo de equipo
