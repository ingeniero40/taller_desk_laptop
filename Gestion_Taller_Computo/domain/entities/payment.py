from sqlmodel import Field
from typing import Optional
import uuid
import datetime
from .base import BaseEntity

class Payment(BaseEntity, table=True):
    __tablename__: str = "payments"
    
    invoice_id: uuid.UUID = Field(foreign_key="invoices.id", nullable=False)
    amount: float = Field(default=0.0)
    payment_method: str = Field(nullable=False) # Cash, Card, Transfer
    transaction_reference: Optional[str] = Field(default=None)
    payment_date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
