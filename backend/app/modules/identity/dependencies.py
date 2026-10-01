from collections.abc import Callable

import jwt
from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.core.security import decode_token
from app.db.session import get_db
from app.modules.identity.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise DomainError("Se requiere autenticación.", 401)
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError:
        raise DomainError("La sesión no es válida o expiró.", 401)
    if payload.get("type") != "access":
        raise DomainError("Token de acceso inválido.", 401)
    user = db.get(User, payload.get("sub"))
    if not user or not user.is_active:
        raise DomainError("La cuenta no está disponible.", 401)
    return user


def require_roles(*allowed_roles: str) -> Callable:
    def check(user: User = Depends(get_current_user)) -> User:
        if not set(allowed_roles).intersection(role.name for role in user.roles):
            raise DomainError("No tienes permiso para realizar esta acción.", 403)
        return user
    return check


def get_user_agent(user_agent: str | None = Header(default=None)) -> str | None:
    return user_agent
