from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.db.session import get_db
from app.modules.identity.dependencies import get_current_user, require_roles
from app.modules.identity.models import User
from app.modules.workshops.models import Vehicle
from app.modules.workshops.routes.clients import workshop_scope
from app.modules.workshops.schemas.client import VehicleCreate, VehicleRead, VehicleUpdate
from app.modules.workshops.services.client_service import create_vehicle, set_vehicle_active, update_vehicle
from app.modules.workshops.services.storage import save_vehicle_photo

router = APIRouter(prefix="/vehicles", tags=["Vehículos"])
staff = Depends(require_roles("administrador_taller", "recepcionista"))


@router.get("", response_model=list[VehicleRead], dependencies=[staff])
def list_vehicles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(Vehicle).where(Vehicle.workshop_id == workshop_scope(user)).order_by(Vehicle.created_at.desc())
    return list(db.scalars(query))


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED, dependencies=[staff])
async def create(
    client_id: str = Form(), vin: str = Form(), plate: str = Form(), brand: str = Form(), model: str = Form(),
    year: int = Form(), version: str = Form(), color: str = Form(), mileage: int | None = Form(default=None),
    photo: UploadFile = File(), db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    try:
        data = VehicleCreate.model_validate({"client_id": client_id, "vin": vin, "plate": plate, "brand": brand, "model": model, "year": year, "version": version, "color": color, "mileage": mileage})
    except ValidationError as error:
        raise DomainError(error.errors()[0]["msg"], 422) from error
    photo_path = await save_vehicle_photo(photo)
    return create_vehicle(db, data, workshop_scope(user), photo_path)


@router.patch("/{vehicle_id}", response_model=VehicleRead, dependencies=[staff])
def update(vehicle_id: str, data: VehicleUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    vehicle = db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.workshop_id == workshop_scope(user)))
    if not vehicle:
        raise DomainError("Vehículo no encontrado.", 404)
    return update_vehicle(db, vehicle, data)


@router.patch("/{vehicle_id}/deactivate", response_model=VehicleRead, dependencies=[staff])
def deactivate(vehicle_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    vehicle = db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.workshop_id == workshop_scope(user)))
    if not vehicle:
        raise DomainError("Vehículo no encontrado.", 404)
    return set_vehicle_active(db, vehicle, False)


@router.patch("/{vehicle_id}/activate", response_model=VehicleRead, dependencies=[staff])
def activate(vehicle_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    vehicle = db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.workshop_id == workshop_scope(user)))
    if not vehicle:
        raise DomainError("Vehículo no encontrado.", 404)
    return set_vehicle_active(db, vehicle, True)
