from datetime import datetime
from typing import Optional

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from backend.common.errors import AppError
from backend.common.security import hash_password, verify_password
from backend.extensions import db
from backend.modules.auth.models import TokenBlocklist, User


def create_user(email: str, password: str, **kwargs) -> User:
    existing = User.query.filter_by(email=email).first()
    if existing:
        raise AppError(code=2001, message="email_exists", status_code=400)
    user = User(email=email, password_hash=hash_password(password), **kwargs)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email_or_phone: str, password: str) -> User:
    user = User.query.filter(
        (User.email == email_or_phone) | (User.phone == email_or_phone)
    ).first()
    if not user or not verify_password(user.password_hash, password):
        raise AppError(code=2002, message="invalid_credentials", status_code=401)
    return user


def issue_tokens(user: User) -> dict:
    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(identity=user.id)
    return {"access": access_token, "refresh": refresh_token}


def revoke_token(jti: str, token_type: str, user_id: int, expires_at: Optional[datetime] = None) -> None:
    entry = TokenBlocklist(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        revoked=True,
        expires_at=expires_at,
    )
    db.session.add(entry)
    db.session.commit()


def is_token_revoked(jti: str) -> bool:
    record = TokenBlocklist.query.filter_by(jti=jti).first()
    return bool(record and record.revoked)
