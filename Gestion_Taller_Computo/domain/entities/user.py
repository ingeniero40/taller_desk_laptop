from sqlmodel import Field
from typing import Optional
from .base import BaseEntity
from ..value_objects.user_role import UserRole


class User(BaseEntity, table=True):
    __tablename__: str = "users"

    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    full_name: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.CUSTOMER, nullable=False)
    phone: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True, nullable=False)
