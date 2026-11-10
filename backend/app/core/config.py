from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Taller Mecánico API"
    database_url: str = "sqlite:///./taller_mecanico.db"
    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    frontend_origins: str = "http://localhost:5173"
    initial_admin_username: str | None = None
    initial_admin_email: str | None = None
    initial_admin_password: str | None = None
    postal_api_base_url: str = "https://cpostal.mx/api/v1"
    postal_api_key: str | None = None
    uploads_root: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_postgres_url(cls, value: str) -> str:
        """Acepta la URL estándar de Railway y selecciona el driver psycopg."""
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
