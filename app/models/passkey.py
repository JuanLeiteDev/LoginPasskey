from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, LargeBinary

from app.database.db import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class Passkey(Base):
    __tablename__ = "Passkeys"

    credential_id: Mapped[bytes] = mapped_column(
        LargeBinary, 
        primary_key=True
    )

    public_key: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False
    )

    sign_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )

    user_email: Mapped[str] = mapped_column(
        ForeignKey("Users.email", ondelete="CASCADE"),
        nullable=False
    )
    
    user: Mapped["User"] = relationship(
        back_populates="passkeys"
    )