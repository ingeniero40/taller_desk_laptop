from sqlmodel import Field
from typing import Optional
import uuid
from .base import BaseEntity


class InvoiceItem(BaseEntity, table=True):
    __tablename__: str = "invoice_items"

    invoice_id: uuid.UUID = Field(foreign_key="invoices.id", nullable=False)
    product_id: Optional[uuid.UUID] = Field(default=None, foreign_key="products.id")
    
    # Snapshot of data at time of sale
    description: str = Field(nullable=False)
    quantity: int = Field(default=1)
    unit_price: float = Field(default=0.0)
    subtotal: float = Field(default=0.0)
    tax: float = Field(default=0.0)
    total: float = Field(default=0.0)
