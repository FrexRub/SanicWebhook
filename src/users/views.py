from sanic import Blueprint, json

router = Blueprint("user", url_prefix="/user")


@router.route("/login", methods=["POST"])
async def login(request):
    return json({"message": "Login successful"})