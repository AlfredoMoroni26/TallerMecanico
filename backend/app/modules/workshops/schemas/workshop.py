import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

RFC_DATE = r"\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])"
RFC_PATTERN = re.compile(rf"^(?:[A-ZÑ&]{{3}}|[A-ZÑ&]{{4}}){RFC_DATE}[A-Z0-9]{{3}}$")


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


class WorkshopCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    rfc: str
    contact_email: EmailStr
    street_address: str = Field(min_length=3, max_length=180)
    neighborhood: str = Field(min_length=2, max_length=120)
    postal_code: str = Field(pattern=r"^\d{5}$")
    state: str = Field(min_length=2, max_length=80)
    municipality: str = Field(min_length=2, max_length=100)

    @field_validator("name", "street_address", "neighborhood", "state", "municipality")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = normalize_text(value)
        if not normalized:
            raise ValueError("Este campo es obligatorio.")
        return normalized

    @field_validator("rfc")
    @classmethod
    def validate_rfc(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not RFC_PATTERN.fullmatch(normalized):
            raise ValueError("Ingresa un RFC mexicano válido de 12 o 13 caracteres.")
        return normalized


class WorkshopRead(BaseModel):
    id: str
    name: str
    rfc: str
    contact_email: EmailStr
    street_address: str
    neighborhood: str
    postal_code: str
    state: str
    municipality: str
    photo_path: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LocationOption(BaseModel):
    id: str
    name: str


class PostalLookup(BaseModel):
    postal_code: str
    state: str
    municipality: str
    neighborhoods: list[str]


class SettlementOption(BaseModel):
    name: str
    postal_code: str
