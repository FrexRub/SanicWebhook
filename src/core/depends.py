from typing import Annotated, Optional

import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sanic import Request
from sanic.exceptions import SanicException


from src.utils.jwt_utils import decode_jwt
from src.users.crud import get_user_by_id
from src.users.models import User
from src.users.schemas import UserSuperSchemas, UserProtectedSchemas
from src.core.config import COOKIE_NAME


async def validate_token(token: str, session: AsyncSession) -> Optional[User]:
    if token is None:
        return None
    try:
        payload = await decode_jwt(token)
    except jwt.ExpiredSignatureError:
        return None

    id_user: int = int(payload["sub"])
    user: User = await get_user_by_id(session=session, id_user=id_user)

    return user

#
# async def compile_profile(request: Request):
#     await request.receive_body()
#     profile = await fake_request_to_db(request.json)
#     return profile
#
# async def current_user_authorization(
#     token: Annotated[str, Depends(oauth2_scheme)],
#     session: AsyncSession = Depends(get_async_session),
# ) -> User:
#     if token is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
#         )
#
#     try:
#         payload = await decode_jwt(token)
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
#         )
#
#     id_user: int = int(payload["sub"])
#     user: User = await get_user_by_id(session=session, id_user=id_user)
#
#     return user


async def current_superuser_user(
    request: Request,
    db_session: AsyncSession,
) -> UserSuperSchemas:

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

    token = request.cookies.get(COOKIE_NAME)
    user: Optional[User] = await validate_token(token=token, session=db_session)

    if user is None:
        raise SanicException("User not authorized", status_code=401)

    return UserProtectedSchemas(**user.__dict__)