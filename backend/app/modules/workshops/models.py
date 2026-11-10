import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Workshop(Base):
    """Registro del establecimiento creado durante la fase de alta."""
    __tablename__ = "workshops"
    __table_args__ = (UniqueConstraint("rfc", name="uq_workshops_rfc"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    rfc: Mapped[str] = mapped_column(String(13), nullable=False, unique=True, index=True)
    contact_email: Mapped[str] = mapped_column(String(254), nullable=False)
    street_address: Mapped[str] = mapped_column(String(180), nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(120), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(5), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    municipality: Mapped[str] = mapped_column(String(100), nullable=False)
    photo_path: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (UniqueConstraint("first_name", "paternal_last_name", "maternal_last_name", "phone", name="uq_client_identity_phone"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workshop_id: Mapped[str] = mapped_column(ForeignKey("workshops.id"), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(80, collation="NOCASE"), nullable=False)
    paternal_last_name: Mapped[str] = mapped_column(String(80, collation="NOCASE"), nullable=False)
    maternal_last_name: Mapped[str] = mapped_column(String(80, collation="NOCASE"), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    rfc: Mapped[str | None] = mapped_column(String(13), nullable=True, unique=True, index=True)
    street_address: Mapped[str] = mapped_column(String(180), nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(120), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(5), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    municipality: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivated_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workshop_id: Mapped[str] = mapped_column(ForeignKey("workshops.id"), nullable=False, index=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    vin: Mapped[str] = mapped_column(String(17), nullable=False, unique=True, index=True)
    plate: Mapped[str] = mapped_column(String(12), nullable=False)
    brand: Mapped[str] = mapped_column(String(60), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    mileage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    client: Mapped[Client] = relationship(lazy="joined")

    @property
    def client_name(self) -> str:
        """Nombre mostrado del cliente sin alterar la asociación del vehículo."""
        return f"{self.client.first_name} {self.client.paternal_last_name} {self.client.maternal_last_name}".strip()


class ClientAudit(Base):
    __tablename__ = "client_audits"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    actor_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    changes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
