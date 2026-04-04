from sqlmodel import Field
from typing import Optional
import uuid
from .base import BaseEntity


class Product(BaseEntity, table=True):
    __tablename__: str = "products"

    sku: str = Field(unique=True, index=True, nullable=False)
    barcode: Optional[str] = Field(default=None, unique=True, index=True)
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)

    # Precios y Stock
    cost_price: float = Field(default=0.0)
    sale_price: float = Field(default=0.0)
    stock: int = Field(default=0)
    min_stock: int = Field(default=5)

    category: Optional[str] = Field(default="Repuestos", index=True)
    supplier_id: Optional[uuid.UUID] = Field(default=None, foreign_key="suppliers.id")
