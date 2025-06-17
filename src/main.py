from sanic import Sanic, json
from sanic_ext import Extend

from src.users.views import router as router_user


app = Sanic("WebhookApp")
Extend(app)
app.blueprint(router_user)

@app.get("/")
async def hello(request):
    return json({"message": "Login successful"})

if __name__ == "__main__":
    app.run(port=8000, auto_reload=True)