import asyncio
import random

from sqlalchemy import exists, select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.payments.models import Score


async def generate_bank_account(prefix: str = "40817", length: int = 20) -> str:
    """
    Генерирует номер банковского счета.

    :param prefix: Префикс счета (по умолчанию "40817" для рублевых счетов).
    :param length: Общая длина номера счета (по умолчанию 20 символов).
    :return: Строка с номером счета.
    """
    unique_part_length = length - len(prefix)
    unique_part = "".join(
        [str(random.randint(0, 9)) for _ in range(unique_part_length)]
    )
    await asyncio.sleep(0.1)
    account_number = prefix + unique_part

    return account_number


async def bank_account(
    session: AsyncSession, prefix: str = "40817", length: int = 20
) -> str:
    """
    Генерирует уникального номер банковского счета.
    """
    account_number = await generate_bank_account(prefix=prefix, length=length)

    stmt = select(exists().where(Score.account_number == account_number))
    res: Result = await session.execute(stmt)
    is_exists: bool = res.scalar()

    while is_exists:
        account_number = await generate_bank_account(prefix=prefix, length=length)
        stmt = select(exists().where(Score.account_number == account_number))
        res: Result = await session.execute(stmt)
        is_exists: bool = res.scalar()

    return account_number
