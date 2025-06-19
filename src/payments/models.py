from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    NUMERIC,
    UUID,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("account_id", "user_id", name="idx_unique_account_user"),
        Index(
            "idx_account_number_hash",
            "account_number",
            postgresql_using="hash",
        ),
    )

    account_id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[NUMERIC] = mapped_column(
        NUMERIC(15, 2), default=0.00, server_default=text("0.00")
    )
    account_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    date_creation: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="scores")


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint(
            "transaction_id", "user_id", name="idx_unique_transaction_user"
        ),
    )

    transaction_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    amount: Mapped[NUMERIC] = mapped_column(NUMERIC(15, 2))
    date_creation: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    account_id: Mapped[int] = mapped_column(
        ForeignKey("scores.account_id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship(back_populates="payments")
