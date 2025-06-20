from sanic import Request, Sanic, html, json
from sanic.exceptions import SanicException
from sanic_ext import Extend, openapi
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import ConnectionsConfig
from src.core.database import DatabaseConnection
from src.core.depends import current_superuser_user, current_user
from src.core.exceptions import (
    ErrorInData,
    PaymentProcessed,
)
from src.payments.schemas import TransactionInSchemas
from src.payments.views import router as router_payments
from src.users.schemas import UserProtectedSchemas, UserSuperSchemas
from src.users.views import router as router_user
from src.utils.processing import process_transaction


class WebhookApp(Sanic):
    def __init__(self, *args, **kwargs):
        test_mode = kwargs.pop("test_mode", False)
        super().__init__(*args, **kwargs)
        self.ctx._test_mode = test_mode

    def setup_db(self, config=None):
        """Настройка подключения к БД с возможностью переопределения для тестов"""
        config = config or self.config
        if self.ctx._test_mode:
            config.DB_DRIVER = "postgresql+asyncpg"
            config.DB_USER = "test"
            config.DB_PASSWORD = "test"
            config.DB_HOST = "localhost"
            config.DB_PORT = 5432
            config.DB_NAME = "testdb"

        db_conn = DatabaseConnection(config)
        db_session: AsyncSession = db_conn.create_session()
        self.ext.dependency(db_session)


app = WebhookApp("WebhookApp", test_mode=False)
Extend(app)

app.update_config(ConnectionsConfig)
app.setup_db()

app.blueprint(router_user)
app.blueprint(router_payments)

app.ext.add_dependency(UserSuperSchemas, current_superuser_user)
app.ext.add_dependency(UserProtectedSchemas, current_user)


@app.exception(SanicException)
async def handle_sanic_exception(request, exception):
    return json(
        {"error": exception.message, "status": exception.status_code},
        status=exception.status_code,
    )


@app.get("/")
async def index(request):
    return html("<h2> * Transaction handler * </h2>")


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
