from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.db.session import get_db
from app.modules.identity.dependencies import require_roles
from app.modules.identity.models import Role
from app.modules.identity.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.modules.identity.services import identity_service as service

router = APIRouter(prefix="/roles", tags=["Roles"])
admin = Depends(require_roles("administrador_taller"))

@router.get("", response_model=list[RoleRead], dependencies=[admin])
def list_roles(db: Session = Depends(get_db)):
    return list(db.scalars(select(Role).order_by(Role.name)))

@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED, dependencies=[admin])
def create(data: RoleCreate, db: Session = Depends(get_db)):
    return service.create_role(db, data)

@router.patch("/{role_id}", response_model=RoleRead, dependencies=[admin])
def update(role_id: str, data: RoleUpdate, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise DomainError("Rol no encontrado.", 404)
    return service.update_role(db, role, data)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin])
def delete(role_id: str, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise DomainError("Rol no encontrado.", 404)
    if role.is_system:
        raise DomainError("Los roles del sistema no se pueden eliminar.", 403)
    db.delete(role); db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
