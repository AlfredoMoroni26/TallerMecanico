import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Nunca persiste la contraseña; bcrypt incluye sal única por hash."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(subject: str, token_type: str, expires_delta: timedelta, roles: list[str] | None = None) -> str:
    now = datetime.now(UTC)
    payload = {"sub": subject, "type": token_type, "iat": now, "exp": now + expires_delta, "jti": secrets.token_urlsafe(24)}
    if roles is not None:
        payload["roles"] = roles
    return jwt.encode(payload, get_settings().secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITHM])


def token_digest(token: str) -> str:
    """Guarda un digest del token de refresh/reset, nunca el token original."""
    return hashlib.sha256(token.encode()).hexdigest()
