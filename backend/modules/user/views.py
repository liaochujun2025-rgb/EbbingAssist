from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.common.response import response_ok
from backend.modules.auth.models import User

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.get("/profile")
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname or user.email.split("@")[0],
        "avatar": user.avatar,
        "timezone": user.timezone,
        "roles": ["user"],
        "prefs": user.prefs or {},
    }
    return response_ok(data)
