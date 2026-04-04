from sqlmodel import Field
from typing import Optional
import uuid
import datetime
from .base import BaseEntity
from ..value_objects.billing_types import QuoteStatus


class Quote(BaseEntity, table=True):
    __tablename__: str = "quotes"

    quote_number: str = Field(unique=True, index=True, nullable=False)
    
    # Relationships
    customer_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    work_order_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="work_orders.id"
    )
    
    # Details
    # Potentially we could have lines here, but start simple.
    items_summary: str = Field(nullable=False) # Simplified: "Mainboard + Display repair"
    
    # Totals
    subtotal: float = Field(default=0.0)
    tax: float = Field(default=0.0)
    total: float = Field(default=0.0)
    
    status: QuoteStatus = Field(default=QuoteStatus.DRAFT, nullable=False)
    
    # Approval Flow
    approval_date: Optional[datetime.datetime] = Field(default=None)
    expiry_date: Optional[datetime.datetime] = Field(default=None)
    conversion_invoice_id: Optional[uuid.UUID] = Field(default=None, foreign_key="invoices.id")
    
    notes: Optional[str] = Field(default=None)
