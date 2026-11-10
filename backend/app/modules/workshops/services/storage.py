from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import DomainError

UPLOAD_ROOT = Path(get_settings().uploads_root)
UPLOAD_DIRECTORY = UPLOAD_ROOT / "workshops"
VEHICLE_UPLOAD_DIRECTORY = UPLOAD_ROOT / "vehicles"
MAX_PHOTO_BYTES = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


async def save_workshop_photo(photo: UploadFile) -> str:
    """Guarda una sola fotografía validada y devuelve su referencia pública."""
    if photo.content_type not in ALLOWED_CONTENT_TYPES:
        raise DomainError("La fotografía debe ser JPG, PNG o WEBP.", 422)
    content = await photo.read()
    if not content:
        raise DomainError("Selecciona una fotografía del taller.", 422)
    if len(content) > MAX_PHOTO_BYTES:
        raise DomainError("La fotografía no puede superar 5 MB.", 422)
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4()}{ALLOWED_CONTENT_TYPES[photo.content_type]}"
    (UPLOAD_DIRECTORY / filename).write_bytes(content)
    return f"/uploads/workshops/{filename}"


async def save_vehicle_photo(photo: UploadFile) -> str:
    """Guarda una sola fotografía validada del vehículo."""
    if photo.content_type not in ALLOWED_CONTENT_TYPES:
        raise DomainError("La fotografía debe ser JPG, PNG o WEBP.", 422)
    content = await photo.read()
    if not content:
        raise DomainError("Selecciona una fotografía del vehículo.", 422)
    if len(content) > MAX_PHOTO_BYTES:
        raise DomainError("La fotografía no puede superar 5 MB.", 422)
    VEHICLE_UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4()}{ALLOWED_CONTENT_TYPES[photo.content_type]}"
    (VEHICLE_UPLOAD_DIRECTORY / filename).write_bytes(content)
    return f"/uploads/vehicles/{filename}"


def delete_photo(photo_path: str) -> None:
    path = UPLOAD_DIRECTORY / Path(photo_path).name
    if path.exists():
        path.unlink()
