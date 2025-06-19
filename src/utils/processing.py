import uuid
import hashlib
import asyncio
import logging
import decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.engine import Result

from src.payments.models import Payment, Score
from src.payments.schemas import (
    PaymentGenerateBaseSchemas,
    PaymentGenerateOutSchemas,
    TransactionInSchemas,
)
from src.core.config import setting_conn, configure_logging
from src.core.exceptions import (
    ErrorInData,
    PaymentProcessed,
)

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def generate_payments(
    data_request: PaymentGenerateBaseSchemas,
) -> PaymentGenerateOutSchemas:
    """
    :param data_request: реквизиты платежа для создания транзакции с подписью
    :type data_request: PaymentGenerateBaseSchemas
    :rtype: PaymentGenerateOutSchemas
    :return: возвращает транзакцию с подписью
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
    :param session: сессия БД
    :type session: AsyncSession
    :param data_request: транзакция на исполнение
    :type data_request: TransactionInSchemas
    :rtype: None
    :return:
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
        raise PaymentProcessed(
            f"The score #{account_id} was not found for the user with id: {user_id}"
        )

    else:
        if amount < 0 and (scores.balance < amount):
            raise PaymentProcessed("insufficient funds")

        async with session.begin_nested():
            logger.info(
                "The score #%s for the user with id:%s change" % (account_id, user_id)
            )
            print(f"The score #{account_id} for the user with id: {user_id} change")
            scores.balance += amount
            payment: Payment = Payment(
                transaction_id=transaction_id,
                amount=amount,
                user_id=user_id,
                account_id=scores.account_id,
            )
            session.add(payment)
        await session.commit()
