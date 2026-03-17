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
    
    # Si quisiéramos navegación bidireccional (requiere importar User en runtime o usar strings)
    # customer: "User" = Relationship(back_populates="devices")
