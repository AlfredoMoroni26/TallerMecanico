import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.modules.workshops.models import Workshop
from app.modules.workshops.schemas.workshop import WorkshopCreate


def _canonical(value: str) -> str:
    return " ".join(value.casefold().split())


def ensure_not_duplicate(db: Session, data: WorkshopCreate) -> None:
    if db.scalar(select(Workshop.id).where(Workshop.rfc == data.rfc)):
        raise DomainError("Ese RFC ya se encuentra registrado.", 409)
    same_establishment = db.scalar(
        select(Workshop.id).where(
            func.lower(Workshop.name) == _canonical(data.name),
            func.lower(Workshop.street_address) == _canonical(data.street_address),
            func.lower(Workshop.neighborhood) == _canonical(data.neighborhood),
            Workshop.postal_code == data.postal_code,
        )
    )
    if same_establishment:
        raise DomainError("Este taller ya se encuentra registrado con la misma dirección.", 409)


def create_workshop(db: Session, data: WorkshopCreate, photo_path: str) -> Workshop:
    ensure_not_duplicate(db, data)
    workshop = Workshop(**data.model_dump(), photo_path=photo_path)
    db.add(workshop)
    db.commit()
    db.refresh(workshop)
    return workshop
