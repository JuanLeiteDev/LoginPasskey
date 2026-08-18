from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import LargeBinary

import uuid

from app.database.db import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.passkey import Passkey

class User(Base):
    __tablename__ = "Users"

    id: Mapped[bytes] = mapped_column(
        LargeBinary, 
        primary_key=True,
        default=lambda: uuid.uuid4().bytes
    )
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    status: Mapped[bool] = mapped_column(default=False)
    passkeys: Mapped[list["Passkey"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

