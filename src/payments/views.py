from sanic import Blueprint, Request
from sanic.response import json
from sanic_ext import openapi
from sqlalchemy.ext.asyncio import AsyncSession

from src.payments.crud import list_scopes, list_payments
from src.utils.processing import generate_payments
from src.payments.schemas import PaymentGenerateBaseSchemas, PaymentGenerateOutSchemas
from src.users.schemas import UserProtectedSchemas

router = Blueprint("payments", url_prefix="/payments")


@router.get("/score")
@openapi.definition(
    response={
        200: {
            "description": "Успешный вывод информации о счетах",
            "content": {
                "application/json": {
                    "example": {
                        "score": [
                            {
                                "account_number": "40817765056221374791",
                                "balance": 0,
                                "date_creation": "18-Jun-2025",
                            }
                        ],
                    }
                }
            },
        },
        401: {"description": "User not authorized"},
        403: {"description": "Access denied"},
        500: {"description": "Server error"},
    },
    tag="Payments",
)
async def get_list_scores(
    request: Request, db_session: AsyncSession, user: UserProtectedSchemas
):
    """
    Получение пользователем информации о своих счетах
    """
    list_scopes_user: list[dict[str, str]] = await list_scopes(
        session=db_session, id_user=user.id
    )
    return json({"scores": list_scopes_user})


@router.get("/payments")
async def get_list_payments_for_user(
    request: Request, db_session: AsyncSession, user: UserProtectedSchemas
):
    """
    Получение пользователем информации о своих платежах
    """
    list_payments_user: list[dict[str, str]] = await list_payments(
        session=db_session, user_id=user.id
    )
    return json({"payments": list_payments_user})


@router.post("/create_payment")
@openapi.definition(
    body={"application/json": PaymentGenerateBaseSchemas.schema()},
    response={
        200: {
            "description": "Успешная генерация платежного поручения с подписью",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": 2,
                        "account_id": 1,
                        "amount": 100.89,
                        "transaction_id": "c9827630-6111-4047-aa1e-2165f61d72ad",
                        "signature": "c32d3de53a030edb70a2e9e3d645b168afc21147a3922fa9a6c33efdc5caa38c",
                    }
                }
            },
        },
        401: {"description": "Неверные данные"},
        500: {"description": "Server error"},
    },
    tag="Payments",
)
async def create_payment(request: Request, db_session: AsyncSession):
    data_request = PaymentGenerateBaseSchemas(**request.json)
    payment: PaymentGenerateOutSchemas = await generate_payments(data_request)
    return json(payment.model_dump())
