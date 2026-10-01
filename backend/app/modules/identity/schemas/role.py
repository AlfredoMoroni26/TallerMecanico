from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    name: str = Field(min_length=3, max_length=80, pattern=r"^[a-z_]+$")
    description: str | None = Field(default=None, max_length=255)


class RoleUpdate(BaseModel):
    description: str | None = Field(default=None, max_length=255)


class RoleRead(BaseModel):
    id: str
    name: str
    description: str | None
    is_system: bool

    model_config = {"from_attributes": True}
