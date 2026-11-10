from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.db.session import get_db
from app.modules.identity.dependencies import get_current_user, require_roles
from app.modules.identity.models import User
from app.modules.workshops.models import Client
from app.modules.workshops.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.modules.workshops.services import client_service

router = APIRouter(prefix="/clients", tags=["Clientes"])
staff = Depends(require_roles("administrador_taller", "recepcionista"))
admin = Depends(require_roles("administrador_taller"))


def workshop_scope(user: User) -> str:
    if not user.workshop_id:
        raise DomainError("Tu cuenta no tiene un taller asignado.", 403)
    return user.workshop_id


@router.get("", response_model=list[ClientRead], dependencies=[staff])
def list_clients(active_only: bool = False, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(Client).where(Client.workshop_id == workshop_scope(user)).order_by(Client.registered_at.desc())
    if active_only:
        query = query.where(Client.is_active.is_(True))
    return list(db.scalars(query))


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED, dependencies=[staff])
def create(data: ClientCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return client_service.create_client(db, data, workshop_scope(user), user.id)


@router.patch("/{client_id}", response_model=ClientRead, dependencies=[staff])
def update(client_id: str, data: ClientUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = db.scalar(select(Client).where(Client.id == client_id, Client.workshop_id == workshop_scope(user)))
    if not client:
        raise DomainError("Cliente no encontrado.", 404)
    return client_service.update_client(db, client, data, user.id)


@router.post("/{client_id}/deactivate", response_model=ClientRead, dependencies=[admin])
def deactivate(client_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = db.scalar(select(Client).where(Client.id == client_id, Client.workshop_id == workshop_scope(user)))
    if not client:
        raise DomainError("Cliente no encontrado.", 404)
    return client_service.deactivate_client(db, client, user.id)
