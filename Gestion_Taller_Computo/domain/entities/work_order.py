from sqlmodel import Field
import datetime
from typing import Optional
import uuid
from .base import BaseEntity
from ..value_objects.work_order_status import WorkOrderStatus
from ..value_objects.order_priority import OrderPriority

class WorkOrder(BaseEntity, table=True):
    __tablename__: str = "work_orders"
    
    ticket_number: str = Field(unique=True, index=True, nullable=False)
    status: WorkOrderStatus = Field(default=WorkOrderStatus.RECEIVED, nullable=False)
    
    # Llaves foráneas
    device_id: uuid.UUID = Field(foreign_key="devices.id", nullable=False)
    technician_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    
    # Información técnica
    diagnostic_notes: Optional[str] = Field(default=None)   # Descripción del problema reportado
    repair_notes: Optional[str] = Field(default=None)        # Notas técnicas de reparación
    
    # Prioridad y Tiempos
    priority: OrderPriority = Field(default=OrderPriority.MEDIUM, nullable=False)
    due_date: Optional[datetime.datetime] = Field(default=None)         # Fecha estimada de entrega
    actual_delivery: Optional[datetime.datetime] = Field(default=None)  # Fecha real de entrega
    estimated_hours: Optional[float] = Field(default=None)              # Horas estimadas de trabajo
    actual_hours: Optional[float] = Field(default=None)                 # Horas reales empleadas
    
    # Costos base (Monto parcial o total)
    quoted_price: float = Field(default=0.0)
