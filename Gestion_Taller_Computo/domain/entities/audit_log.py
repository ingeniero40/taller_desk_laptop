from sqlmodel import Field
import datetime
import uuid
from typing import Optional
from .base import BaseEntity

class AuditLog(BaseEntity, table=True):
    """
    Registro histórico de acciones críticas dentro del sistema.
    Base de auditoría técnica y administrativa.
    """
    __tablename__: str = "audit_logs"

    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id", index=True)
    user_name: str = Field(default="SISTEMA")
    
    action: str = Field(nullable=False) # e.g. "WORK_ORDER_UPDATE", "PAYMENT_CREATED"
    module: str = Field(nullable=False) # e.g. "ORDERS", "BILLING", "INVENTORY"
    
    entity_id: str = Field(index=True)   # ID del objeto afectado (string para flexibilidad)
    entity_type: str = Field(index=True) # "WorkOrder", "Invoice", etc.
    
    previous_value: Optional[str] = Field(default=None) # JSON o texto previo
    new_value: Optional[str] = Field(default=None)      # JSON o texto nuevo
    
    details: str = Field(default="")
    ip_address: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
