import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[uuid] = mapped_column(
        UUID, nullable=False, primary_key=True, unique=True, default=uuid.uuid4
    )
