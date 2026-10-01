from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.core.security import create_token, decode_token, hash_password, token_digest, verify_password
from app.modules.identity.models import PasswordResetToken, Role, Session as UserSession, User
from app.modules.identity.schemas.auth import TokenPair
from app.modules.identity.schemas.role import RoleCreate, RoleUpdate
from app.modules.identity.schemas.user import UserCreate, UserUpdate

DEFAULT_ROLES = [
    ("administrador_taller", "Administración integral del taller"),
    ("recepcionista", "Recepción de clientes y vehículos"),
    ("asesor_servicio", "Asesoría y seguimiento de servicio"),
    ("tecnico", "Ejecución técnica de órdenes"),
    ("cliente", "Portal de cliente"),
    ("sistema", "Cuenta de integración interna"),
]


def seed_roles(db: Session) -> None:
    if db.scalar(select(Role.id).limit(1)) is None:
        db.add_all([Role(name=name, description=description, is_system=True) for name, description in DEFAULT_ROLES])
        db.commit()


def seed_initial_admin(db: Session) -> None:
    """Crea el primer administrador sólo si se configuró explícitamente en el entorno."""
    settings = get_settings()
    if not all([settings.initial_admin_username, settings.initial_admin_email, settings.initial_admin_password]):
        return
    if db.scalar(select(User.id).where(User.email == settings.initial_admin_email.lower())):
        return
    admin_role = db.scalar(select(Role).where(Role.name == "administrador_taller"))
    if not admin_role:
        return
    db.add(User(username=settings.initial_admin_username, email=settings.initial_admin_email.lower(), password_hash=hash_password(settings.initial_admin_password), roles=[admin_role]))
    db.commit()


def _roles_by_ids(db: Session, role_ids: list[str]) -> list[Role]:
    if not role_ids:
        return []
    roles = list(db.scalars(select(Role).where(Role.id.in_(role_ids))))
    if len(roles) != len(set(role_ids)):
        raise DomainError("Uno o más roles no existen.", 422)
    return roles


def create_user(db: Session, data: UserCreate, allow_roles: bool = False) -> User:
    if db.scalar(select(User).where(User.email == data.email.lower())):
        raise DomainError("El correo electrónico ya está registrado.", 409)
    if db.scalar(select(User).where(User.username == data.username)):
        raise DomainError("El nombre de usuario ya está registrado.", 409)
    roles = _roles_by_ids(db, data.role_ids)
    if not allow_roles:
        roles = list(db.scalars(select(Role).where(Role.name == "cliente")))
    user = User(username=data.username, email=data.email.lower(), password_hash=hash_password(data.password), roles=roles)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    values = data.model_dump(exclude_unset=True)
    if "email" in values:
        email = values["email"].lower()
        duplicate = db.scalar(select(User).where(User.email == email, User.id != user.id))
        if duplicate:
            raise DomainError("El correo electrónico ya está registrado.", 409)
        user.email = email
    if "username" in values:
        duplicate = db.scalar(select(User).where(User.username == values["username"], User.id != user.id))
        if duplicate:
            raise DomainError("El nombre de usuario ya está registrado.", 409)
        user.username = values["username"]
    if "is_active" in values:
        user.is_active = values["is_active"]
    if "role_ids" in values:
        user.roles = _roles_by_ids(db, values["role_ids"])
    db.commit()
    db.refresh(user)
    return user


def create_role(db: Session, data: RoleCreate) -> Role:
    if db.scalar(select(Role).where(Role.name == data.name)):
        raise DomainError("El nombre del rol ya existe.", 409)
    role = Role(**data.model_dump())
    db.add(role); db.commit(); db.refresh(role)
    return role


def update_role(db: Session, role: Role, data: RoleUpdate) -> Role:
    if role.is_system:
        raise DomainError("Los roles del sistema no se pueden modificar.", 403)
    role.description = data.description
    db.commit(); db.refresh(role)
    return role


def issue_tokens(db: Session, user: User, user_agent: str | None = None) -> TokenPair:
    settings = get_settings()
    access = create_token(user.id, "access", timedelta(minutes=settings.access_token_expire_minutes), [r.name for r in user.roles])
    refresh = create_token(user.id, "refresh", timedelta(days=settings.refresh_token_expire_days))
    db.add(UserSession(user_id=user.id, refresh_token_hash=token_digest(refresh), expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days), user_agent=(user_agent or "")[:255]))
    db.commit()
    return TokenPair(access_token=access, refresh_token=refresh)


def authenticate(db: Session, login: str, password: str, user_agent: str | None) -> TokenPair:
    user = db.scalar(select(User).where(or_(User.email == login.lower(), User.username == login)))
    # Mismo mensaje para no revelar si una cuenta existe.
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        raise DomainError("Credenciales inválidas o cuenta inactiva.", 401)
    return issue_tokens(db, user, user_agent)


def refresh_tokens(db: Session, refresh_token: str, user_agent: str | None) -> TokenPair:
    try:
        payload = decode_token(refresh_token)
    except jwt.PyJWTError:
        raise DomainError("La sesión expiró. Inicia sesión nuevamente.", 401)
    if payload.get("type") != "refresh":
        raise DomainError("Token de sesión inválido.", 401)
    session = db.scalar(select(UserSession).where(UserSession.refresh_token_hash == token_digest(refresh_token)))
    if not session or session.revoked_at or session.expires_at.replace(tzinfo=UTC) <= datetime.now(UTC) or not session.user.is_active:
        raise DomainError("La sesión expiró. Inicia sesión nuevamente.", 401)
    session.revoked_at = datetime.now(UTC)  # rotación: el refresh anterior deja de servir
    db.commit()
    return issue_tokens(db, session.user, user_agent)


def revoke_session(db: Session, refresh_token: str) -> None:
    session = db.scalar(select(UserSession).where(UserSession.refresh_token_hash == token_digest(refresh_token)))
    if session and not session.revoked_at:
        session.revoked_at = datetime.now(UTC)
        db.commit()


def request_reset(db: Session, email: str) -> str | None:
    user = db.scalar(select(User).where(User.email == email.lower(), User.is_active.is_(True)))
    if not user:
        return None
    raw_token = create_token(user.id, "password_reset", timedelta(minutes=30))
    db.add(PasswordResetToken(user_id=user.id, token_hash=token_digest(raw_token), expires_at=datetime.now(UTC) + timedelta(minutes=30)))
    db.commit()
    return raw_token


def reset_password(db: Session, raw_token: str, new_password: str) -> None:
    try:
        payload = decode_token(raw_token)
    except jwt.PyJWTError:
        raise DomainError("El enlace de recuperación es inválido o expiró.", 400)
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_digest(raw_token)))
    if payload.get("type") != "password_reset" or not token or token.used_at or token.expires_at.replace(tzinfo=UTC) <= datetime.now(UTC):
        raise DomainError("El enlace de recuperación es inválido o expiró.", 400)
    user = db.get(User, token.user_id)
    if not user:
        raise DomainError("El enlace de recuperación es inválido o expiró.", 400)
    user.password_hash = hash_password(new_password)
    token.used_at = datetime.now(UTC)
    for session in user.sessions:
        session.revoked_at = datetime.now(UTC)
    db.commit()
