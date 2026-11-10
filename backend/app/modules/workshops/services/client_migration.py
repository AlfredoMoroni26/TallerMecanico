from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_client_user_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "workshop_id" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN workshop_id VARCHAR(36) REFERENCES workshops(id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_users_workshop_id ON users(workshop_id)"))
    if "vehicles" in inspector.get_table_names():
        vehicle_columns = {column["name"] for column in inspector.get_columns("vehicles")}
        if "photo_path" not in vehicle_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE vehicles ADD COLUMN photo_path VARCHAR(255)"))
