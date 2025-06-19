from sanic import Sanic, html, json, Request
from sanic_ext import Extend, openapi
from sanic.exceptions import SanicException
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.views import router as router_user
from src.payments.views import router as router_payments

from src.core.config import ConnectionsConfig
from src.core.database import DatabaseConnection
from src.core.depends import current_superuser_user, current_user
from src.users.schemas import UserSuperSchemas, UserProtectedSchemas
from src.utils.processing import process_transaction
from src.payments.schemas import TransactionInSchemas
from src.core.exceptions import (
    PaymentProcessed,
    ErrorInData,
)


app = Sanic("WebhookApp")
Extend(app)

app.blueprint(router_user)
app.blueprint(router_payments)
app.update_config(ConnectionsConfig)

app.ext.add_dependency(UserSuperSchemas, current_superuser_user)
app.ext.add_dependency(UserProtectedSchemas, current_user)


@app.before_server_start
async def setup_db(application: Sanic, request) -> None:
    db_conn = DatabaseConnection(application.config)
    db_session: AsyncSession = db_conn.create_session()

    application.ext.dependency(db_session)


@app.exception(SanicException)
async def handle_sanic_exception(request, exception):
    return json(
        {"error": exception.message, "status": exception.status_code},
        status=exception.status_code,
    )


@app.get("/")
async def hello(request):
    return html("<h2> Transaction handler</h2>")


@app.post("/webhook")
@openapi.definition(
    body={"application/json": TransactionInSchemas.schema()},
    response={
        200: {
            "description": "Успешная обработка поступившего платежа",
            "content": {
                "application/json": {
                    "example": {
                        "result": "ok",
                    }
                }
            },
        },
        400: {"description": "Неверные данные"},
        500: {"description": "Server error"},
    },
    tag="Webhook",
)
async def transaction(request: Request, db_session: AsyncSession):
    data_request = TransactionInSchemas(**request.json)
    try:
        await process_transaction(session=db_session, data_request=data_request)
    except ErrorInData as exp:
        raise SanicException(f"{exp}", status_code=400)
    except PaymentProcessed as exp:
        raise SanicException(f"{exp}", status_code=400)
    return json({"result": "ok"})


if __name__ == "__main__":
    app.run(port=8000, auto_reload=True)
