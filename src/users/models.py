from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

# if TYPE_CHECKING:
#     from src.payments.models import Score, Payment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    registered_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    hashed_password: Mapped[str]
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # scores: Mapped[list["Score"]] = relationship(
    #     back_populates="user",
    #     cascade="save-update, merge, delete",
    #     passive_deletes=True,
    # )
    #
    # payments: Mapped[list["Payment"]] = relationship(
    #     back_populates="user",
    #     cascade="save-update, merge, delete",
    #     passive_deletes=True,
    # )
