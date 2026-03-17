from sqlmodel import Field
from typing import Optional
from .base import BaseEntity

class Supplier(BaseEntity, table=True):
    __tablename__: str = "suppliers"
    
    name: str = Field(index=True, nullable=False)
    contact_name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
