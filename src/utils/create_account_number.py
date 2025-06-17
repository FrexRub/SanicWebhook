import random
import asyncio


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
