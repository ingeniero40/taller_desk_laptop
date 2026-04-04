from sqlmodel import Field
from typing import Optional
import uuid
import datetime
from .base import BaseEntity

class InventoryMovement(BaseEntity, table=True):
    __tablename__: str = "inventory_movements"

    product_id: uuid.UUID = Field(foreign_key="products.id", nullable=False)
    movement_type: str = Field(nullable=False) # "IN", "OUT", "ADJUST"
    quantity: int = Field(nullable=False)
    reference_id: Optional[str] = Field(default=None) # e.g. WorkOrder ID
    notes: Optional[str] = Field(default=None)
    created_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
