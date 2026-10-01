from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.exceptions import DomainError, domain_error_handler, integrity_error_handler
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.modules.identity import models  # noqa: F401: registra metadata
from app.modules.identity.routes import auth, roles, users
from app.modules.identity.services.identity_service import seed_initial_admin, seed_roles


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)  # Migrar a Alembic en producción.
    with SessionLocal() as db:
        seed_roles(db)
        seed_initial_admin(db)
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")

@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
