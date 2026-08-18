from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import LargeBinary, String

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
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, default=None, nullable=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    status: Mapped[bool] = mapped_column(default=False)
    passkeys: Mapped[list["Passkey"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

