from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from .role import RoleRead


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role_ids: list[str] = Field(default_factory=list)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(char.isupper() for char in value) or not any(char.islower() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("La contraseña debe incluir mayúscula, minúscula y número.")
        return value


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr | None = None
    is_active: bool | None = None
    role_ids: list[str] | None = None


class UserRead(BaseModel):
    id: str
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    roles: list[RoleRead]

    model_config = {"from_attributes": True}
