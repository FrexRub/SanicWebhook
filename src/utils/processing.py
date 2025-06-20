import asyncio
import decimal
import hashlib
import logging
import uuid
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import configure_logging, setting_conn
from src.core.exceptions import (
    ErrorInData,
    PaymentProcessed,
)
from src.users.models import User
from src.utils.create_account_number import bank_account
from src.payments.models import Payment, Score
from src.payments.schemas import (
    PaymentGenerateBaseSchemas,
    PaymentGenerateOutSchemas,
    TransactionInSchemas,
)

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def generate_payments(
    data_request: PaymentGenerateBaseSchemas,
) -> PaymentGenerateOutSchemas:
    """
    Генерация платежа по реквизитам (transaction_id генерируется системой)
    """
    if data_request.transaction_id:
        transaction_id = data_request.transaction_id
    else:
        transaction_id = str(uuid.uuid4())
    payload = (
        str(data_request.account_id)
        + str(data_request.amount)
        + transaction_id
        + str(data_request.user_id)
        + setting_conn.SECRET_KEY
    )
    signature = hashlib.sha256(payload.encode()).hexdigest()
    await asyncio.sleep(0)

    result = PaymentGenerateOutSchemas(
        transaction_id=transaction_id,
        user_id=data_request.user_id,
        account_id=data_request.account_id,
        amount=data_request.amount,
        signature=signature,
    )

    return result


async def process_transaction(
    session: AsyncSession, data_request: TransactionInSchemas
) -> None:
    """
    Обработка поступившего платежа
    """
    data: PaymentGenerateBaseSchemas = PaymentGenerateBaseSchemas(
        **data_request.model_dump()
    )
    data_generate: PaymentGenerateOutSchemas = await generate_payments(
        data_request=data
    )

    if data_request.signature != data_generate.signature:
        raise ErrorInData("Error signature")

    account_id = data.account_id
    user_id = data.user_id
    transaction_id = data.transaction_id
    amount = decimal.Decimal(data.amount)

    logger.info("Start transaction with id %s" % transaction_id)

    stmt = select(Payment).filter(Payment.transaction_id == transaction_id)
    result: Result = await session.execute(stmt)
    payment: Payment = result.scalars().first()
    if payment:
        logger.info("The payment #%s is processed" % transaction_id)
        raise PaymentProcessed(f"The payment #{transaction_id} is processed")

    user: Optional[User] = await session.get(User, user_id)
    if user is None:
        raise PaymentProcessed(f"User by id: #{user_id} not found")

    stmt = select(Score).filter(
        and_(
            Score.account_id == account_id,
            Score.user_id == user_id,
        )
    )
    result: Result = await session.execute(stmt)
    scores: Score = result.scalars().first()

    if scores is None:
        logger.info(
            "The score #%s was not found for the user with id:%s"
            % (account_id, user_id)
        )
        new_account_number = await bank_account(session=session)
        scores: Score = Score(
            account_number=new_account_number,
            user=user,
            account_id=account_id,
            balance=decimal.Decimal(0.0),
        )
        session.add(scores)
        await session.commit()
        await session.flush()

        logger.info(
            "The score #%s for the user with id:%s created" % (account_id, user_id)
        )

    if float(amount) < 0 and (scores.balance < abs(amount)):
        raise PaymentProcessed("insufficient funds")

    async with session.begin_nested():
        logger.info(f"float(amount) {float(amount)}  {float(amount) < 0}")
        scores.balance += decimal.Decimal(amount)
        payment: Payment = Payment(
            transaction_id=transaction_id,
            amount=amount,
            user_id=user_id,
            account_id=scores.account_id,
        )
        session.add(payment)
    await session.commit()
    logger.info("The score #%s for the user with id:%s change" % (account_id, user_id))
