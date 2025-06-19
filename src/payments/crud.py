import logging
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import configure_logging
from src.users.models import User
from src.users.crud import get_user_by_id
from src.payments.models import Score, Payment
from src.payments.schemas import ScoreBaseSchemas, PaymentOutSchemas

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def list_scopes(session: AsyncSession, id_user: int) -> list[dict[str, str]]:
    user: User = await get_user_by_id(session=session, id_user=id_user)

    stmt = select(Score).filter(Score.user_id == user.id)
    result: Result = await session.execute(stmt)
    scores = result.scalars().all()
    list_scopes_user: list[dict[str, str]] = [
        ScoreBaseSchemas(**i_scores.__dict__).model_dump() for i_scores in scores
    ]

    return list_scopes_user


async def list_payments(session: AsyncSession, user_id: int) -> list[dict[str, str]]:
    logger.info("Get list payments for user with id: %s" % user_id)

    stmt = select(Payment).filter(Payment.user_id == user_id)
    result: Result = await session.execute(stmt)
    payments = result.scalars().all()

    list_payment_user: list[dict[str, str]] = [
        PaymentOutSchemas(**payment.__dict__).model_dump() for payment in payments
    ]

    return list_payment_user
