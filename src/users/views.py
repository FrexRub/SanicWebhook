import json as js

from sanic import Blueprint, Request
from sanic.response import json, HTTPResponse
from sanic_ext import openapi
from sqlalchemy.ext.asyncio import AsyncSession


from src.users.schemas import LoginSchemas
from src.users.models import User
from src.users.crud import (
    get_user_from_db,
    create_user,
    update_user_db,
    delete_user_db,
    get_users,
)
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
    UserSuperSchemas,
    UserProtectedSchemas,
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
        500: {"description": "Server error"},
    },
    tag="User",
)
async def login(request: Request, db_session: AsyncSession) -> HTTPResponse:
    """
    Обрабатывает вход пользователя в систему.
    """
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
            "content": {
                "application/json": {
                    "example": {
                        "id": 10,
                        "full_name": "user full name",
                        "email": "example@example.com",
                    }
                }
            },
        },
        400: {"description": "Неверные данные"},
        401: {"description": "User not authorized"},
        403: {"description": "Access denied"},
        500: {"description": "Server error"},
    },
    tag="User",
)
async def user_create(
    request: Request,
    db_session: AsyncSession,
    user: UserSuperSchemas,
) -> HTTPResponse:
    """
    Создание нового пользователя системы.
    """
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


@router.get("/logout")
@openapi.definition(
    response={
        200: {
            "description": "Успешный выход",
            "content": {"application/json": {"example": {"result": "Ok"}}},
        },
        500: {"description": "Server error"},
    },
    tag="User",
)
def logout(request: Request) -> HTTPResponse:
    """
    Обрабатывает выход пользователя из системы.
    """
    response = json({"result": "Ok"}, status=200)
    response.delete_cookie(COOKIE_NAME)

    return response


@router.put("/<id_user:int>/")
@openapi.definition(
    body={"application/json": UserUpdateSchemas.schema()},
    response={
        200: {
            "description": "Успешное изменение данных пользователя",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "full_name": "Name",
                        "email": "example@example.com",
                    }
                }
            },
        },
        400: {"description": "Неверные данные"},
        401: {"description": "User not authorized"},
        403: {"description": "Access denied"},
        500: {"description": "Server error"},
    },
    tag="User",
)
async def update_user(
    request: Request,
    id_user: int,
    db_session: AsyncSession,
    user: UserSuperSchemas,
) -> HTTPResponse:
    """
    Полное изменение данных пользователя.
    """
    try:
        data_user_update = UserUpdateSchemas(**request.json)
        user_update = await update_user_db(
            session=db_session, id_user=id_user, user_update=data_user_update
        )
    except UniqueViolationError:
        return json(
            status=400,
            body=f"Duplicate email",
        )
    except NotFindUser:
        return json(
            status=400,
            body=f"User with id {id_user} not found!",
        )
    else:
        return json(
            {
                "id": user_update.id,
                "full_name": user_update.full_name,
                "email": user_update.email,
            },
            status=200,
        )


@router.patch("/<id_user:int>/")
@openapi.definition(
    body={"application/json": UserUpdatePartialSchemas.schema()},
    response={
        200: {
            "description": "Успешное изменение данных пользователя",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "full_name": "Name",
                        "email": "example@example.com",
                    }
                }
            },
        },
        400: {"description": "Неверные данные"},
        401: {"description": "User not authorized"},
        403: {"description": "Access denied"},
        500: {"description": "Server error"},
    },
    tag="User",
)
async def update_user_partial(
    request: Request,
    id_user: int,
    db_session: AsyncSession,
    user: UserSuperSchemas,
) -> HTTPResponse:
    """
    Частичное изменение данных пользователя.
    """
    try:
        data_user_update = UserUpdatePartialSchemas(**request.json)
        user_update = await update_user_db(
            session=db_session,
            id_user=id_user,
            user_update=data_user_update,
            partial=True,
        )
    except UniqueViolationError:
        return json(
            status=400,
            body=f"Duplicate email",
        )
    except NotFindUser:
        return json(
            status=400,
            body=f"User with id {id_user} not found!",
        )
    else:
        return json(
            {
                "id": user_update.id,
                "full_name": user_update.full_name,
                "email": user_update.email,
            },
            status=200,
        )


@router.delete("/<id_user:int>/")
@openapi.definition(
    response={
        204: {
            "description": "Успешное удаление пользователя",
            "content": {"application/json": {"example": {"result": "Ok"}}},
        },
        400: {"description": "Пользователь не найден"},
        401: {"description": "User not authorized"},
        403: {"description": "Access denied"},
        500: {"description": "Server error"},
    },
    tag="User",
)
async def delete_user(
    request: Request,
    id_user: int,
    db_session: AsyncSession,
    user: UserSuperSchemas,
) -> HTTPResponse:
    """
    Удаление пользователя.
    """
    try:
        await delete_user_db(
            session=db_session,
            id_user=id_user,
        )
    except NotFindUser:
        return json(
            status=400,
            body=f"User with id {id_user} not found!",
        )
    else:
        return json({"result": "Ok"}, status=204)


@router.get("/list")
@openapi.definition(
    response={
        200: {
            "description": "Успешный вывод списка пользователей",
            "content": {
                "application/json": {
                    "example": {
                        "users": [
                            {
                                "full_name": "Uly Ivanova",
                                "email": "ivanova@mail.com",
                                "id": 5,
                                "score": [
                                    {
                                        "account_number": "40817765056221374791",
                                        "balance": 0,
                                        "date_creation": "18-Jun-2025",
                                    }
                                ],
                            }
                        ]
                    }
                }
            },
        },
        401: {"description": "User not authorized"},
        403: {"description": "Access denied"},
        500: {"description": "Server error"},
    },
    tag="User",
)
async def get_list_users(
    request: Request,
    db_session: AsyncSession,
    user: UserSuperSchemas
) -> HTTPResponse:
    """
    Получение списка пользователей с их счетами.
    """
    list_users = await get_users(session=db_session)
    return json({"users": list_users})
