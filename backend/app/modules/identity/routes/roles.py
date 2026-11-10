from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import DomainError
from app.db.session import get_db
from app.modules.identity.dependencies import require_roles
from app.modules.identity.models import Role
from app.modules.identity.schemas.role import RoleCreate, RoleRead, RoleRename
from app.modules.identity.services import identity_service as service

router = APIRouter(prefix="/roles", tags=["Roles"])
admin = Depends(require_roles("administrador_taller"))

@router.get("", response_model=list[RoleRead], dependencies=[admin])
def list_roles(db: Session = Depends(get_db)):
    return list(db.scalars(select(Role).options(selectinload(Role.estatus)).order_by(Role.name)))

@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED, dependencies=[admin])
def create(data: RoleCreate, db: Session = Depends(get_db)):
    return service.create_role(db, data)

@router.patch("/{role_id}/name", response_model=RoleRead, dependencies=[admin])
def rename(role_id: str, data: RoleRename, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise DomainError("Rol no encontrado.", 404)
    return service.rename_role(db, role, data)

@router.patch("/{role_id}/suspend", response_model=RoleRead, dependencies=[admin])
def suspend(role_id: str, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise DomainError("Rol no encontrado.", 404)
    return service.suspend_role(db, role)


@router.patch("/{role_id}/activate", response_model=RoleRead, dependencies=[admin])
def activate(role_id: str, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise DomainError("Rol no encontrado.", 404)
    return service.activate_role(db, role)
