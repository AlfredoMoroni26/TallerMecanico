from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.config import get_settings


def _cors_headers(request: Request) -> dict[str, str]:
    """Conserva CORS en errores de dominio generados antes de la ruta."""
    origin = request.headers.get("origin")
    if origin and origin in get_settings().cors_origins:
        return {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true", "Vary": "Origin"}
    return {}


class DomainError(Exception):
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code


async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=_cors_headers(_))


async def integrity_error_handler(_: Request, __: IntegrityError) -> JSONResponse:
    # No filtrar nombres de constraints o información de la base de datos.
    return JSONResponse(status_code=409, content={"detail": "No se pudo guardar el registro porque ya existe un valor único."}, headers=_cors_headers(_))
