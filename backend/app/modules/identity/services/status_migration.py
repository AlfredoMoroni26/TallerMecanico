from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.modules.identity.models import Status

ACTIVE_STATUS_ID = 1
SUSPENDED_STATUS_ID = 2


def ensure_role_status_schema(engine: Engine) -> None:
    """Migra SQLite sin perder los roles existentes ni recrear la tabla roles."""
    inspector = inspect(engine)
    if "roles" not in inspector.get_table_names():
        return
    column_names = {column["name"] for column in inspector.get_columns("roles")}
    with engine.begin() as connection:
        if "id_estatus" not in column_names:
            connection.execute(text("ALTER TABLE roles ADD COLUMN id_estatus INTEGER REFERENCES estatus(id_estatus)"))
        if "id_rol" not in column_names:
            connection.execute(text("ALTER TABLE roles ADD COLUMN id_rol INTEGER"))
            connection.execute(text("UPDATE roles SET id_rol = rowid WHERE id_rol IS NULL"))
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_roles_id_rol ON roles(id_rol)"))


def seed_statuses(db: Session) -> None:
    statuses = {status.id_estatus: status for status in db.query(Status).all()}
    if ACTIVE_STATUS_ID not in statuses:
        db.add(Status(id_estatus=ACTIVE_STATUS_ID, nombre_estatus="Activo"))
    if SUSPENDED_STATUS_ID not in statuses:
        db.add(Status(id_estatus=SUSPENDED_STATUS_ID, nombre_estatus="Suspendido"))
    db.commit()
    # Los roles creados antes de esta fase permanecen vigentes y se preservan.
    db.execute(text("UPDATE roles SET id_estatus = :active WHERE id_estatus IS NULL"), {"active": ACTIVE_STATUS_ID})
    db.commit()
