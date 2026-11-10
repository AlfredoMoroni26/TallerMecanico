from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.db.session import get_db
from app.modules.identity.dependencies import require_roles
from app.modules.workshops.models import Workshop
from app.modules.workshops.schemas.workshop import LocationOption, PostalLookup, SettlementOption, WorkshopCreate, WorkshopRead
from app.modules.workshops.services import postal_service, workshop_service
from app.modules.workshops.services.storage import delete_photo, save_workshop_photo

router = APIRouter(prefix="/workshops", tags=["Alta de taller mecánico"])
authorized = Depends(require_roles("administrador_taller", "recepcionista", "secretaria"))
admin = Depends(require_roles("administrador_taller"))


@router.get("/options", dependencies=[admin])
def options(db: Session = Depends(get_db)):
    return [{"id": workshop.id, "name": workshop.name} for workshop in db.query(Workshop).order_by(Workshop.name)]


@router.get("/location/states", response_model=list[LocationOption], dependencies=[authorized])
def states():
    return postal_service.list_states()


@router.get("/location/states/{state_id}/municipalities", response_model=list[LocationOption], dependencies=[authorized])
def municipalities(state_id: str):
    return postal_service.list_municipalities(state_id)


@router.get("/location/settlements", response_model=list[SettlementOption], dependencies=[authorized])
def settlements(state: str, municipality: str, query: str):
    return postal_service.search_settlements(state, municipality, query)


@router.get("/location/postal-codes/{postal_code}", response_model=PostalLookup, dependencies=[authorized])
def postal_code(postal_code: str):
    if not postal_code.isdigit() or len(postal_code) != 5:
        raise DomainError("El código postal debe contener 5 dígitos.", 422)
    return postal_service.lookup_postal_code(postal_code)


@router.post("", response_model=WorkshopRead, status_code=status.HTTP_201_CREATED, dependencies=[authorized])
async def create(
    name: str = Form(), rfc: str = Form(), contact_email: str = Form(), street_address: str = Form(),
    neighborhood: str = Form(), postal_code: str = Form(), state: str = Form(), municipality: str = Form(),
    photo: UploadFile = File(), db: Session = Depends(get_db),
):
    try:
        data = WorkshopCreate.model_validate({
            "name": name, "rfc": rfc, "contact_email": contact_email, "street_address": street_address,
            "neighborhood": neighborhood, "postal_code": postal_code, "state": state, "municipality": municipality,
        })
    except ValidationError as error:
        raise DomainError(error.errors()[0]["msg"], 422) from error

    workshop_service.ensure_not_duplicate(db, data)
    photo_path = await save_workshop_photo(photo)
    try:
        return workshop_service.create_workshop(db, data, photo_path)
    except IntegrityError as error:
        db.rollback()
        delete_photo(photo_path)
        raise DomainError("No fue posible registrar el taller porque sus datos ya existen.", 409) from error
    except Exception:
        delete_photo(photo_path)
        raise
