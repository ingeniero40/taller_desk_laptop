from sqlmodel import Field
from typing import Optional
import uuid
import datetime
from .base import BaseEntity
from ..value_objects.billing_types import InvoiceStatus


class Invoice(BaseEntity, table=True):
    __tablename__: str = "invoices"

    invoice_number: str = Field(unique=True, index=True, nullable=False)

    # Relaciones
    customer_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    work_order_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="work_orders.id"
    )

    # Totales
    subtotal: float = Field(default=0.0)
    tax: float = Field(default=0.0)
    total: float = Field(default=0.0)
    amount_paid: float = Field(default=0.0)

    status: InvoiceStatus = Field(default=InvoiceStatus.PENDING, nullable=False)
    due_date: Optional[datetime.datetime] = Field(default=None)
