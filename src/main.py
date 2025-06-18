from sanic import Sanic, json
from sanic_ext import Extend
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.views import router as router_user
from sanic.exceptions import SanicException

from src.core.config import ConnectionsConfig
from src.core.database import DatabaseConnection
from src.core.depends import current_superuser_user, current_user
from src.users.schemas import UserSuperSchemas, UserProtectedSchemas


app = Sanic("WebhookApp")
Extend(app)

app.blueprint(router_user)
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
        status=exception.status_code
    )


@app.get("/")
async def hello(request):
    return json({"message": "Login successful"})


if __name__ == "__main__":
    app.run(port=8000, auto_reload=True)
