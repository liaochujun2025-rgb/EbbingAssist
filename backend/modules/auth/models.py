from datetime import datetime
from uuid import uuid4

from backend.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(32), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(64), nullable=True)
    avatar = db.Column(db.String(512), nullable=True)
    timezone = db.Column(db.String(64), default="UTC")
    prefs = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class TokenBlocklist(db.Model):
    __tablename__ = "auth_tokens"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    token_type = db.Column(db.String(16), nullable=False)  # access/refresh
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Token {self.jti} revoked={self.revoked}>"

    @staticmethod
    def new_jti() -> str:
        return str(uuid4())
