from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    unset_jwt_cookies,
)

from backend.common.errors import AppError
from backend.common.response import response_ok
from backend.extensions import jwt
from backend.modules.auth.models import TokenBlocklist, User
from backend.modules.auth.service import (
    authenticate,
    create_user,
    is_token_revoked,
    revoke_token,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return is_token_revoked(jwt_payload["jti"])


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return response_error(2003, "token_revoked", 401)


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return response_error(1002, "invalid_token", 401)


@jwt.unauthorized_loader
def missing_token_callback(error):
    return response_error(1002, "missing_authorization", 401)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return response_error(1004, "token_expired", 401)


def _parse_json(required_fields):
    data = request.get_json() or {}
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        raise AppError(code=1001, message=f"missing_fields:{','.join(missing)}", status_code=400)
    return data


@auth_bp.post("/register")
def register():
    data = _parse_json(["email", "password"])
    user = create_user(email=data["email"], password=data["password"])
    tokens = {
        "access": create_access_token(identity=user.id, fresh=True),
        "refresh": create_refresh_token(identity=user.id),
    }
    return response_ok({"user_id": user.id, "tokens": tokens}, "registered")


@auth_bp.post("/login")
def login():
    data = _parse_json(["account", "password"])
    user = authenticate(data["account"], data["password"])
    tokens = {
        "access": create_access_token(identity=user.id, fresh=True),
        "refresh": create_refresh_token(identity=user.id),
    }
    return response_ok({"user_id": user.id, "tokens": tokens}, "login_success")


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    jti = get_jwt()["jti"]
    if is_token_revoked(jti):
        raise AppError(code=2003, message="token_revoked", status_code=401)
    new_access = create_access_token(identity=identity, fresh=False)
    return response_ok({"access": new_access}, "refreshed")


@auth_bp.post("/logout")
@jwt_required(verify_type=False)
def logout():
    jwt_payload = get_jwt()
    jti = jwt_payload["jti"]
    token_type = jwt_payload["type"]
    identity = jwt_payload["sub"]
    expires = datetime.fromtimestamp(jwt_payload["exp"])
    revoke_token(jti=jti, token_type=token_type, user_id=identity, expires_at=expires)
    resp = response_ok(message="logged_out")
    unset_jwt_cookies(resp[0])
    return resp
