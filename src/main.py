from sanic import Sanic, json
from sanic_ext import Extend
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.views import router as router_user

from src.core.config import ConnectionsConfig
from src.core.database import DatabaseConnection


app = Sanic("WebhookApp")
Extend(app)
app.blueprint(router_user)
app.update_config(ConnectionsConfig)


@app.before_server_start
async def setup_db(application: Sanic, _) -> None:
    db_conn = DatabaseConnection(application.config)
    db_session: AsyncSession = db_conn.create_session()

    application.ext.dependency(db_session)


@app.get("/")
async def hello(request):
    return json({"message": "Login successful"})


if __name__ == "__main__":
    app.run(port=8000, auto_reload=True)
