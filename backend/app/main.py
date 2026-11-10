from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.exceptions import DomainError, domain_error_handler, integrity_error_handler
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.modules.identity import models  # noqa: F401: registra metadata
from app.modules.identity.routes import auth, roles, users
from app.modules.workshops import models as workshop_models  # noqa: F401: registra metadata
from app.modules.workshops.routes import clients, vehicles, workshops
from app.modules.workshops.services.storage import UPLOAD_DIRECTORY, VEHICLE_UPLOAD_DIRECTORY
from app.modules.identity.services.identity_service import seed_initial_admin, seed_roles
from app.modules.identity.services.status_migration import ensure_role_status_schema, seed_statuses
from app.modules.workshops.services.client_migration import ensure_client_user_schema


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)  # Migrar a Alembic en producción.
    ensure_role_status_schema(engine)
    ensure_client_user_schema(engine)
    with SessionLocal() as db:
        seed_statuses(db)
        seed_roles(db)
        seed_initial_admin(db)
    yield


settings = get_settings()
FRONTEND_DIRECTORY = Path("frontend_dist")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
VEHICLE_UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(workshops.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(vehicles.router, prefix="/api/v1")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIRECTORY.parent), name="uploads")

@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}


if FRONTEND_DIRECTORY.is_dir():
    @app.get("/{frontend_path:path}", include_in_schema=False)
    def serve_frontend(frontend_path: str):
        """Entrega la SPA compilada y permite navegación directa por sus rutas."""
        requested_file = (FRONTEND_DIRECTORY / frontend_path).resolve()
        frontend_root = FRONTEND_DIRECTORY.resolve()
        if frontend_path and requested_file.is_relative_to(frontend_root) and requested_file.is_file():
            return FileResponse(requested_file)
        return FileResponse(frontend_root / "index.html")
