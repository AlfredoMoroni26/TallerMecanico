import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.modules.workshops.schemas.workshop import RFC_PATTERN, normalize_text


class ClientBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=80)
    paternal_last_name: str = Field(min_length=2, max_length=80)
    maternal_last_name: str = Field(min_length=2, max_length=80)
    phone: str = Field(min_length=10, max_length=20)
    email: EmailStr
    rfc: str | None = Field(default=None, max_length=13)
    street_address: str = Field(min_length=3, max_length=180)
    neighborhood: str = Field(min_length=2, max_length=120)
    postal_code: str = Field(pattern=r"^\d{5}$")
    state: str = Field(min_length=2, max_length=80)
    municipality: str = Field(min_length=2, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("first_name", "paternal_last_name", "maternal_last_name", "street_address", "neighborhood", "state", "municipality")
    @classmethod
    def normalize_text_fields(cls, value: str) -> str:
        return normalize_text(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        normalized = re.sub(r"\D", "", value)
        if len(normalized) != 10:
            raise ValueError("El teléfono debe contener 10 dígitos.")
        return normalized

    @field_validator("rfc")
    @classmethod
    def normalize_rfc(cls, value: str | None) -> str | None:
        if not value or not value.strip():
            return None
        normalized = value.strip().upper()
        if not RFC_PATTERN.fullmatch(normalized):
            raise ValueError("Ingresa un RFC mexicano válido de 12 o 13 caracteres.")
        return normalized


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientRead(ClientBase):
    id: str
    workshop_id: str
    is_active: bool
    registered_at: datetime
    updated_at: datetime
    deactivated_at: datetime | None
    model_config = {"from_attributes": True}


class VehicleFields(BaseModel):
    vin: str = Field(min_length=17, max_length=17)
    plate: str = Field(min_length=3, max_length=12)
    brand: str = Field(min_length=2, max_length=60)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1900, le=2100)
    version: str = Field(min_length=1, max_length=80)
    color: str = Field(min_length=2, max_length=50)
    mileage: int | None = Field(default=None, ge=0)

    @field_validator("vin")
    @classmethod
    def normalize_vin(cls, value: str) -> str:
        normalized = value.replace(" ", "").upper()
        if not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", normalized):
            raise ValueError("El VIN debe tener 17 caracteres válidos, sin I, O ni Q.")
        return normalized

    @field_validator("plate")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9]", "", value).upper()
        if not re.fullmatch(r"[A-Z0-9]{3,12}", normalized):
            raise ValueError("La placa debe contener de 3 a 12 caracteres alfanuméricos.")
        return normalized


class VehicleCreate(VehicleFields):
    client_id: str


class VehicleUpdate(BaseModel):
    """Datos editables; VIN, cliente y taller permanecen inmutables."""
    plate: str = Field(min_length=3, max_length=12)
    brand: str = Field(min_length=2, max_length=60)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1900, le=2100)
    version: str = Field(min_length=1, max_length=80)
    color: str = Field(min_length=2, max_length=50)
    mileage: int = Field(ge=0)
    model_config = {"extra": "forbid"}

    @field_validator("plate")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9]", "", value).upper()
        if not re.fullmatch(r"[A-Z0-9]{3,12}", normalized):
            raise ValueError("La placa debe contener de 3 a 12 caracteres alfanuméricos.")
        return normalized


class VehicleRead(VehicleCreate):
    id: str
    workshop_id: str
    is_active: bool
    photo_path: str | None
    created_at: datetime
    client_name: str
    model_config = {"from_attributes": True}
