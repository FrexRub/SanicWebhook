from sanic import Blueprint
from sanic.response import json, text
from sanic.exceptions import SanicException
from sanic_ext import openapi
from sqlalchemy.ext.asyncio import AsyncSession


from src.users.schemas import LoginSchemas
from src.users.models import User
from src.users.crud import get_user_from_db, create_user
from src.utils.jwt_utils import validate_password, create_jwt
from src.core.config import COOKIE_NAME
from src.core.exceptions import (
    UniqueViolationError,
    NotFindUser,
    EmailInUse,
    ErrorInData,
)
from src.users.schemas import (
    UserCreateSchemas,
    UserUpdateSchemas,
    UserUpdatePartialSchemas,
    UserCreateSchemasIn,
)


router = Blueprint("user", url_prefix="/user")


@router.post("/login")
@openapi.definition(
    body={"application/json": LoginSchemas.schema()},
    response={
        200: {
            "description": "Успешный вход",
            "content": {
                "application/json": {
                    "example": {"access_token": "abc123", "token_type": "bearer"}
                }
            },
        },
        401: {"description": "Неверные данные"},
    },
    tag="User",
)
async def login(request, db_session: AsyncSession):
    data_login = LoginSchemas(**request.json)
    try:
        user: User = await get_user_from_db(session=db_session, email=data_login.email)
    except NotFindUser:
        return json(
            status=400,
            body=f"The user with the username: {data_login.email} not found",
        )

    if await validate_password(
        password=data_login.password, hashed_password=user.hashed_password
    ):
        access_token: str = await create_jwt(str(user.id))
        response = json(
            {"access_token": access_token, "token_type": "bearer"}, status=200
        )

        response.cookies.add_cookie(
            key=COOKIE_NAME,
            value=access_token,
            samesite="lax",
            path="/",
        )
        return response
    else:
        return json(
            status=400,
            body=f"Error password for login: {data_login.email}",
        )


@router.post("/create")
@openapi.definition(
    body={"application/json": UserCreateSchemasIn.schema()},
    response={
        201: {
            "description": "Успешное создание пользователя",
            "content": {"application/json": {"example": {"status": "Ok"}}},
        },
        401: {"description": "Неверные данные"},
    },
    tag="User",
)
async def user_create(
    request,
    db_session: AsyncSession,
    # user: User = Depends(current_superuser_user),
):
    try:
        new_user = UserCreateSchemas(
            full_name=request.json["username"],
            email=request.json["email"],
            hashed_password=request.json["password"],
        )
        user: User = await create_user(session=db_session, user_data=new_user)
    except EmailInUse:
        return json(
            status=400,
            body="The email address is already in use",
        )

    except (ErrorInData, ValueError) as exp:
        return json(
            status=400,
            body=f"{exp}",
        )

    return json(
        {"id": user.id, "full_name": user.full_name, "email": user.email},
        status=201,
    )
