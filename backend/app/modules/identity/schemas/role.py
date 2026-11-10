import re

from pydantic import BaseModel, Field, field_validator


class RoleCreate(BaseModel):
    name: str = Field(min_length=3, max_length=80)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Una forma canónica evita duplicados por espacios o mayúsculas."""
        normalized = "_".join(value.strip().casefold().split())
        if not re.fullmatch(r"[a-z0-9_]{3,80}", normalized):
            raise ValueError("El nombre debe contener letras, números o espacios.")
        return normalized


class RoleRename(BaseModel):
    name: str = Field(min_length=3, max_length=80)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return RoleCreate.normalize_name(value)


class RoleUpdate(BaseModel):
    description: str | None = Field(default=None, max_length=255)


class StatusRead(BaseModel):
    id_estatus: int
    nombre_estatus: str

    model_config = {"from_attributes": True}


class RoleRead(BaseModel):
    id: str
    id_rol: int
    name: str
    description: str | None
    is_system: bool
    id_estatus: int
    estatus: StatusRead

    model_config = {"from_attributes": True}
