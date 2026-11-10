import json
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.modules.workshops.models import Client, ClientAudit, Vehicle
from app.modules.workshops.schemas.client import ClientBase, VehicleCreate, VehicleUpdate


def _same(value: str) -> str:
    return " ".join(value.casefold().split())


def _duplicate(db: Session, data: ClientBase, exclude_id: str | None = None) -> Client | None:
    query = select(Client)
    if exclude_id:
        query = query.where(Client.id != exclude_id)
    clauses = [Client.email == data.email]
    if data.rfc:
        clauses.append(Client.rfc == data.rfc)
    clauses.append((func.lower(Client.first_name) == _same(data.first_name)) & (func.lower(Client.paternal_last_name) == _same(data.paternal_last_name)) & (func.lower(Client.maternal_last_name) == _same(data.maternal_last_name)) & (Client.phone == data.phone))
    return db.scalar(query.where(or_(*clauses)))


def assert_no_duplicate(db: Session, data: ClientBase, workshop_id: str, exclude_id: str | None = None) -> None:
    duplicate = _duplicate(db, data, exclude_id)
    if duplicate:
        if duplicate.workshop_id != workshop_id:
            raise DomainError("Este cliente ya se encuentra registrado y asociado a otro taller mecánico.", 409)
        raise DomainError("Este cliente ya se encuentra registrado en el sistema. No es posible continuar con el registro.", 409)


def audit(db: Session, client_id: str, actor_id: str, action: str, changes: dict[str, object] | None = None) -> None:
    db.add(ClientAudit(client_id=client_id, actor_user_id=actor_id, action=action, changes=json.dumps(changes, ensure_ascii=False) if changes else None))


def create_client(db: Session, data: ClientBase, workshop_id: str, actor_id: str) -> Client:
    assert_no_duplicate(db, data, workshop_id)
    client = Client(workshop_id=workshop_id, **data.model_dump())
    db.add(client); db.flush(); audit(db, client.id, actor_id, "created"); db.commit(); db.refresh(client)
    return client


def update_client(db: Session, client: Client, data: ClientBase, actor_id: str) -> Client:
    assert_no_duplicate(db, data, client.workshop_id, client.id)
    changes = {field: {"before": getattr(client, field), "after": value} for field, value in data.model_dump().items() if getattr(client, field) != value}
    for field, value in data.model_dump().items():
        setattr(client, field, value)
    if changes:
        audit(db, client.id, actor_id, "updated", changes)
        db.commit(); db.refresh(client)
    return client


def deactivate_client(db: Session, client: Client, actor_id: str) -> Client:
    if not client.is_active:
        raise DomainError("El cliente ya está inactivo.", 409)
    client.is_active = False
    client.deactivated_at = datetime.now(UTC)
    client.deactivated_by_user_id = actor_id
    audit(db, client.id, actor_id, "deactivated")
    db.commit(); db.refresh(client)
    return client


def create_vehicle(db: Session, data: VehicleCreate, workshop_id: str, photo_path: str) -> Vehicle:
    client = db.scalar(select(Client).where(Client.id == data.client_id, Client.workshop_id == workshop_id))
    if not client:
        raise DomainError("El cliente no pertenece a tu taller.", 404)
    if not client.is_active:
        raise DomainError("No se pueden registrar vehículos para clientes inactivos.", 409)
    if db.scalar(select(Vehicle.id).where(Vehicle.vin == data.vin)):
        raise DomainError("Este vehículo ya se encuentra registrado. El número de serie o VIN debe ser único.", 409)
    vehicle = Vehicle(workshop_id=workshop_id, photo_path=photo_path, **data.model_dump())
    db.add(vehicle); db.commit(); db.refresh(vehicle)
    return vehicle


def update_vehicle(db: Session, vehicle: Vehicle, data: VehicleUpdate) -> Vehicle:
    """Actualiza datos editables sin permitir cambiar VIN, cliente o taller."""
    for field, value in data.model_dump().items():
        setattr(vehicle, field, value)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def set_vehicle_active(db: Session, vehicle: Vehicle, is_active: bool) -> Vehicle:
    """Cambia el estado lógico de un vehículo, conservando su historial."""
    if vehicle.is_active == is_active:
        state = "activo" if is_active else "inactivo"
        raise DomainError(f"El vehículo ya se encuentra {state}.", 409)
    vehicle.is_active = is_active
    db.commit()
    db.refresh(vehicle)
    return vehicle
