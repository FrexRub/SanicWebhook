from typing import Optional

import jwt
from sanic import Request
from sanic.exceptions import SanicException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import COOKIE_NAME
from src.users.crud import get_user_by_id
from src.users.models import User
from src.users.schemas import UserProtectedSchemas, UserSuperSchemas
from src.utils.jwt_utils import decode_jwt


async def validate_token(token: str, session: AsyncSession) -> Optional[User]:
    """
    Валидация токена и возвращение данных об авторизованном клиенте
    """
    if token is None:
        return None
    try:
        payload = await decode_jwt(token)
    except jwt.ExpiredSignatureError:
        return None

    id_user: int = int(payload["sub"])
    user: User = await get_user_by_id(session=session, id_user=id_user)

    return user


async def current_superuser_user(
    request: Request,
    db_session: AsyncSession,
) -> UserSuperSchemas:
    """
    Проверка авторизации пользователя и его принадлежность к администраторам
    """

    token = request.cookies.get(COOKIE_NAME)
    user: Optional[User] = await validate_token(token=token, session=db_session)

    if user is None:
        raise SanicException("User not authorized", status_code=401)

    if not user.is_superuser:
        raise SanicException("Access denied", status_code=403)

    return UserSuperSchemas(**user.__dict__)


async def current_user(
    request: Request,
    db_session: AsyncSession,
) -> UserProtectedSchemas:
    """
    Проверка авторизации пользователя
    """
    token = request.cookies.get(COOKIE_NAME)
    user: Optional[User] = await validate_token(token=token, session=db_session)

    if user is None:
        raise SanicException("User not authorized", status_code=401)

    return UserProtectedSchemas(**user.__dict__)