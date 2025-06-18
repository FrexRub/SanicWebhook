import logging
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.jwt_utils import create_hash_password
from src.utils.create_account_number import bank_account
from src.core.config import configure_logging
from src.core.exceptions import (
    UniqueViolationError,
    NotFindUser,
    EmailInUse,
    ErrorInData,
)
from src.users.models import User
from src.payments.models import Score
from src.users.schemas import (
    UserCreateSchemas,
    UserUpdateSchemas,
    UserUpdatePartialSchemas,
)

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def get_user_from_db(session: AsyncSession, email: str) -> User:
    logger.info("Start find user by username: %s" % email)
    stmt = select(User).where(User.email == email)
    res: Result = await session.execute(stmt)
    user: Optional[User] = res.scalars().one_or_none()
    if not user:
        logger.info("User by name %s not find" % email)
        raise NotFindUser(f"Not find user by username {email}")
    logger.info("User has benn found")
    return user


async def get_user_by_id(session: AsyncSession, id_user: int) -> Optional[User]:
    logger.info("User request by id %d" % id_user)
    return await session.get(User, id_user)


async def find_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    logger.info("User find by email %s" % email)
    stmt = select(User).filter(User.email == email)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_data: UserCreateSchemas) -> User:
    """
    :param session: сессия
    :type session: AsyncSession
    :param user_data: данные нового пользователя
    :type user_data: UserCreateSchemas
    :rtype: User
    :return: возвращает нового пользователя
    """
    logger.info("Start create user with email %s" % user_data.email)
    result: Optional[User] = await find_user_by_email(
        session=session, email=user_data.email
    )
    if result:
        raise EmailInUse("The email address is already in use")

    try:
        new_user: User = User(**user_data.model_dump())
    except ValueError as exc:
        raise ErrorInData(exc)
    else:
        new_user_hashed_password = await create_hash_password(new_user.hashed_password)
        new_user.hashed_password = new_user_hashed_password.decode()
        session.add(new_user)

        new_account_number = await bank_account(session=session)
        new_score: Score = Score(account_number=new_account_number, user=new_user)
        session.add(new_score)

        await session.commit()
        logger.info("User with email %s created" % user_data.email)
        return new_user


async def get_users(session: AsyncSession) -> list[User]:
    logger.info("Get list users")
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def update_user_db(
    session: AsyncSession,
    id_user: int,
    user_update: Union[UserUpdateSchemas, UserUpdatePartialSchemas],
    partial: bool = False,
) -> User:
    logger.info("Start update user")

    user: Optional[User] = await get_user_by_id(session=session, id_user=id_user)
    if user is None:
        raise NotFindUser(f"User with id {id_user} not found!")

    try:
        for name, value in user_update.model_dump(exclude_unset=partial).items():
            setattr(user, name, value)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise UniqueViolationError(
            "Duplicate key value violates unique constraint users_email_key"
        )
    return user


async def delete_user_db(session: AsyncSession, user: User) -> None:
    logger.info("Delete user by id %d" % user.id)
    await session.delete(user)
    await session.commit()
