import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
import uuid


class BaseEntity(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=False,
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "onupdate": datetime.datetime.utcnow,
        },
    )
