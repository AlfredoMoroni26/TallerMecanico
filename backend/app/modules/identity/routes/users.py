from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.db.session import get_db
from app.modules.identity.dependencies import get_current_user, require_roles
from app.modules.identity.models import User
from app.modules.identity.schemas.user import UserCreate, UserRead, UserUpdate
from app.modules.identity.services import identity_service as service

router = APIRouter(prefix="/users", tags=["Usuarios"])
admin = Depends(require_roles("administrador_taller"))


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("", response_model=list[UserRead], dependencies=[admin])
def list_users(db: Session = Depends(get_db)):
    return list(db.scalars(select(User).order_by(User.created_at.desc())))


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[admin])
def create(data: UserCreate, db: Session = Depends(get_db)):
    return service.create_user(db, data, allow_roles=True)


@router.get("/{user_id}", response_model=UserRead, dependencies=[admin])
def get_one(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise DomainError("Usuario no encontrado.", 404)
    return user


@router.patch("/{user_id}", response_model=UserRead, dependencies=[admin])
def update(user_id: str, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise DomainError("Usuario no encontrado.", 404)
    return service.update_user(db, user, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin])
def deactivate(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise DomainError("Usuario no encontrado.", 404)
    user.is_active = False  # baja lógica: conserva historial y revoca sesiones.
    for session in user.sessions:
        if not session.revoked_at:
            from datetime import UTC, datetime
            session.revoked_at = datetime.now(UTC)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
